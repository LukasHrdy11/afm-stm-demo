"""Vykreslení výsledků FM-AFM simulace - sdílené mezi CLI skriptem a UI.

Obdoba stm_sim/plotting.py (viz tam pro zdůvodnění a pravidla). Platí
totéž: modul NEZNÁ žádnou cestu, nesmí v něm být savefig ani odkaz na
export/ - dostane data, vrátí Figure.

Proti STM přibývá čtvrtý panel (Δf) a jedna zvláštnost: u povrchu
"atoms-AFM" je řada BODOVÝCH atomů, která nemá výšku h(x). Místo profilu
povrchu se proto kreslí značky atomů v rovině z = 0.
"""

import matplotlib.pyplot as plt
import numpy as np

from .frequency_shift import frequency_shift

# Popisky grafů ve dvou jazycích (viz stm_sim/plotting.py). Výchozí "cs"
# dává přesně původní grafy dávkového skriptu.
_POPISKY = {
    "cs": {
        "fwd": "forward", "bwd": "backward", "ztip_fwd": "z_tip (forward)",
        "ztip_bwd": "z_tip (backward)", "atomy": "atomy (body)", "h": "h (povrch)",
        "vyska": "výška [nm]", "t_vyska": "Výška hrotu a povrchu",
        "t_d": "Vzdálenost hrot-vzorek (mean poloha)",
        "t_chyba": "Chyba regulátoru (df_set - Δf)", "t_df": "Posun frekvence",
        "ref": "referenční běh", "naraz": "NÁRAZ", "nestabilita": "NESTABILITA",
        "t_udalost": "t - t_událost [µs]  ({label})",
        "t_zoom": "Rezonanční frekvence cantileveru kolem nárazu/nestability",
        "ztip_ch": "z_tip (konstantní výška)", "ztip_smycka": "z_tip (se zpětnou vazbou)",
        "t_ch": "Hrot stojí, povrch se mění", "df_ch": "Δf (bez zpětné vazby)",
        "df_smycka": "Δf (se zpětnou vazbou)", "t_df_ch": "Δf kopíruje topografii",
        "d_ch": "konstantní výška", "d_smycka": "se zpětnou vazbou",
        "dfd_t_F": "Síla hrot-vzorek F(d) (ve střední poloze kmitu)",
        "dfd_t_df": "Posun frekvence Δf(d) - vážený průměr síly přes kmit",
        "dfd_min": "minimum Δf (hranice stabilní větve)",
        "dfd_nestab": "zde smyčka reguluje opačně",
        "dfd_pracovni": "pracovní bod (d_set, Δf_set)", "dfd_sken": "d během skenu",
        "dfd_sum": "Δf_set ± σ šumu", "dfd_osa": "vzdálenost d [nm]",
        "dfd_F": "F [nN]", "dfd_zoom": "výřez u pracovního bodu",
        "rez_t": "Rezonance v bodě x = {x:.2f} nm (Δf = {df:+.3f} Hz, změřeno {dfm:+.3f} Hz)",
        "rez_volny": "volný cantilever (Δf = 0)", "rez_pravy": "nad povrchem (bez šumu)",
        "rez_meas": "nad povrchem (se šumem Δf)", "rez_buzeni": "buzení f0",
        "rez_amp": "amplituda [rel.]", "rez_faze": "fáze [°]", "rez_f": "f - f0 [Hz]",
        "rez_t_x": "Fáze při buzení na f0 podél skenu (AM pohled)",
        "rez_x": "x [nm]", "rez_bez_sumu": "bez šumu", "rez_se_sumem": "se šumem Δf",
        "rez_poloha": "zobrazená poloha",
        "rez_zoom": "u f0: φ = {fd:.2f}° (se šumem {fm:.2f}°)",
        "eom_t_z": "Kmit hrotu z(t) v d_set = {d:.2f} nm a síla, kterou cítí",
        "eom_z": "z [nm]", "eom_Ft": "F [pN]", "eom_t": "t [µs]",
        "eom_t_int": "Co vzorec 17.15 průměruje: F(d + A·sinθ)·sinθ",
        "eom_theta": "θ [rad] (θ = -π/2: dolní bod obratu, u vzorku)",
        "eom_t_df": "Δf(d): pohybová rovnice (body) vs. vzorec 17.15 (čára)",
        "eom_vzorec": "vzorec 17.15 (harmonic balance)",
        "eom_num": "pohybová rovnice (frekvence z průchodů nulou)",
        "kmb_t_z": "Výška hrotu a povrchu", "kmb_t_I": "Tunelový proud ⟨I⟩ (log. osa)",
        "kmb_t_df": "Posun frekvence Δf", "kmb_t_d": "Vzdálenost d (střed kmitu)",
        "kmb_reg": " - REGULOVANÝ kanál", "kmb_pas": " - zaznamenáno pasivně",
        "kmb_meas": "měřeno (se šumem)", "kmb_pravy": "bez šumu",
        "eom_rozdil": "v d_set: rovnice {num:+.4f} Hz, vzorec {vz:+.4f} Hz (rozdíl {rel:.2g} %)",
    },
    "en": {
        "fwd": "forward", "bwd": "backward", "ztip_fwd": "z_tip (forward)",
        "ztip_bwd": "z_tip (backward)", "atomy": "atoms (points)", "h": "h (surface)",
        "vyska": "height [nm]", "t_vyska": "Tip and surface height",
        "t_d": "Tip-sample distance (mean position)",
        "t_chyba": "Controller error (df_set - Δf)", "t_df": "Frequency shift",
        "ref": "reference run", "naraz": "CRASH", "nestabilita": "INSTABILITY",
        "t_udalost": "t - t_event [µs]  ({label})",
        "t_zoom": "Cantilever resonance frequency around the crash/instability",
        "ztip_ch": "z_tip (constant height)", "ztip_smycka": "z_tip (with feedback)",
        "t_ch": "Tip fixed, surface changes", "df_ch": "Δf (feedback off)",
        "df_smycka": "Δf (with feedback)", "t_df_ch": "Δf follows the topography",
        "d_ch": "constant height", "d_smycka": "with feedback",
        "dfd_t_F": "Tip-sample force F(d) (at the mean position of the oscillation)",
        "dfd_t_df": "Frequency shift Δf(d) - force averaged over the oscillation",
        "dfd_min": "minimum of Δf (edge of the stable branch)",
        "dfd_nestab": "here the loop regulates the wrong way",
        "dfd_pracovni": "working point (d_set, Δf_set)", "dfd_sken": "d during the scan",
        "dfd_sum": "Δf_set ± noise σ", "dfd_osa": "distance d [nm]",
        "dfd_F": "F [nN]", "dfd_zoom": "zoom around the working point",
        "rez_t": "Resonance at x = {x:.2f} nm (Δf = {df:+.3f} Hz, measured {dfm:+.3f} Hz)",
        "rez_volny": "free cantilever (Δf = 0)", "rez_pravy": "above the surface (no noise)",
        "rez_meas": "above the surface (with Δf noise)", "rez_buzeni": "drive at f0",
        "rez_amp": "amplitude [rel.]", "rez_faze": "phase [°]", "rez_f": "f - f0 [Hz]",
        "rez_t_x": "Phase with the drive at f0 along the scan (AM view)",
        "rez_x": "x [nm]", "rez_bez_sumu": "no noise", "rez_se_sumem": "with Δf noise",
        "rez_poloha": "displayed position",
        "rez_zoom": "at f0: φ = {fd:.2f}° (with noise {fm:.2f}°)",
        "eom_t_z": "Tip oscillation z(t) at d_set = {d:.2f} nm and the force it feels",
        "eom_z": "z [nm]", "eom_Ft": "F [pN]", "eom_t": "t [µs]",
        "eom_t_int": "What formula 17.15 averages: F(d + A·sinθ)·sinθ",
        "eom_theta": "θ [rad] (θ = -π/2: lower turning point, at the sample)",
        "eom_t_df": "Δf(d): equation of motion (points) vs. formula 17.15 (line)",
        "eom_vzorec": "formula 17.15 (harmonic balance)",
        "eom_num": "equation of motion (frequency from zero crossings)",
        "kmb_t_z": "Tip and surface height", "kmb_t_I": "Tunnelling current ⟨I⟩ (log axis)",
        "kmb_t_df": "Frequency shift Δf", "kmb_t_d": "Distance d (centre of oscillation)",
        "kmb_reg": " - REGULATED channel", "kmb_pas": " - recorded passively",
        "kmb_meas": "measured (with noise)", "kmb_pravy": "no noise",
        "eom_rozdil": "at d_set: equation {num:+.4f} Hz, formula {vz:+.4f} Hz (difference {rel:.2g} %)",
    },
}


