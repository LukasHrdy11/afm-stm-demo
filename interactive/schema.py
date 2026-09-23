"""Vlastní bloková schémata zpětnovazebních smyček STM a FM-AFM (matplotlib).

Schémata jsou nakreslená znovu, ne převzatá z literatury (veřejné repo smí
kapitoly jen citovat): inspirace Voigtländer, Scanning Probe Microscopy,
kap. 5.7-5.9 (regulátor STM) a 17.2.2 (FM detekce, PLL).

U STM umí schéma vepsat do bloků hodnoty jednoho kroku simulace (z krokování
v panelu) - text "proud -> chyba -> příkaz -> hrot" se tím stane obrázkem.

Modul závisí jen na matplotlib (ne na ipywidgets), takže jde použít i ze
skriptu, např. pro obrázek do prezentace.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

_TEXTY = {
    "cs": {
        "stm_t": "Zpětnovazební smyčka STM (režim konstantního proudu)",
        "b_tunel": "Tunelový přechod\nI = V·c·exp(−2κg)",
        "b_pre": "Předzesilovač\nI_meas = I + šum",
        "b_log": "Logaritmus a porovnání\ne = ln(I_meas / I_set)",
        "b_reg": "Regulátor {reg}\n{vzorec}",
        "b_piezo": "Akční člen (piezo)\nT_sys·dz/dt = y − z",
        "b_mezera": "Mezera\ng = z_hrot − h(x)",
        "v_Iset": "setpoint I_set", "v_sum": "šum proudu", "v_povrch": "povrch h(x)\n(+ šum mezery)",
        "afm_t": "Zpětnovazební smyčka FM-AFM (qPlus, self-excitation)",
        "a_cant": "Cantilever + hrot\nsíla F(d) posune rezonanci",
        "a_pll": "PLL (fázový závěs)\nměří f = f0 + Δf",
        "a_por": "Porovnání\ne = Δf_set − Δf",
        "a_reg": "Regulátor {reg}\n{vzorec}",
        "a_piezo": "Akční člen (piezo)\nT_sys·dz/dt = y − z",
        "a_d": "Vzdálenost\nd = z_hrot − h(x)",
        "a_amp": "Regulátor amplitudy + budič\n(drží A, budí ve fázi)",
        "v_dfset": "setpoint Δf_set", "v_sumdf": "šum Δf",
        "zdroj": "Vlastní schéma podle: B. Voigtländer, Scanning Probe Microscopy, {kap}.",
        "kap_stm": "kap. 5.7–5.9", "kap_afm": "kap. 17.2.2",
        "prikaz": "příkaz y (ne poloha!)",
    },
    "en": {
        "stm_t": "STM feedback loop (constant-current mode)",
        "b_tunel": "Tunnel junction\nI = V·c·exp(−2κg)",
        "b_pre": "Preamplifier\nI_meas = I + noise",
        "b_log": "Logarithm and comparison\ne = ln(I_meas / I_set)",
        "b_reg": "Controller {reg}\n{vzorec}",
        "b_piezo": "Actuator (piezo)\nT_sys·dz/dt = y − z",
        "b_mezera": "Gap\ng = z_tip − h(x)",
        "v_Iset": "setpoint I_set", "v_sum": "current noise", "v_povrch": "surface h(x)\n(+ gap noise)",
        "afm_t": "FM-AFM feedback loop (qPlus, self-excitation)",
        "a_cant": "Cantilever + tip\nforce F(d) shifts the resonance",
        "a_pll": "PLL (phase-locked loop)\nmeasures f = f0 + Δf",
        "a_por": "Comparison\ne = Δf_set − Δf",
        "a_reg": "Controller {reg}\n{vzorec}",
        "a_piezo": "Actuator (piezo)\nT_sys·dz/dt = y − z",
        "a_d": "Distance\nd = z_tip − h(x)",
        "a_amp": "Amplitude controller + drive\n(keeps A, drives in phase)",
        "v_dfset": "setpoint Δf_set", "v_sumdf": "Δf noise",
        "zdroj": "Own diagram after: B. Voigtländer, Scanning Probe Microscopy, {kap}.",
        "kap_stm": "ch. 5.7–5.9", "kap_afm": "ch. 17.2.2",
        "prikaz": "command y (not a position!)",
    },
}

_VZORCE = {"P": "y = y0 + K_P·e", "I": "y = ∫ K_I·e dt",
           "PI": "y = K_P·e + ∫ K_I·e dt"}

# Rozmístění šesti bloků smyčky (střed x, y) - horní řada zleva doprava,
# spodní zprava doleva, šipky jdou dokola.
_POZICE = [(1.7, 3.6), (5.0, 3.6), (8.3, 3.6), (8.3, 1.2), (5.0, 1.2), (1.7, 1.2)]
_SIRKA, _VYSKA = 2.9, 1.25


def _blok(ax, x, y, text, hodnota=None, barva="#e8f0fa"):
    ax.add_patch(FancyBboxPatch((x - _SIRKA / 2, y - _VYSKA / 2), _SIRKA, _VYSKA,
                                boxstyle="round,pad=0.05", facecolor=barva,
                                edgecolor="#335", linewidth=1.2))
    if hodnota:
        ax.text(x, y + 0.18, text, ha="center", va="center", fontsize=8.5)
        ax.text(x, y - 0.42, hodnota, ha="center", va="center", fontsize=9,
                color="#b04000", fontweight="bold")
    else:
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5)


def _sipka(ax, a, b, text=None, posun=(0.0, 0.18)):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14,
                                 color="#335", linewidth=1.4))
    if text:
        ax.text((a[0] + b[0]) / 2 + posun[0], (a[1] + b[1]) / 2 + posun[1], text,
                ha="center", va="bottom", fontsize=7.5, color="#555")


def _smycka(ax, texty, hodnoty):
    """Šest bloků do kruhu + šipky mezi nimi."""
    for (x, y), text, hod in zip(_POZICE, texty, hodnoty):
        _blok(ax, x, y, text, hod)
    h, v = _SIRKA / 2, _VYSKA / 2
    (x0, y0), (x1, _), (x2, _), (x3, y3), (x4, _), (x5, _) = _POZICE
    _sipka(ax, (x0 + h, y0), (x1 - h, y0))
    _sipka(ax, (x1 + h, y0), (x2 - h, y0))
    _sipka(ax, (x2, y0 - v), (x3, y3 + v))
    _sipka(ax, (x3 - h, y3), (x4 + h, y3))
    _sipka(ax, (x4 - h, y3), (x5 + h, y3))
    _sipka(ax, (x5, y3 + v), (x0, y0 - v))


def _vstup(ax, kam, text, shora=True):
    x, y = kam
    y_hrana = y + _VYSKA / 2 if shora else y - _VYSKA / 2
    y_start = y_hrana + 0.55 if shora else y_hrana - 0.55
    _sipka(ax, (x, y_start), (x, y_hrana))
    ax.text(x, y_start + (0.05 if shora else -0.05), text, ha="center",
            va="bottom" if shora else "top", fontsize=7.5, color="#555")


def _platno(titulek):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.2, 5.4)
    ax.axis("off")
    ax.set_title(titulek, fontsize=11)
    return fig, ax


def fig_schema_stm(controller="PI", stav=None, jazyk="cs"):
    """Blokové schéma STM smyčky; se `stav` (krok z krokování) i s hodnotami.

    Args:
        controller: "P", "I" nebo "PI" (vzorec v bloku regulátoru).
        stav: slovník jednoho kroku z run_loop callbacku (klíče I, I_meas, e,
            y, z_tip_novy, g, h), nebo None = schéma bez hodnot.
        jazyk: "cs" nebo "en".

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _TEXTY[jazyk]
    fig, ax = _platno(P["stm_t"])
    texty = [P["b_tunel"], P["b_pre"], P["b_log"],
             P["b_reg"].format(reg=controller, vzorec=_VZORCE[controller]),
             P["b_piezo"], P["b_mezera"]]
    hodnoty = [None] * 6
    if stav is not None:
        hodnoty = [f"I = {stav['I'] * 1e12:.1f} pA",
                   f"I_meas = {stav['I_meas'] * 1e12:.1f} pA",
                   f"e = {stav['e']:+.4f}",
                   None if stav["y"] is None else f"y = {stav['y'] * 1e9:.4f} nm",
                   None if stav["y"] is None else f"z = {stav['z_tip_novy'] * 1e9:.4f} nm",
                   f"g = {stav['g'] * 1e9:.4f} nm  (h = {stav['h'] * 1e9:.3f} nm)"]
    _smycka(ax, texty, hodnoty)
    _vstup(ax, _POZICE[2], P["v_Iset"])
    _vstup(ax, _POZICE[1], P["v_sum"])
    _vstup(ax, _POZICE[5], P["v_povrch"], shora=False)
    ax.text(6.65, 1.2 + _VYSKA / 2 + 0.05, P["prikaz"], ha="center", va="bottom",
            fontsize=7.5, color="#555")
    ax.text(5.0, -0.15, P["zdroj"].format(kap=P["kap_stm"]), ha="center",
            fontsize=7, color="#777", style="italic")
    fig.tight_layout()
    return fig


