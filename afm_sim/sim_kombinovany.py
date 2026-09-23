"""Kombinovaný STM/AFM sken: jeden kmitající vodivý hrot (qPlus) nad jedním vzorkem.

Reálné qPlus senzory měří tunelový proud a posun frekvence ZÁROVEŇ. Zpětná
vazba ale může regulovat jen jeden z nich; druhý se zaznamenává pasivně
a ukazuje, jak na tentýž povrch reaguje jiný kontrastní mechanismus.
Tři režimy:

- rezim = "I":  smyčka drží konstantní (časově středovaný) proud, Δf se jen
  zaznamenává (STM topografie + AFM kanál),
- rezim = "df": smyčka drží konstantní Δf, proud se jen zaznamenává,
- rezim = "vypnuto": konstantní výška, oba kanály pasivně.

Model (zjednodušení, uvádět u závěrů):
- Střední poloha kmitu d = z_tip - h(x) je společná pro oba kanály.
- Proud je STŘEDOVANÝ přes kmit: pro d(t) = d + A·sin(ωt) je
      ⟨I⟩ = V·c·exp(-2κd) · I0(2κA),
  kde I0 je modifikovaná Besselova funkce - proud teče hlavně v dolním bodě
  obratu. Konstanta c se kalibruje tak, aby ⟨I⟩(d_set) = I_set: oba režimy
  pak mají TÝŽ pracovní bod d_set a dají se porovnat. Pro A -> 0 je I0 = 1
  a model přejde ve stm_sim (hlídá tests/test_kombinovany.py).
- Δf(d) je vzorec 17.15 (afm_sim.frequency_shift), stejně jako v afm_sim.sim.
- Náraz: d <= d_contact (volající typicky r_min + A, jako v AFM).

Smyčka kopíruje pořadí kroků z stm_sim.sim.run_loop a afm_sim.sim.run_loop
(povrch -> vzdálenost -> signál -> šum -> záznam -> náraz -> regulátor ->
akční člen), aby šly limitní případy porovnat s nimi bit po bitu / na
zaokrouhlovací chybu. Tahle smyčka je jediné místo, kde afm_sim sahá na
stm_sim (tunelový proud) - obě knihovny jinak zůstávají nezávislé.
"""

import math
from dataclasses import dataclass, field

import numpy as np

from stm_sim.tip_current import current

from .frequency_shift import frequency_shift

I_MIN = 1e-15   # A, stejná podlaha logaritmu jako v stm_sim.sim


@dataclass
class KombinovanyResult:
    t: list = field(default_factory=list)
    x: list = field(default_factory=list)
    z_tip: list = field(default_factory=list)
    d: list = field(default_factory=list)
    I: list = field(default_factory=list)
    I_meas: list = field(default_factory=list)
    df: list = field(default_factory=list)
    df_meas: list = field(default_factory=list)
    e: list = field(default_factory=list)
    rezim: str = "I"
    crashed: bool = False
    crash_index: int = None


def c_stredovany(V, kappa, A, d_set, I_set):
    """Konstanta c tak, aby proud STŘEDOVANÝ přes kmit dal v d_set právě I_set."""
    return I_set / (V * math.exp(-2.0 * kappa * d_set) * float(np.i0(2.0 * kappa * A)))


def tabulka_df(A, k_cant, f0, force_fn, d_od, d_do, n=6000, n_theta=400):
    """Δf(d) předpočítané na jemné mřížce -> rychlá funkce d -> Δf (lineární interpolace).

    Δf závisí (při pevné síle a A) jen na d, takže není nutné počítat
    integrál 17.15 v každém kroku - v režimu "I" je to jen pasivní kanál
    a smyčka jinak běží ~5x pomaleji (hlavně ve webové verzi). Integrál je
    týž jako ve frequency_shift, jen vektorově přes celou mřížku.
    Za horní mezí mřížky se vrací poslední hodnota (Δf tam je ~0), pod
    dolní mezí taky - tam je ale už náraz.
    """
    d = np.linspace(d_od, d_do, n)
    theta = np.linspace(-np.pi / 2.0, np.pi / 2.0, n_theta)
    r = d[:, None] + A * np.sin(theta)[None, :]
    integrand = force_fn(r) * np.sin(theta)[None, :]
    dth = theta[1] - theta[0]
    integral = dth * (integrand.sum(axis=1) - 0.5 * (integrand[:, 0] + integrand[:, -1]))
    df = -(f0 / (np.pi * k_cant * A)) * integral
    krok = d[1] - d[0]
    d_list, df_list = d.tolist(), df.tolist()
    posledni = n - 1

    def df_fn(dd):
        j = int((dd - d_od) / krok)
        if j < 0:
            return df_list[0]
        if j >= posledni:
            return df_list[-1]
        w = (dd - d_list[j]) / krok
        return df_list[j] + w * (df_list[j + 1] - df_list[j])

    return df_fn