def _nm(hodnoty):
    """Převod pole metrů na nanometry (kvůli čitelnosti os)."""
    return [h * 1e9 for h in hodnoty]


def fig_prubehy(result_fwd, surface_fn, d_contact, df_set, result_bwd=None,
                titulek="", atoms_row=None, overlay=None,
                overlay_popis=None, jazyk="cs"):
    """Postaví čtyřpanelový graf: výška hrotu, vzdálenost d, chyba, Δf.

    Args:
        result_fwd: výsledek forward průjezdu (afm_sim.sim.run_loop).
        surface_fn: funkce h(x) -> výška povrchu [m]; ignoruje se, pokud
            je zadaný atoms_row (bodové atomy nemají h(x)).
        d_contact: vzdálenost, při které se hlásí náraz [m].
        df_set: setpoint posunu frekvence [Hz] (referenční čára).
        result_bwd: výsledek backward průjezdu, nebo None.
        titulek: dodatek do titulku horního panelu.
        atoms_row: AtomRow pro povrch "atoms-AFM", nebo None. Když je
            zadaná, kreslí se místo profilu povrchu značky atomů.
        overlay: starší výsledek vykreslený poloprůhledně na pozadí, nebo
            None (porovnání dvou běhů v jednom grafu).
        overlay_popis: popisek zamknuté křivky v legendě (None = výchozí).
        jazyk: "cs" nebo "en" - jazyk popisků v obrázku.

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    if overlay_popis is None:
        overlay_popis = P["ref"]
    fig, axes = plt.subplots(4, 1, figsize=(7, 10))

    if overlay is not None:
        styl = {"color": "gray", "alpha": 0.5, "linestyle": "--", "linewidth": 1.0}
        axes[0].plot(_nm(overlay.x), _nm(overlay.z_tip), label=overlay_popis, **styl)
        axes[1].plot(_nm(overlay.x), _nm(overlay.d), label=overlay_popis, **styl)
        axes[2].plot(_nm(overlay.x), overlay.e, label=overlay_popis, **styl)
        axes[3].plot(_nm(overlay.x), overlay.df, label=overlay_popis, **styl)

    axes[0].plot(_nm(result_fwd.x), _nm(result_fwd.z_tip), label=P["ztip_fwd"])
    if result_bwd is not None:
        axes[0].plot(_nm(result_bwd.x), _nm(result_bwd.z_tip),
                     label=P["ztip_bwd"])
    if atoms_row is not None:
        # Bodové atomy: značky v rovině atomů místo (plochého) h(x).
        axes[0].plot(atoms_row.x * 1e9, np.zeros(atoms_row.n), "ko",
                     label=P["atomy"])
    else:
        h_curve = [surface_fn(x) for x in result_fwd.x]
        axes[0].plot(_nm(result_fwd.x), _nm(h_curve), "--", label=P["h"])
    axes[0].set_xlabel("x [nm]")
    axes[0].set_ylabel(P["vyska"])
    axes[0].set_title(f"{P['t_vyska']} ({titulek})" if titulek
                      else P["t_vyska"])
    axes[0].legend()

    axes[1].plot(_nm(result_fwd.x), _nm(result_fwd.d), label=P["fwd"])
    if result_bwd is not None:
        axes[1].plot(_nm(result_bwd.x), _nm(result_bwd.d), label=P["bwd"])
    axes[1].axhline(d_contact * 1e9, color="red", linestyle=":", label="d_contact")
    axes[1].set_xlabel("x [nm]")
    axes[1].set_ylabel("d [nm]")
    axes[1].set_title(P["t_d"])
    axes[1].legend()

    axes[2].plot(_nm(result_fwd.x), result_fwd.e, label=P["fwd"])
    if result_bwd is not None:
        axes[2].plot(_nm(result_bwd.x), result_bwd.e, label=P["bwd"])
    axes[2].set_xlabel("x [nm]")
    axes[2].set_ylabel("e [Hz]")
    axes[2].set_title(P["t_chyba"])
    if result_bwd is not None:
        axes[2].legend()

    axes[3].plot(_nm(result_fwd.x), result_fwd.df, label=P["fwd"])
    if result_bwd is not None:
        axes[3].plot(_nm(result_bwd.x), result_bwd.df, label=P["bwd"])
    axes[3].axhline(df_set, color="gray", linestyle=":", label="df_set")
    axes[3].set_xlabel("x [nm]")
    axes[3].set_ylabel("Δf [Hz]")
    axes[3].set_title(P["t_df"])
    axes[3].legend()

    fig.tight_layout()
    return fig


def fig_frekvence_kolem_udalosti(result, f0, label, n_okno=300, jazyk="cs"):
    """Zoom rezonanční frekvence f(t) = f0 + Δf(d) kolem nárazu/nestability.

    Stávající data z result.df, jen jiný výřez a osa (čas místo x).

    Fáze se nevykresluje - model je čistě konzervativní (Lennard-Jones),
    bez disipace, takže fázový posun by nebyl reálným výstupem simulace.

    Args:
        result: výsledek s crashed nebo unstable = True.
        f0: rezonanční frekvence cantileveru [Hz].
        label: který průjezd to je ("forward"/"backward"), do popisku osy.
        n_okno: kolik kroků před událostí se vykreslí.

    Returns:
        matplotlib Figure, nebo None, pokud v tomto běhu k události nedošlo.
    """
    if not (result.crashed or result.unstable):
        return None
    P = _POPISKY[jazyk]

    i_udalost = result.crash_index if result.crashed else result.unstable_index
    i_start = max(0, i_udalost - n_okno)
    t_okno = [(t - result.t[i_udalost]) * 1e6 for t in result.t[i_start:i_udalost + 1]]
    f_okno = [f0 + df for df in result.df[i_start:i_udalost + 1]]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t_okno, [f * 1e-3 for f in f_okno])
    ax.axvline(0.0, color="red", linestyle=":",
               label=P["naraz"] if result.crashed else P["nestabilita"])
    ax.axhline(f0 * 1e-3, color="gray", linestyle="--", label="f0")
    ax.set_xlabel(P["t_udalost"].format(label=label))
    ax.set_ylabel("f = f0 + Δf [kHz]")
    ax.set_title(P["t_zoom"])
    ax.legend()
    fig.tight_layout()
    return fig


def fig_konstantni_vyska(result, surface_fn, df_set, d_contact, titulek="",
                         atoms_row=None, result_smycka=None, jazyk="cs"):
    """Graf skenu s VYPNUTOU zpětnou vazbou (režim konstantní výšky).

    Obdoba stm_sim.plotting.fig_konstantni_vyska pro AFM. Ukazuje, co se
    se zapnutou smyčkou nevidí: topografie se promítne rovnou do Δf, místo
    aby ji regulátor vykompenzoval pohybem hrotu.

    Δf se na rozdíl od proudu u STM kreslí v lineární ose - není
    exponenciální a navíc je záporná.

    Args:
        result: ConstantHeightResult z afm_sim.sim.constant_height_scan().
        surface_fn: funkce h(x) -> výška povrchu [m].
        df_set: Δf pracovního bodu [Hz] (referenční čára).
        d_contact: vzdálenost, při které se hlásí náraz [m].
        titulek: dodatek do titulku horního panelu.
        atoms_row: AtomRow pro povrch "atoms-AFM", nebo None.
        result_smycka: volitelný výsledek TÉHOŽ povrchu se zapnutou smyčkou,
            vykreslený pro přímé srovnání obou režimů.
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
    if atoms_row is not None:
        axes[0].plot(atoms_row.x * 1e9, np.zeros(atoms_row.n), "ko",
                     label=P["atomy"])
    else:
        h_curve = [surface_fn(x) for x in result.x]
        axes[0].plot(_nm(result.x), _nm(h_curve), "--", label=P["h"])
    axes[0].set_xlabel("x [nm]")
    axes[0].set_ylabel(P["vyska"])
    axes[0].set_title(f"{P['t_ch']} ({titulek})" if titulek
                      else P["t_ch"])
    axes[0].legend()

    axes[1].plot(_nm(result.x), result.df_meas, label=P["df_ch"])
    if result_smycka is not None:
        axes[1].plot(_nm(result_smycka.x), result_smycka.df_meas,
                     label=P["df_smycka"])
    axes[1].axhline(df_set, color="red", linestyle=":", label="df_set")
    axes[1].set_xlabel("x [nm]")
    axes[1].set_ylabel("Δf [Hz]")
    axes[1].set_title(P["t_df_ch"])
    axes[1].legend()

    axes[2].plot(_nm(result.x), _nm(result.d), label=P["d_ch"])
    if result_smycka is not None:
        axes[2].plot(_nm(result_smycka.x), _nm(result_smycka.d),
                     label=P["d_smycka"])
    axes[2].axhline(d_contact * 1e9, color="red", linestyle=":", label="d_contact")
    axes[2].set_xlabel("x [nm]")
    axes[2].set_ylabel("d [nm]")
    axes[2].set_title(P["t_d"])
    axes[2].legend()

    fig.tight_layout()
    return fig


