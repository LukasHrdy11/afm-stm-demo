"""Vykreslení výsledků STM simulace - sdílené mezi CLI skriptem a UI.

Proč to nesedí v run_simulation.py: tentýž graf potřebuje jak dávkový
spouštěč (uloží PNG do export/), tak interaktivní panel (kreslí inline do
widgetu). Aby se kreslení nemuselo psát dvakrát, žije tady.

PRAVIDLO: tenhle modul NEZNÁ žádnou cestu. Nesmí v něm být savefig ani
odkaz na export/ - dostane data, vrátí Figure a co se s ní stane, řeší
volající. Jen tak jde kreslení použít i tam, kde se na disk nic neukládá.

Vrácenou figuru je volající povinen po použití zavřít (plt.close), jinak
se při opakovaném překreslování v UI hromadí v paměti.
"""

import math

import matplotlib.pyplot as plt
import numpy as np

from .tip_current import c_from_setpoint, current

# Popisky grafů ve dvou jazycích. Výchozí "cs" dává přesně původní grafy
# (dávkové skripty jazyk nezadávají). Překlad UI je v interactive/texty.py,
# sem patří jen texty uvnitř obrázků - tenhle modul nesmí záviset na interactive/.
_POPISKY = {
    "cs": {
        "fwd": "forward", "bwd": "backward", "ztip_fwd": "z_tip (forward)",
        "ztip_bwd": "z_tip (backward)", "h": "h (povrch)", "vyska": "výška [nm]",
        "t_vyska": "Výška hrotu a povrchu", "t_mezera": "Mezera hrot-vzorek",
        "t_chyba": "Log-chyba regulátoru", "ref": "referenční běh",
        "ztip_ch": "z_tip (konstantní výška)", "ztip_smycka": "z_tip (se zpětnou vazbou)",
        "t_ch": "Hrot stojí, povrch se mění", "I_ch": "I (bez zpětné vazby)",
        "I_smycka": "I (se zpětnou vazbou)", "t_I_ch": "Proud kopíruje topografii (log. osa)",
        "g_ch": "konstantní výška", "g_smycka": "se zpětnou vazbou",
        "Iz_t_lin": "Tunelový proud vs. mezera (lineární osa)",
        "Iz_t_log": "Totéž v log. ose: přímka se sklonem -2κ",
        "Iz_mer": "κ = {k:.1f} /nm (změřeno)", "Iz_lit": "κ = {k:.1f} /nm (literatura)",
        "Iz_pracovni": "pracovní bod (g_set, I_set)", "Iz_sken": "mezera během skenu",
        "Iz_krok": "hrot v zobrazeném kroku", "Iz_dekada": "10× menší proud na každých {d:.0f} pm",
        "g_osa": "mezera g [nm]",
    },
    "en": {
        "fwd": "forward", "bwd": "backward", "ztip_fwd": "z_tip (forward)",
        "ztip_bwd": "z_tip (backward)", "h": "h (surface)", "vyska": "height [nm]",
        "t_vyska": "Tip and surface height", "t_mezera": "Tip-sample gap",
        "t_chyba": "Controller log error", "ref": "reference run",
        "ztip_ch": "z_tip (constant height)", "ztip_smycka": "z_tip (with feedback)",
        "t_ch": "Tip fixed, surface changes", "I_ch": "I (feedback off)",
        "I_smycka": "I (with feedback)", "t_I_ch": "Current follows the topography (log axis)",
        "g_ch": "constant height", "g_smycka": "with feedback",
        "Iz_t_lin": "Tunnelling current vs. gap (linear axis)",
        "Iz_t_log": "Same on a log axis: a line with slope -2κ",
        "Iz_mer": "κ = {k:.1f} /nm (measured)", "Iz_lit": "κ = {k:.1f} /nm (literature)",
        "Iz_pracovni": "working point (g_set, I_set)", "Iz_sken": "gap during the scan",
        "Iz_krok": "tip in the displayed step", "Iz_dekada": "10× less current every {d:.0f} pm",
        "g_osa": "gap g [nm]",
    },
}


def _nm(hodnoty):
    """Převod pole metrů na nanometry (kvůli čitelnosti os)."""
    return [h * 1e9 for h in hodnoty]