def kombinovany_sken(rezim, surface_fn, v, kappa, V, I_set, d_set, force_fn, A,
                     k_cant, f0, df_set, d_contact, dt, t_end, controller=None,
                     plant=None, z_fixed=None, x0=0.0, t0=0.0, current_noise=None,
                     freq_noise=None, c=None, df_fn=None):
    """Sken jednoho řádku s oběma kanály (proud i Δf).

    Args:
        rezim: "I", "df" nebo "vypnuto" (viz modulový docstring).
        surface_fn: h(x) [m].
        v: rychlost pojezdu [m/s] (záporná = zpětný průjezd).
        kappa, V, I_set: parametry tunelového proudu.
        d_set: pracovní bod [m] - kalibrace c (⟨I⟩(d_set) = I_set).
        force_fn, A, k_cant, f0: parametry AFM kanálu.
        df_set: setpoint Δf [Hz] (v režimu "df" regulovaný, jinak jen reference).
        d_contact: vzdálenost, při které se hlásí náraz [m].
        dt, t_end: časový krok a délka skenu [s].
        controller, plant: regulátor a akční člen (jen pro "I" a "df"); pro
            zpětný průjezd se předávají STEJNÉ instance (viz stm_sim.sim).
        z_fixed: pevná výška hrotu pro "vypnuto" [m].
        x0, t0: počáteční poloha a čas.
        current_noise: šum měřeného proudu [A] se step(dt), nebo None.
        freq_noise: šum měřeného Δf [Hz] se step(dt), nebo None.
        c: konstanta proudu; None = spočítá se z d_set (c_stredovany).
        df_fn: volitelná rychlá náhrada Δf(d) (např. tabulka z tabulka_df);
            None = přesný vzorec 17.15 v každém kroku (jako afm_sim.sim).

    Returns:
        KombinovanyResult.
    """
    if rezim not in ("I", "df", "vypnuto"):
        raise ValueError(f"Neznámý režim {rezim!r} (očekávám I/df/vypnuto)")
    if c is None:
        c = c_stredovany(V, kappa, A, d_set, I_set)
    stred = float(np.i0(2.0 * kappa * A))
    result = KombinovanyResult(rezim=rezim)

    n_steps = int(t_end / dt)
    z_tip = plant.z if rezim != "vypnuto" else z_fixed
    for i in range(n_steps):
        t_local = i * dt
        t = t0 + t_local
        x = x0 + v * t_local
        h = surface_fn(x)
        d = z_tip - h
        I = current(V, c, kappa, d) * stred
        I_meas = I if current_noise is None else I + current_noise.step(dt)
        df = (frequency_shift(d, A, k_cant, f0, force_fn) if df_fn is None
              else df_fn(d))
        df_meas = df if freq_noise is None else df + freq_noise.step(dt)

        if rezim == "I":
            if current_noise is None:
                e = math.log(I / I_set)
            else:
                e = math.log(max(abs(I_meas), I_MIN) / I_set)
        elif rezim == "df":
            e = df_set - df_meas
        else:
            e = 0.0

        result.t.append(t)
        result.x.append(x)
        result.z_tip.append(z_tip)
        result.d.append(d)
        result.I.append(I)
        result.I_meas.append(I_meas)
        result.df.append(df)
        result.df_meas.append(df_meas)
        result.e.append(e)

        if d <= d_contact:
            result.crashed = True
            result.crash_index = i
            break

        if rezim != "vypnuto":
            y = controller.step(e, dt)
            z_tip = plant.step(y, dt)

    return result
