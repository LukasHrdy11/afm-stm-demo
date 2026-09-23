"""Sestavení a spuštění kombinovaného STM/AFM skenu z jednoho slovníku parametrů.

Obdoba vypocet_stm.py / vypocet_afm.py (viz tam pro rozdělení výpočet/widgety
a pravidlo přenositelnosti). Parametry proudu (kappa, V, I_set) jsou ze
STM presetu "reálný přístroj", parametry cantileveru a síly ze AFM presetu
"typický qPlus" - jeden vodivý qPlus hrot, který měří obojí.

Pracovní bod d_set je společný: v režimu "I" se kalibruje proud tak, aby
⟨I⟩(d_set) = I_set, v režimu "df" je Δf_set = Δf(d_set). Oba režimy tak
startují ve stejné výšce nad stejným povrchem a liší se jen tím, KTERÝ signál
smyčka drží.
"""

import numpy as np

from afm_sim import measured as afm_measured
from afm_sim import noise as afm_noise
from afm_sim.frequency_shift import frequency_shift, gain_from_tau as gain_afm, kappa_eff
from afm_sim.sim_kombinovany import c_stredovany, kombinovany_sken, tabulka_df
from afm_sim.tip_force import lj_force, r_min
from stm_sim import measured as stm_measured
from stm_sim import noise as stm_noise
from stm_sim.controller import (
    IntegralController, PIController, ProportionalController,
    gain_from_tau as gain_stm,
)
from stm_sim.plant import FirstOrderPlant
from stm_sim.surface import atoms_surface, ramp_surface, step_surface

from .vypocet_afm import PracovniBodError, d_minima_frequency_shift

VYCHOZI = dict(
    # tunelový proud (STM, změřené kappa)
    kappa=stm_measured.KAPPA, V=stm_measured.V_BIAS, I_set=stm_measured.I_SET,
    # cantilever a síla (AFM, typický qPlus - nekalibrováno)
    k_cant=afm_measured.K_CANT, f0=afm_measured.F0, A=afm_measured.A_OSC,
    U0=afm_measured.U0, Ra=afm_measured.RA,
    # smyčka
    rezim="I",               # "I" | "df" | "vypnuto"
    controller="PI",
    # 0,8 nm: Δf je tu ~ -1 Hz, tedy nad šumem (u 1,0 nm z AFM presetu jen
    # ~ -0,1 Hz, srovnatelné se šumem 0,08 Hz) a pořád za minimem Δf(d).
    d_set=0.8e-9,
    tau_I=stm_measured.TAU, K_P_I=stm_measured.K_P,
    tau_df=afm_measured.TAU, K_P_df=afm_measured.K_P,
    T_SYS=stm_measured.T_SYS, v=stm_measured.V_SCAN,
    backward=True,
    # šum (násobek změřeného)
    sum_proudu=True, sum_frekvence=True, mera_sumu=1.0, seed=42,
    # povrch
    surface="atoms", x_edge=3e-9, H=0.1e-9, w=0.3e-9,
    atoms_start=3e-9, atoms_H=0.1e-9, atoms_spacing=0.6e-9, atoms_sigma=0.10e-9,
    atoms_pocet=6,
)


def sestav_povrch(p):
    if p["surface"] == "step":
        return lambda x: step_surface(x, p["x_edge"], p["H"])
    if p["surface"] == "ramp":
        return lambda x: ramp_surface(x, p["x_edge"], p["H"], p["w"])
    if p["surface"] == "atoms":
        return lambda x: atoms_surface(x, p["atoms_start"], p["atoms_H"],
                                       p["atoms_spacing"], p["atoms_sigma"])
    raise ValueError(f"Neznámý surface: {p['surface']!r} (očekávám step/ramp/atoms)")


def sestav_regulator(p, force_fn, d_contact):
    """Regulátor pro zvolený režim; zesílení podle signálu, který se reguluje."""
    if p["rezim"] == "I":
        K_I, K_P = gain_stm(p["kappa"], p["tau_I"]), p["K_P_I"]
    else:
        d_min = d_minima_frequency_shift(p, force_fn, d_contact)
        if not p["d_set"] > d_min:
            raise PracovniBodError(p["d_set"], d_min)
        k_eff = kappa_eff(p["d_set"], p["A"], p["k_cant"], p["f0"], force_fn)
        K_I, K_P = gain_afm(k_eff, p["tau_df"]), p["K_P_df"]
    if p["controller"] == "P":
        return ProportionalController(base=p["d_set"], K_P=K_P)
    if p["controller"] == "I":
        return IntegralController(y0=p["d_set"], K_I=K_I)
    if p["controller"] == "PI":
        return PIController(y0=p["d_set"], K_I=K_I, K_P=K_P)
    raise ValueError(f"Neznámý controller: {p['controller']!r}")