def fig_prubehy(result_fwd, surface_fn, g_contact, result_bwd=None,
                titulek="", overlay=None, overlay_popis=None, jazyk="cs"):
    """Postaví třípanelový graf: výška hrotu, mezera, log-chyba.

    Args:
        result_fwd: SimulationResult forward průjezdu.
        surface_fn: funkce h(x) -> výška povrchu [m] (kreslí se jako
            referenční profil pod dráhu hrotu).
        g_contact: mezera, při které se hlásí náraz [m] (vodorovná čára).
        result_bwd: SimulationResult backward průjezdu, nebo None.
        titulek: dodatek do titulku horního panelu (např. "PI, atoms").
        overlay: starší SimulationResult vykreslený poloprůhledně na
            pozadí, nebo None. Slouží k porovnání dvou běhů v jednom
            grafu (P vs. I vs. PI, šum zapnutý vs. vypnutý, smyčka vs.
            konstantní výška) bez přepínání mezi obrázky.
        overlay_popis: popisek zamknuté křivky v legendě (None = výchozí).
        jazyk: "cs" nebo "en" - jazyk popisků v obrázku.

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    if overlay_popis is None:
        overlay_popis = P["ref"]
    fig, axes = plt.subplots(3, 1, figsize=(7, 8))

    if overlay is not None:
        _vykresli_overlay(axes, overlay, overlay_popis)

    axes[0].plot(_nm(result_fwd.x), _nm(result_fwd.z_tip), label=P["ztip_fwd"])
    if result_bwd is not None:
        axes[0].plot(_nm(result_bwd.x), _nm(result_bwd.z_tip),
                     label=P["ztip_bwd"])
    h_curve = [surface_fn(x) for x in result_fwd.x]
    axes[0].plot(_nm(result_fwd.x), _nm(h_curve), "--", label=P["h"])
    axes[0].set_xlabel("x [nm]")
    axes[0].set_ylabel(P["vyska"])
    axes[0].set_title(f"{P['t_vyska']} ({titulek})" if titulek
                      else P["t_vyska"])
    axes[0].legend()

    axes[1].plot(_nm(result_fwd.x), _nm(result_fwd.g), label=P["fwd"])
    if result_bwd is not None:
        axes[1].plot(_nm(result_bwd.x), _nm(result_bwd.g), label=P["bwd"])
    axes[1].axhline(g_contact * 1e9, color="red", linestyle=":", label="g_contact")
    axes[1].set_xlabel("x [nm]")
    axes[1].set_ylabel("g [nm]")
    axes[1].set_title(P["t_mezera"])
    axes[1].legend()

    axes[2].plot(_nm(result_fwd.x), result_fwd.e, label=P["fwd"])
    if result_bwd is not None:
        axes[2].plot(_nm(result_bwd.x), result_bwd.e, label=P["bwd"])
    axes[2].set_xlabel("x [nm]")
    axes[2].set_ylabel("e [-]")
    axes[2].set_title(P["t_chyba"])
    if result_bwd is not None:
        axes[2].legend()

    fig.tight_layout()
    return fig


def _vykresli_overlay(axes, overlay, popis):
    """Zamknutá referenční křivka na pozadí (šedá, poloprůhledná)."""
    styl = {"color": "gray", "alpha": 0.5, "linestyle": "--", "linewidth": 1.0}
    axes[0].plot(_nm(overlay.x), _nm(overlay.z_tip), label=popis, **styl)
    axes[1].plot(_nm(overlay.x), _nm(overlay.g), label=popis, **styl)
    # Sken v konstantní výšce log-chybu nepočítá (není co regulovat).
    if getattr(overlay, "e", None):
        axes[2].plot(_nm(overlay.x), overlay.e, label=popis, **styl)


def fig_konstantni_vyska(result, surface_fn, I_set, g_contact, titulek="",
                         result_smycka=None, jazyk="cs"):
    """Graf skenu s VYPNUTOU zpětnou vazbou (režim konstantní výšky).

    Ukazuje to, co se u zapnuté smyčky nevidí: topografie se promítne
    rovnou do proudu, místo aby ji regulátor vykompenzoval pohybem hrotu.
    Proud je v logaritmické ose, protože přes hranu roste exponenciálně.

    Args:
        result: ConstantHeightResult z constant_height_scan().
        surface_fn: funkce h(x) -> výška povrchu [m].
        I_set: proud, na který je hrot kalibrovaný [A] (referenční čára).
        g_contact: mezera, při které se hlásí náraz [m].
        titulek: dodatek do titulku horního panelu.
        result_smycka: volitelný SimulationResult TÉHOŽ povrchu se zapnutou
            smyčkou, vykreslený pro přímé srovnání obou režimů.
        jazyk: "cs" nebo "en" - jazyk popisků v obrázku.

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    fig, axes = plt.subplots(3, 1, figsize=(7, 8))

    axes[0].plot(_nm(result.x), _nm(result.z_tip),
                 label=P["ztip_ch"])
    if result_smycka is not None:
        axes[0].plot(_nm(result_smycka.x), _nm(result_smycka.z_tip),
                     label=P["ztip_smycka"])
    h_curve = [surface_fn(x) for x in result.x]
    axes[0].plot(_nm(result.x), _nm(h_curve), "--", label=P["h"])
    axes[0].set_xlabel("x [nm]")
    axes[0].set_ylabel(P["vyska"])
    axes[0].set_title(f"{P['t_ch']} ({titulek})" if titulek
                      else P["t_ch"])
    axes[0].legend()

    axes[1].semilogy(_nm(result.x), [I * 1e12 for I in result.I_meas],
                     label=P["I_ch"])
    if result_smycka is not None:
        axes[1].semilogy(_nm(result_smycka.x),
                         [I * 1e12 for I in result_smycka.I_meas],
                         label=P["I_smycka"])
    axes[1].axhline(I_set * 1e12, color="red", linestyle=":", label="I_set")
    axes[1].set_xlabel("x [nm]")
    axes[1].set_ylabel("I [pA]")
    axes[1].set_title(P["t_I_ch"])
    axes[1].legend()

    axes[2].plot(_nm(result.x), _nm(result.g), label=P["g_ch"])
    if result_smycka is not None:
        axes[2].plot(_nm(result_smycka.x), _nm(result_smycka.g),
                     label=P["g_smycka"])
    axes[2].axhline(g_contact * 1e9, color="red", linestyle=":", label="g_contact")
    axes[2].set_xlabel("x [nm]")
    axes[2].set_ylabel("g [nm]")
    axes[2].set_title(P["t_mezera"])
    axes[2].legend()

    fig.tight_layout()
    return fig