def fig_df_vs_d(A, k_cant, f0, force_fn, d_contact, d_set, df_set, d_min,
                d_skenu=None, sigma_df=None, jazyk="cs"):
    """Síla F(d) a posun frekvence Δf(d) s vyznačeným pracovním bodem.

    Ukazuje, proč je u AFM pracovní bod složitější než u STM: Δf(d) NENÍ
    monotónní. Za minimem (blíž ke vzorku) má citlivost opačné znaménko
    a smyčka by hrot místo odtažení přitáhla.

    Args:
        A, k_cant, f0: parametry cantileveru.
        force_fn: F(d) [N] - u bodových atomů síla nad referenčním atomem.
        d_contact: vzdálenost, při které se hlásí náraz [m].
        d_set, df_set: pracovní bod [m], [Hz].
        d_min: poloha minima Δf(d) [m].
        d_skenu: (d_min, d_max) během skenu [m], nebo None.
        sigma_df: směrodatná odchylka šumu Δf [Hz] (pás kolem df_set), nebo None.
        jazyk: "cs" nebo "en".

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    d = np.linspace(0.98 * d_contact, max(2.5e-9, d_set + 1.0e-9), 300)
    F = np.array([force_fn(di) for di in d])
    df = np.array([frequency_shift(di, A, k_cant, f0, force_fn) for di in d])

    fig, axes = plt.subplots(2, 1, figsize=(8, 6.5), sharex=True)
    for ax in axes:
        if d_skenu is not None:
            ax.axvspan(d_skenu[0] * 1e9, d_skenu[1] * 1e9, color="tab:orange",
                       alpha=0.25, label=P["dfd_sken"])
        ax.axvspan(d[0] * 1e9, d_min * 1e9, color="red", alpha=0.07,
                   label=P["dfd_nestab"])
        ax.axvline(d_min * 1e9, color="purple", linestyle="--", label=P["dfd_min"])
        ax.axvline(d_contact * 1e9, color="red", linestyle=":", label="d_contact")
        ax.axvline(d_set * 1e9, color="k", linewidth=0.5)

    axes[0].plot(d * 1e9, F * 1e9)
    axes[0].axhline(0.0, color="gray", linewidth=0.5)
    axes[0].set_ylabel(P["dfd_F"])
    axes[0].set_title(P["dfd_t_F"])
    # Odpudivá větev u kontaktu jde do obrovských hodnot a zploštila by zbytek.
    rozsah = max(abs(F.min()), 1e-12) * 1e9
    axes[0].set_ylim(-1.3 * rozsah, 1.0 * rozsah)

    axes[1].plot(d * 1e9, df)
    if sigma_df:
        axes[1].axhspan(df_set - sigma_df, df_set + sigma_df, color="gray",
                        alpha=0.3, label=P["dfd_sum"])
    axes[1].plot([d_set * 1e9], [df_set], "ko", label=P["dfd_pracovni"])
    axes[1].set_ylabel("Δf [Hz]")
    axes[1].set_xlabel(P["dfd_osa"])
    axes[1].set_title(P["dfd_t_df"])
    rozsah = max(abs(df.min()), 1e-3)
    axes[1].set_ylim(-1.3 * rozsah, 0.5 * rozsah)
    axes[1].legend(fontsize=8, loc="lower right")

    # Výřez kolem pracovního bodu: v celkovém měřítku (jáma u kontaktu) je
    # Δf u d_set skoro nula a poměr k šumu není vidět.
    okno = (d > d_set - 0.35e-9) & (d < d_set + 0.35e-9)
    if okno.sum() > 5:
        vyrez = axes[1].inset_axes([0.45, 0.42, 0.33, 0.45])
        vyrez.plot(d[okno] * 1e9, df[okno])
        if sigma_df:
            vyrez.axhspan(df_set - sigma_df, df_set + sigma_df, color="gray", alpha=0.3)
        vyrez.plot([d_set * 1e9], [df_set], "ko")
        if d_skenu is not None:
            vyrez.axvspan(d_skenu[0] * 1e9, d_skenu[1] * 1e9, color="tab:orange",
                          alpha=0.25)
        vyrez.set_xlim(d[okno][0] * 1e9, d[okno][-1] * 1e9)
        vyrez.tick_params(labelsize=7)
        vyrez.set_title(P["dfd_zoom"], fontsize=8)
    fig.tight_layout()
    return fig


def fig_rezonance_ve_skenu(f0, Q, prubeh, i, odezva, jazyk="cs"):
    """Rezonanční křivka v jednom bodě skenu + fáze podél celého skenu.

    Horní dva panely: amplituda a fáze odezvy kolem f0 - volný cantilever,
    rezonance posunutá pravým Δf(x_i) a zašuměným Δf_meas(x_i); svislá čára
    je budicí frekvence f0 a bod na ní je fáze, kterou by AM detekce změřila.
    Spodní panel: tatáž fáze podél celého skenu, s vyznačeným bodem i.

    Args:
        f0, Q: parametry cantileveru.
        prubeh: slovník z interactive.vypocet_afm.faze_podel_skenu().
        i: index zobrazeného bodu skenu.
        odezva: funkce (df, f_drive) -> (amplituda, fáze [°]) - předává se
            zvenku, aby graf a výpočet fáze používaly jediný vzorec.
        jazyk: "cs" nebo "en".

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    sirka = f0 / Q
    f = np.linspace(f0 - 2.0 * sirka, f0 + 2.0 * sirka, 400)
    df_i, dfm_i = prubeh["df"][i], prubeh["df_meas"][i]
    fig = plt.figure(figsize=(8, 8))
    mrizka = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1.1])
    ax_a = fig.add_subplot(mrizka[0])
    ax_f = fig.add_subplot(mrizka[1], sharex=ax_a)
    ax_x = fig.add_subplot(mrizka[2])

    for df_k, styl, popis in ((0.0, dict(color="gray", linestyle="--"), P["rez_volny"]),
                              (df_i, dict(color="tab:blue"), P["rez_pravy"]),
                              (dfm_i, dict(color="tab:orange", alpha=0.8), P["rez_meas"])):
        amp, faze = odezva(df_k, f)
        ax_a.plot(f - f0, amp, label=popis, **styl)
        ax_f.plot(f - f0, faze, **styl)
    for ax in (ax_a, ax_f):
        ax.axvline(0.0, color="k", linewidth=0.8)
    a_d, faze_d = odezva(df_i, f0)
    a_m, faze_m = odezva(dfm_i, f0)
    ax_f.plot([0.0], [faze_d], "o", color="tab:blue")
    ax_f.plot([0.0], [faze_m], "o", color="tab:orange", label=P["rez_buzeni"])
    # Výřez u budicí frekvence: posun Δf je proti šířce rezonance f0/Q malý,
    # v celém okně by se křivky slily a změna fáze by nebyla vidět.
    polosirka = max(0.3, 3.0 * max(abs(df_i), abs(dfm_i)))
    fz = np.linspace(f0 - polosirka, f0 + polosirka, 200)
    vyrez = ax_f.inset_axes([0.62, 0.5, 0.36, 0.46])
    for df_k, styl in ((0.0, dict(color="gray", linestyle="--")),
                       (df_i, dict(color="tab:blue")),
                       (dfm_i, dict(color="tab:orange", alpha=0.8))):
        vyrez.plot(fz - f0, odezva(df_k, fz)[1], **styl)
    vyrez.axvline(0.0, color="k", linewidth=0.8)
    vyrez.plot([0.0], [faze_d], "o", color="tab:blue")
    vyrez.plot([0.0], [faze_m], "o", color="tab:orange")
    vyrez.set_title(P["rez_zoom"].format(fd=faze_d, fm=faze_m), fontsize=7)
    vyrez.tick_params(labelsize=7)
    ax_a.set_ylabel(P["rez_amp"])
    ax_a.set_title(P["rez_t"].format(x=prubeh["x"][i] * 1e9, df=df_i, dfm=dfm_i),
                   fontsize=10)
    ax_a.legend(fontsize=8)
    ax_f.set_ylabel(P["rez_faze"])
    ax_f.set_xlabel(P["rez_f"])

    x = prubeh["x"] * 1e9
    ax_x.plot(x, prubeh["faze_meas"], color="tab:orange", alpha=0.6,
              linewidth=0.8, label=P["rez_se_sumem"])
    ax_x.plot(x, prubeh["faze"], color="tab:blue", label=P["rez_bez_sumu"])
    ax_x.axvline(x[i], color="k", linestyle=":", label=P["rez_poloha"])
    ax_x.axhline(-90.0, color="gray", linewidth=0.5)
    ax_x.set_xlabel(P["rez_x"])
    ax_x.set_ylabel(P["rez_faze"])
    ax_x.set_title(P["rez_t_x"], fontsize=10)
    ax_x.legend(fontsize=8)
    fig.tight_layout()
    return fig