def sestav_sum(p):
    """Šum proudu a Δf ze dvou SAMOSTATNÝCH generátorů (zapnutí jednoho nemění druhý)."""
    mira = p["mera_sumu"]
    cn = fn = None
    if p["sum_proudu"] and mira > 0:
        cn = stm_noise.LowpassWhiteNoise(np.random.default_rng(p["seed"]),
                                         stm_noise.SIGMA_PROUD * mira, stm_noise.F_PRE)
    if p["sum_frekvence"] and mira > 0:
        fn = afm_noise.sum_frekvence(np.random.default_rng([p["seed"], 2]),
                                     sigma=afm_noise.SIGMA_DF * mira)
    return cn, fn


def delka_skenu(p):
    if p["surface"] == "atoms":
        konec = p["atoms_start"] + (p["atoms_pocet"] + 0.5) * p["atoms_spacing"]
    else:
        konec = p["x_edge"] + 2e-9
    tau = p["tau_I"] if p["rezim"] == "I" else p["tau_df"]
    return 20 * tau + konec / p["v"], tau / 100


def spust(parametry=None, **zmeny):
    """Spustí kombinovaný sken; vrací slovník jako vypocet_afm.spust().

    Raises:
        PracovniBodError: v režimu "df", když d_set leží před minimem Δf(d).
    """
    p = dict(VYCHOZI if parametry is None else parametry)
    p.update(zmeny)
    force_fn = lambda r: lj_force(r, p["U0"], p["Ra"])
    d_contact = r_min(p["Ra"]) + p["A"]
    surface_fn = sestav_povrch(p)
    t_end, dt = delka_skenu(p)
    df_set = frequency_shift(p["d_set"], p["A"], p["k_cant"], p["f0"], force_fn)
    c = c_stredovany(p["V"], p["kappa"], p["A"], p["d_set"], p["I_set"])
    current_noise, freq_noise = sestav_sum(p)
    # Δf z tabulky (rychlé, chyba interpolace << šum Δf); přesná cesta se
    # testuje v tests/test_kombinovany.py.
    df_fn = tabulka_df(p["A"], p["k_cant"], p["f0"], force_fn, 0.98 * d_contact,
                       p["d_set"] + 3e-9)

    spolecne = dict(
        rezim=p["rezim"], surface_fn=surface_fn, kappa=p["kappa"], V=p["V"],
        I_set=p["I_set"], d_set=p["d_set"], force_fn=force_fn, A=p["A"],
        k_cant=p["k_cant"], f0=p["f0"], df_set=df_set, d_contact=d_contact,
        dt=dt, t_end=t_end, current_noise=current_noise, freq_noise=freq_noise, c=c,
        df_fn=df_fn,
    )
    vystup = {"parametry": p, "surface_fn": surface_fn, "df_set": df_set,
              "d_contact": d_contact, "d_set": p["d_set"], "I_set": p["I_set"],
              "force_fn": force_fn, "df_fn": df_fn, "t_end": t_end, "dt": dt,
              "bwd": None}

    if p["rezim"] == "vypnuto":
        z_fixed = p.get("z_fixed") or p["d_set"]
        vystup["fwd"] = kombinovany_sken(v=p["v"], z_fixed=z_fixed, **spolecne)
        return vystup

    controller = sestav_regulator(p, force_fn, d_contact)
    plant = FirstOrderPlant(z0=p["d_set"], T_sys=p["T_SYS"])
    fwd = kombinovany_sken(v=p["v"], controller=controller, plant=plant, **spolecne)
    vystup["fwd"] = fwd
    if p["backward"] and not fwd.crashed:
        vystup["bwd"] = kombinovany_sken(v=-p["v"], controller=controller, plant=plant,
                                         x0=fwd.x[-1], t0=fwd.t[-1] + dt, **spolecne)
    return vystup
