"""Δf přímo z pohybové rovnice cantileveru - nezávislá kontrola vzorce 17.15.

Ve FM módu (self-excitation) kmitá cantilever na své VLASTNÍ frekvenci a PLL
ji jen měří. Tady se ta vlastní frekvence spočítá "hrubou silou": integruje
se volný, netlumený kmit hrotu v poli síly hrot-vzorek

    m·z'' = -k·z + F(d + z),     m = k/ω0²,

s počátkem v horním bodě obratu (z = +A, v = 0), a frekvence se odečte
z průchodů nulou. Δf = f(se silou) - f(bez síly): odečtení běhu bez síly
vyruší systematickou chybu integrace (RK4 i interpolace průchodů), takže
zbyde jen vliv síly.

Proti afm_sim.frequency_shift.frequency_shift() (harmonic balance, vážený
průměr síly přes kmit) nepředpokládá nic o tvaru pohybu - proto je to
nezávislá cesta ke stejné veličině. Shodují se do prvního řádu v F/(k·A),
což je u qPlus (k = 1800 N/m) s velkou rezervou.

Tlumení a buzení se vynechávají: ve FM módu je regulátor amplitudy
kompenzuje, na frekvenci (v prvním řádu) nemají vliv. Proti
afm_sim.phase_shift.phase_shift_numeric (buzený tlumený oscilátor, ustálení
~Q period) je tohle o řády rychlejší - stačí ~10 period - a hodí se proto
do interaktivního panelu.
"""

import numpy as np


def _vektorova(force_fn):
    """Síla použitelná na pole vzdáleností (skalární funkce se obalí)."""
    try:
        zkouska = force_fn(np.array([1e-9, 2e-9]))
        if np.shape(zkouska) == (2,):
            return force_fn
    except Exception:   # noqa: BLE001 - skalární funkce na poli spadne různě
        pass
    return np.vectorize(force_fn, otypes=[float])


def integruj_kmit(d, A, k_cant, f0, force_fn, n_period=10, kroku_na_periodu=400):
    """Volný netlumený kmit hrotu v poli síly (RK4), pro jedno nebo víc d.

    Args:
        d: střední vzdálenost hrot-vzorek [m] (skalár nebo 1D pole).
        A: amplituda (počáteční výchylka v horním bodě obratu) [m].
        k_cant, f0: tuhost [N/m] a volná rezonanční frekvence [Hz].
        force_fn: F(r) [N]; None = bez síly (volný cantilever).
        n_period: kolik period se integruje.
        kroku_na_periodu: krok RK4 jako zlomek periody 1/f0.

    Returns:
        (t, z) - t tvaru (N,), z tvaru (N, len(d)) [m]; z je výchylka od d,
        kladná směrem OD vzorku (stejná konvence jako d + z ve frequency_shift).
    """
    d = np.atleast_1d(np.asarray(d, dtype=float))
    omega0 = 2.0 * np.pi * f0
    m = k_cant / omega0 ** 2
    F = _vektorova(force_fn) if force_fn is not None else None
    dt = 1.0 / (f0 * kroku_na_periodu)
    n = int(n_period * kroku_na_periodu) + 1

    def zrychleni(z):
        a = -omega0 ** 2 * z
        if F is not None:
            a = a + F(d + z) / m
        return a

    z = np.full(d.shape, float(A))
    v = np.zeros(d.shape)
    t = np.arange(n) * dt
    z_arr = np.empty((n, d.size))
    z_arr[0] = z
    for i in range(1, n):
        k1z, k1v = v, zrychleni(z)
        k2z, k2v = v + 0.5 * dt * k1v, zrychleni(z + 0.5 * dt * k1z)
        k3z, k3v = v + 0.5 * dt * k2v, zrychleni(z + 0.5 * dt * k2z)
        k4z, k4v = v + dt * k3v, zrychleni(z + dt * k3z)
        z = z + dt / 6.0 * (k1z + 2.0 * k2z + 2.0 * k3z + k4z)
        v = v + dt / 6.0 * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)
        z_arr[i] = z
    return t, z_arr


def frekvence_z_pruchodu(t, z):
    """Frekvence kmitu z průchodů nulou (lineární interpolace), po sloupcích z.

    Bere se první a poslední průchod SHORA DOLŮ a počet period mezi nimi -
    průměr přes celé okno, ne jedna perioda.
    """
    f = np.empty(z.shape[1])
    for j in range(z.shape[1]):
        s = z[:, j]
        idx = np.nonzero((s[:-1] > 0) & (s[1:] <= 0))[0]
        if len(idx) < 2:
            f[j] = np.nan
            continue
        casy = t[idx] + (t[idx + 1] - t[idx]) * s[idx] / (s[idx] - s[idx + 1])
        f[j] = (len(casy) - 1) / (casy[-1] - casy[0])
    return f


def df_z_pohybove_rovnice(d, A, k_cant, f0, force_fn, n_period=10,
                          kroku_na_periodu=400):
    """Δf [Hz] z pohybové rovnice: f(se silou) - f(bez síly), pro skalár i pole d."""
    t, z = integruj_kmit(d, A, k_cant, f0, force_fn, n_period, kroku_na_periodu)
    t0, z0 = integruj_kmit(np.atleast_1d(d)[:1], A, k_cant, f0, None, n_period,
                           kroku_na_periodu)
    df = frekvence_z_pruchodu(t, z) - frekvence_z_pruchodu(t0, z0)[0]
    return float(df[0]) if np.ndim(d) == 0 else df