def fig_pohybova_rovnice(A, k_cant, f0, force_fn, d_set, d_contact, d_min,
                         t, z, d_body, df_body, jazyk="cs"):
    """Odkud se bere Δf: kmit hrotu, integrand vzorce 17.15 a srovnání obou cest.

    Args:
        A, k_cant, f0: parametry cantileveru.
        force_fn: F(r) [N].
        d_set: pracovní bod [m]; d_contact, d_min viz fig_df_vs_d.
        t, z: kmit v d_set z afm_sim.pohybova_rovnice.integruj_kmit (z jeden
            sloupec) - kreslí se první ~3 periody.
        d_body, df_body: vzdálenosti [m] a Δf [Hz] z pohybové rovnice.
        jazyk: "cs" nebo "en".

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    fig, axes = plt.subplots(3, 1, figsize=(8, 9))

    n3 = min(len(t), int(3.0 / (f0 * (t[1] - t[0]))) + 1)
    z3 = np.asarray(z[:n3]).ravel()
    axes[0].plot(t[:n3] * 1e6, z3 * 1e9, color="tab:blue")
    axes[0].set_ylabel(P["eom_z"], color="tab:blue")
    axes[0].set_xlabel(P["eom_t"])
    axes[0].set_title(P["eom_t_z"].format(d=d_set * 1e9), fontsize=10)
    dvojce = axes[0].twinx()
    dvojce.plot(t[:n3] * 1e6, [force_fn(d_set + zi) * 1e12 for zi in z3],
                color="tab:red")
    dvojce.set_ylabel(P["eom_Ft"], color="tab:red")

    theta = np.linspace(-np.pi / 2.0, np.pi / 2.0, 400)
    integrand = np.array([force_fn(d_set + A * np.sin(th)) for th in theta]) * np.sin(theta)
    axes[1].plot(theta, integrand * 1e12, color="tab:purple")
    axes[1].fill_between(theta, integrand * 1e12, color="tab:purple", alpha=0.25)
    axes[1].axhline(0.0, color="gray", linewidth=0.5)
    axes[1].set_xlabel(P["eom_theta"])
    axes[1].set_ylabel("F·sinθ [pN]")
    axes[1].set_title(P["eom_t_int"], fontsize=10)

    d = np.linspace(max(d_min, 1.01 * d_contact), max(2.0e-9, d_set + 0.6e-9), 200)
    df = [frequency_shift(di, A, k_cant, f0, force_fn) for di in d]
    axes[2].plot(d * 1e9, df, label=P["eom_vzorec"])
    axes[2].plot(np.asarray(d_body) * 1e9, df_body, "o", color="tab:orange",
                 label=P["eom_num"])
    axes[2].axvline(d_set * 1e9, color="k", linewidth=0.5)
    axes[2].set_xlabel(P["dfd_osa"])
    axes[2].set_ylabel("Δf [Hz]")
    axes[2].set_title(P["eom_t_df"], fontsize=10)
    axes[2].legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    return fig


def fig_kombinovany(result_fwd, surface_fn, I_set, df_set, d_contact,
                    result_bwd=None, titulek="", overlay=None, jazyk="cs"):
    """Kombinovaný STM/AFM sken: výška hrotu, proud, Δf a vzdálenost pod sebou.

    U titulku proudu a Δf je napsané, který kanál smyčka reguluje a který se
    jen zaznamenává (podle result_fwd.rezim).

    Args:
        result_fwd, result_bwd: KombinovanyResult (afm_sim.sim_kombinovany).
        surface_fn: h(x) [m].
        I_set, df_set: setpointy (referenční čáry) [A], [Hz].
        d_contact: vzdálenost nárazu [m].
        titulek: dodatek do titulku horního panelu.
        overlay: starší KombinovanyResult vykreslený šedě na pozadí, nebo None.
        jazyk: "cs" nebo "en".

    Returns:
        matplotlib Figure (volající ji musí zavřít).
    """
    P = _POPISKY[jazyk]
    rezim = result_fwd.rezim
    fig, axes = plt.subplots(4, 1, figsize=(8, 10.5), sharex=True)
    if overlay is not None:
        styl = {"color": "gray", "alpha": 0.5, "linestyle": "--", "linewidth": 1.0}
        axes[0].plot(_nm(overlay.x), _nm(overlay.z_tip), label=P["ref"], **styl)
        axes[1].semilogy(_nm(overlay.x), [i * 1e12 for i in overlay.I_meas], **styl)
        axes[2].plot(_nm(overlay.x), overlay.df_meas, **styl)
        axes[3].plot(_nm(overlay.x), _nm(overlay.d), **styl)

    pruchody = [(result_fwd, P["fwd"])]
    if result_bwd is not None:
        pruchody.append((result_bwd, P["bwd"]))
    for res, popis in pruchody:
        axes[0].plot(_nm(res.x), _nm(res.z_tip), label=f"z_tip ({popis})")
        axes[1].semilogy(_nm(res.x), [max(abs(i), 1e-15) * 1e12 for i in res.I_meas],
                         linewidth=0.8, label=popis)
        axes[2].plot(_nm(res.x), res.df_meas, linewidth=0.8, label=popis)
        axes[3].plot(_nm(res.x), _nm(res.d), label=popis)
    axes[1].semilogy(_nm(result_fwd.x), [i * 1e12 for i in result_fwd.I], color="k",
                     linewidth=0.8, label=P["kmb_pravy"])
    axes[2].plot(_nm(result_fwd.x), result_fwd.df, color="k", linewidth=0.8,
                 label=P["kmb_pravy"])
    h = [surface_fn(x) for x in result_fwd.x]
    axes[0].plot(_nm(result_fwd.x), _nm(h), "--", label=P["h"])
    axes[1].axhline(I_set * 1e12, color="red", linestyle=":", label="I_set")
    axes[2].axhline(df_set, color="red", linestyle=":", label="Δf_set")
    axes[3].axhline(d_contact * 1e9, color="red", linestyle=":", label="d_contact")

    axes[0].set_title(f"{P['kmb_t_z']} ({titulek})" if titulek else P["kmb_t_z"])
    axes[1].set_title(P["kmb_t_I"] + (P["kmb_reg"] if rezim == "I" else P["kmb_pas"]))
    axes[2].set_title(P["kmb_t_df"] + (P["kmb_reg"] if rezim == "df" else P["kmb_pas"]))
    axes[3].set_title(P["kmb_t_d"])
    axes[0].set_ylabel(P["vyska"])
    axes[1].set_ylabel("I [pA]")
    axes[2].set_ylabel("Δf [Hz]")
    axes[3].set_ylabel("d [nm]")
    axes[3].set_xlabel("x [nm]")
    for ax in axes:
        ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    return fig