def fig_schema_afm(controller="PI", jazyk="cs"):
    """Blokové schéma FM-AFM smyčky (vzdálenostní smyčka + smyčka amplitudy)."""
    P = _TEXTY[jazyk]
    fig, ax = _platno(P["afm_t"])
    texty = [P["a_cant"], P["a_pll"], P["a_por"],
             P["a_reg"].format(reg=controller, vzorec=_VZORCE[controller]),
             P["a_piezo"], P["a_d"]]
    _smycka(ax, texty, [None] * 6)
    # Vnitřní smyčka: PLL + regulátor amplitudy budí cantilever ve fázi.
    xa, ya = 3.35, 5.0
    ax.add_patch(FancyBboxPatch((xa - 1.45, ya - 0.33), 2.9, 0.66,
                                boxstyle="round,pad=0.04", facecolor="#f4efe6",
                                edgecolor="#853", linewidth=1.0))
    ax.text(xa, ya, P["a_amp"], ha="center", va="center", fontsize=7.5)
    _sipka(ax, (_POZICE[1][0] - 0.4, _POZICE[1][1] + _VYSKA / 2), (xa + 0.9, ya - 0.33))
    _sipka(ax, (xa - 0.9, ya - 0.33), (_POZICE[0][0] + 0.4, _POZICE[0][1] + _VYSKA / 2))
    _vstup(ax, _POZICE[2], P["v_dfset"])
    _vstup(ax, _POZICE[5], P["v_povrch"].split("\n")[0], shora=False)
    ax.text(6.65, 1.2 + _VYSKA / 2 + 0.05, P["prikaz"], ha="center", va="bottom",
            fontsize=7.5, color="#555")
    ax.text(5.0, -0.15, P["zdroj"].format(kap=P["kap_afm"]), ha="center",
            fontsize=7, color="#777", style="italic")
    fig.tight_layout()
    return fig