def fig_proud_vs_z(kappa, V, I_set, g_set, g_contact, g_skenu=None, g_bod=None,
                   kappa_ref=None, zdroj_kappa="zmereno", jazyk="cs"):
    """Závislost tunelového proudu na mezeře I(g) s vyznačeným pracovním bodem.

    Ukazuje, proč STM vůbec funguje: proud klesá exponenciálně, řádově 10×
    na každé ~0,1-0,2 nm. V log. ose je to přímka se sklonem -2κ.

    Args:
        kappa, V, I_set, g_set: parametry modelu (konstanta c se dopočte tak,
            aby I(g_set) = I_set, stejně jako v simulaci).
        g_contact: mezera, při které se hlásí náraz [m].
        g_skenu: (g_min, g_max) mezery během skenu [m], nebo None.
        g_bod: mezera v právě zobrazeném kroku krokování [m], nebo None.
        kappa_ref: druhá kappa pro srovnání (např. literaturová), nebo None.
            Křivka jde týmž pracovním bodem - liší se jen sklonem.
        zdroj_kappa: "zmereno" nebo "literatura" - popisek hlavní křivky.
        jazyk: "cs" nebo "en".

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    g_od = max(0.5 * g_contact, 0.05e-9)
    g = np.linspace(g_od, g_set + 0.6e-9, 400)

    def krivka(k):
        c = c_from_setpoint(V, k, g_set, I_set)
        return np.array([current(V, c, k, gi) for gi in g])

    I = krivka(kappa)
    popis = (P["Iz_mer"] if zdroj_kappa == "zmereno" else P["Iz_lit"]).format(k=kappa * 1e-9)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, log in ((axes[0], False), (axes[1], True)):
        if g_skenu is not None:
            ax.axvspan(g_skenu[0] * 1e9, g_skenu[1] * 1e9, color="tab:orange",
                       alpha=0.25, label=P["Iz_sken"])
        ax.plot(g * 1e9, I * 1e12, label=popis)
        if kappa_ref is not None:
            ax.plot(g * 1e9, krivka(kappa_ref) * 1e12, "--", color="gray",
                    label=P["Iz_lit"].format(k=kappa_ref * 1e-9))
        ax.plot([g_set * 1e9], [I_set * 1e12], "ko", label=P["Iz_pracovni"])
        if g_bod is not None:
            c = c_from_setpoint(V, kappa, g_set, I_set)
            ax.plot([g_bod * 1e9], [current(V, c, kappa, g_bod) * 1e12], "r*",
                    markersize=12, label=P["Iz_krok"])
        ax.axvline(g_contact * 1e9, color="red", linestyle=":", label="g_contact")
        ax.set_xlabel(P["g_osa"])
        ax.set_ylabel("I [pA]")
        if log:
            ax.set_yscale("log")
            ax.set_title(P["Iz_t_log"])
            dekada = math.log(10.0) / (2.0 * kappa) * 1e12
            ax.text(0.97, 0.95, P["Iz_dekada"].format(d=dekada), ha="right",
                    va="top", transform=ax.transAxes, fontsize=9,
                    bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"})
        else:
            # Lineární osa: jinak by kontakt (obrovský proud) zploštil zbytek.
            ax.set_ylim(0, 6 * I_set * 1e12)
            ax.set_title(P["Iz_t_lin"])
            ax.legend(fontsize=8)
    fig.tight_layout()
    return fig
