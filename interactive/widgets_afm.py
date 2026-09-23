"""Interaktivní FM-AFM panel pro dashboard.ipynb (ipywidgets).

Obdoba widgets_stm.py (viz tam pro rozdělení výpočet/widgety/texty). Navíc
má část o tom, co Δf vlastně je: posun CELÉ rezonance, ne přímo měřená
veličina.

Preset se jmenuje "typický qPlus", ne "reálný přístroj": kalibrace
parametrů hrotu se nepovedla a změřený je tu jen šum (viz
afm_sim/measured.py, kde je u každé konstanty uvedeno, odkud je). Panel to
u sebe píše (texty.py, klíč afm.nekalibrovano).
"""

import ipywidgets as w
import matplotlib.pyplot as plt

from afm_sim import measured, noise
from afm_sim.plotting import (
    fig_df_vs_d, fig_frekvence_kolem_udalosti, fig_konstantni_vyska, fig_prubehy,
    fig_pohybova_rovnice, fig_rezonance_ve_skenu,
)

from .ovladace import (
    legenda, posuvnik, rozbalovac, s_napovedou, vykresli, zalozky_grafu,
    zaskrtavatko, zobraz,
)
from .schema import fig_schema_afm
from .texty import t
from .vypocet_afm import (
    VYCHOZI, PracovniBodError, d_minima_frequency_shift, faze_podel_skenu,
    odezva_pri_buzeni, pohybova_rovnice_vs_vzorec, spust,
)

# Kolik bodů skenu nabídne posuvník polohy u rezonanční křivky (přehrávání).
POCET_POLOH = 80

NAZVY_PRESETU = {"qplus": "v.preset_qplus", "ideal": "v.preset_ideal"}

GEOMETRIE = {
    "step": ("H", "x_edge"),
    "ramp": ("H", "w", "x_edge"),
    "atoms": ("x_edge", "atoms_H", "atoms_spacing", "atoms_sigma"),
    "atoms-AFM": ("atoms_afm_spacing", "atoms_afm_pocet", "atoms_afm_y"),
}

LEGENDA = ("afm.preset", "afm.controller", "afm.surface", "afm.gain_mode",
           "afm.d_set", "afm.A", "afm.tau", "afm.T_SYS", "afm.v", "afm.K_P",
           "afm.mera_sumu", "afm.sum_frekvence", "afm.sum_amplitudy",
           "afm.backward", "afm.zpetna_vazba", "afm.z_fixed", "afm.H", "afm.w",
           "afm.x_edge", "afm.atoms_H", "afm.atoms_spacing", "afm.atoms_sigma",
           "afm.atoms_afm_spacing", "afm.atoms_afm_pocet", "afm.atoms_afm_y",
           "afm.Q", "afm.poloha")


def build_afm_panel(jazyk="cs"):
    """Sestaví a vrátí celý FM-AFM panel jako jeden widget."""
    T = lambda klic, **pole: t(klic, jazyk, **pole)
    stav = {"overlay": None, "posledni": None, "nacitam": False, "p": None}

    preset = rozbalovac("afm.preset", jazyk,
                        [(T(NAZVY_PRESETU[k]), k) for k in measured.PRESETY],
                        "qplus")
    regulator = rozbalovac("afm.controller", jazyk, ["P", "I", "PI"],
                           VYCHOZI["controller"])
    povrch = rozbalovac("afm.surface", jazyk, ["step", "ramp", "atoms", "atoms-AFM"],
                        VYCHOZI["surface"])
    gain_mode = rozbalovac("afm.gain_mode", jazyk,
                           [(T("afm.fixed"), "fixed"), (T("afm.local"), "local")],
                           VYCHOZI["gain_mode"])

    d_set = posuvnik("afm.d_set", jazyk, VYCHOZI["d_set"] * 1e9, 0.5, 2.0, 0.02)
    amplituda = posuvnik("afm.A", jazyk, VYCHOZI["A"] * 1e9, 0.05, 1.5, 0.05)
    tau = posuvnik("afm.tau", jazyk, VYCHOZI["tau"] * 1e3, 0.1, 10.0, 0.1,
                   format=".1f")
    t_sys = posuvnik("afm.T_SYS", jazyk, VYCHOZI["T_SYS"] * 1e6, 0.0, 500.0, 10.0,
                     format=".0f")
    rychlost = posuvnik("afm.v", jazyk, VYCHOZI["v"] * 1e9, 5.0, 500.0, 5.0,
                        format=".0f")
    k_p = posuvnik("afm.K_P", jazyk, VYCHOZI["K_P"] * 1e9, 0.0, 0.5, 0.005)
    mira_sumu = posuvnik("afm.mera_sumu", jazyk, 1.0, 0.0, 10.0, 0.25, format=".2f")
    # Pevná výška hrotu; má smysl jen s VYPNUTOU zpětnou vazbou.
    z_fixed = posuvnik("afm.z_fixed", jazyk, VYCHOZI["d_set"] * 1e9, 0.5, 2.0, 0.02)
    radku_s = w.HTML()

    geometrie = {
        "H": posuvnik("afm.H", jazyk, VYCHOZI["H"] * 1e9, 0.02, 0.5, 0.01),
        "w": posuvnik("afm.w", jazyk, VYCHOZI["w"] * 1e9, 0.02, 3.0, 0.02),
        "x_edge": posuvnik("afm.x_edge", jazyk, VYCHOZI["x_edge"] * 1e9,
                           1.0, 10.0, 0.1, format=".1f"),
        "atoms_H": posuvnik("afm.atoms_H", jazyk, VYCHOZI["atoms_H"] * 1e9,
                            0.02, 0.4, 0.01),
        "atoms_spacing": posuvnik("afm.atoms_spacing", jazyk,
                                  VYCHOZI["atoms_spacing"] * 1e9, 0.2, 1.5, 0.05,
                                  format=".2f"),
        "atoms_sigma": posuvnik("afm.atoms_sigma", jazyk,
                                VYCHOZI["atoms_sigma"] * 1e9, 0.03, 0.4, 0.01,
                                format=".2f"),
        "atoms_afm_spacing": posuvnik("afm.atoms_afm_spacing", jazyk,
                                      VYCHOZI["atoms_afm_spacing"] * 1e9,
                                      0.3, 1.5, 0.05, format=".2f"),
        "atoms_afm_pocet": posuvnik("afm.atoms_afm_pocet", jazyk,
                                    VYCHOZI["atoms_afm_pocet"], 2, 12, 1, cele=True),
        "atoms_afm_y": posuvnik("afm.atoms_afm_y", jazyk,
                                VYCHOZI["atoms_afm_y"] * 1e9, 0.0, 0.6, 0.02,
                                format=".2f"),
    }

    sum_frekvence = zaskrtavatko("afm.sum_frekvence", jazyk, VYCHOZI["sum_frekvence"])
    sum_amplitudy = zaskrtavatko("afm.sum_amplitudy", jazyk, VYCHOZI["sum_amplitudy"])
    backward = zaskrtavatko("afm.backward", jazyk, VYCHOZI["backward"])
    zpetna_vazba = zaskrtavatko("afm.zpetna_vazba", jazyk, True)

    prepocitat = w.Button(description=T("p.prepocitat"), button_style="primary",
                          icon="refresh")
    zamknout = s_napovedou(w.Button(description=T("p.zamknout"), icon="lock"),
                           T("p.zamknout_tip"))
    uvolnit = w.Button(description=T("p.uvolnit"), icon="unlock")

    hlaseni = w.HTML()

    # --- rezonance a fáze během skenu (vlastní podpanel) --------------------
    q_faktor = posuvnik("afm.Q", jazyk, 5000.0, 2, 5.5, 0.1, format=".0f", log=True)
    poloha = posuvnik("afm.poloha", jazyk, 0, 0, POCET_POLOH - 1, 1, cele=True)
    prehrat = w.Play(value=0, min=0, max=POCET_POLOH - 1, step=1, interval=700)
    w.jslink((prehrat, "value"), (poloha, "value"))
    graf_rezonance = w.Output()

    def parametry():
        p = dict(VYCHOZI)
        # Z presetu se berou jen hodnoty bez vlastního ovladače (U0, Ra,
        # k_cant, f0); zbytek nastavuje nacti_preset() do widgetů.
        p.update(measured.PRESETY[preset.value])
        g = {k: v.value for k, v in geometrie.items()}
        p.update(
            controller=regulator.value, surface=povrch.value,
            gain_mode=gain_mode.value, d_set=d_set.value * 1e-9,
            A=amplituda.value * 1e-9, tau=tau.value * 1e-3,
            T_SYS=t_sys.value * 1e-6, v=rychlost.value * 1e-9,
            K_P=k_p.value * 1e-9, mera_sumu=mira_sumu.value,
            sum_frekvence=sum_frekvence.value, sum_amplitudy=sum_amplitudy.value,
            backward=backward.value, zpetna_vazba=zpetna_vazba.value,
            z_fixed=z_fixed.value * 1e-9, Q=q_faktor.value,
            H=g["H"] * 1e-9, w=g["w"] * 1e-9, x_edge=g["x_edge"] * 1e-9,
            atoms_start=g["x_edge"] * 1e-9, atoms_H=g["atoms_H"] * 1e-9,
            atoms_spacing=g["atoms_spacing"] * 1e-9,
            atoms_sigma=g["atoms_sigma"] * 1e-9,
            atoms_afm_spacing=g["atoms_afm_spacing"] * 1e-9,
            atoms_afm_pocet=g["atoms_afm_pocet"],
            atoms_afm_y=g["atoms_afm_y"] * 1e-9,
        )
        return p

    def shrnuti(vysledek):
        res = vysledek["fwd"] or vysledek["konstantni_vyska"]
        d_min = min(res.d)
        rezerva = (d_min - vysledek["d_contact"]) * 1e12
        if res.crashed:
            return T("afm.naraz", x=res.x[-1] * 1e9)
        if getattr(res, "unstable", False):
            return T("afm.nestabilita")
        return T("afm.ok", d=d_min * 1e9, rezerva=rezerva, df=vysledek["df_set"],
                 barva="#b00" if rezerva < 50 else "#060")

    def graf_prubehy():
        vysledek = stav["posledni"]
        if vysledek is None:
            return None
        p = vysledek["parametry"]
        if vysledek["fwd"] is None:
            zamknuta = stav["overlay"]
            return fig_konstantni_vyska(
                result=vysledek["konstantni_vyska"],
                surface_fn=vysledek["surface_fn"], df_set=vysledek["df_set"],
                d_contact=vysledek["d_contact"], atoms_row=vysledek["atoms_row"],
                titulek=T("afm.titulek_ch", povrch=p["surface"]),
                result_smycka=(zamknuta if hasattr(zamknuta, "e") else None),
                jazyk=jazyk)
        return fig_prubehy(
            result_fwd=vysledek["fwd"], surface_fn=vysledek["surface_fn"],
            d_contact=vysledek["d_contact"], df_set=vysledek["df_set"],
            result_bwd=vysledek["bwd"], atoms_row=vysledek["atoms_row"],
            titulek=T("afm.titulek", reg=p["controller"], povrch=p["surface"],
                      mode=p["gain_mode"]),
            overlay=stav["overlay"], jazyk=jazyk)

    def graf_udalost():
        # Zoom frekvence kolem nárazu/nestability, jen když k ní došlo.
        vysledek = stav["posledni"]
        if vysledek is None:
            return None
        for res, label in ((vysledek["fwd"], "forward"), (vysledek["bwd"], "backward")):
            if res is not None:
                fig = fig_frekvence_kolem_udalosti(res, vysledek["parametry"]["f0"],
                                                   label, jazyk=jazyk)
                if fig is not None:
                    return fig
        return None

    def graf_df_d():
        vysledek = stav["posledni"]
        if vysledek is None:
            return None
        p = vysledek["parametry"]
        d_vse = []
        for res in (vysledek["fwd"], vysledek["bwd"], vysledek["konstantni_vyska"]):
            if res is not None:
                d_vse += list(res.d)
        sigma = (noise.SIGMA_DF * p["mera_sumu"]
                 if p["sum_frekvence"] and p["mera_sumu"] > 0 else None)
        return fig_df_vs_d(
            A=p["A"], k_cant=p["k_cant"], f0=p["f0"], force_fn=vysledek["force_ref"],
            d_contact=vysledek["d_contact"], d_set=vysledek["d_set"],
            df_set=vysledek["df_set"],
            d_min=d_minima_frequency_shift(p, vysledek["force_ref"],
                                           vysledek["d_contact"]),
            d_skenu=(min(d_vse), max(d_vse)), sigma_df=sigma, jazyk=jazyk)

    eom_popis = w.HTML()

    def graf_eom():
        vysledek = stav["posledni"]
        if vysledek is None:
            eom_popis.value = ""
            return None
        p = vysledek["parametry"]
        e = pohybova_rovnice_vs_vzorec(vysledek)
        rel = abs(e["df_rovnice"] - e["df_vzorec"]) / max(abs(e["df_vzorec"]), 1e-12) * 100
        eom_popis.value = T("afm.eom_popis", rozdil=T(
            "afm.eom_rozdil", num=e["df_rovnice"], vz=e["df_vzorec"], rel=rel))
        return fig_pohybova_rovnice(
            p["A"], p["k_cant"], p["f0"], vysledek["force_ref"], vysledek["d_set"],
            vysledek["d_contact"], e["d_min"], e["t"], e["z"], e["d_body"],
            e["df_body"], jazyk=jazyk)

    grafy = [(T("p.tab_prubehy"), graf_prubehy), (T("afm.tab_dfd"), graf_df_d),
             (T("afm.tab_eom"), graf_eom),
             (T("p.tab_schema"), lambda: fig_schema_afm(regulator.value, jazyk))]
    zalozky, zneplatni = zalozky_grafu(grafy)
    graf_zoom = w.Output()

    def prekresli(_=None):
        if stav["nacitam"]:
            return   # probíhá načítání presetu, překreslí se až nakonec
        p = parametry()
        try:
            vysledek = spust(p)
        except PracovniBodError as chyba:
            # Starý graf se nesmí nechat na obrazovce - patřil jinému
            # nastavení a u chybové hlášky by mátl.
            hlaseni.value = ("<b style='color:#b00'>"
                             + T("afm.chyba_dset", d_set=chyba.d_set * 1e9,
                                 d_min=chyba.d_min * 1e9) + "</b>")
            stav["posledni"] = None
            zneplatni()
            vykresli(graf_zoom, None)
            prekresli_rezonanci()
            return
        stav["posledni"] = vysledek
        res = vysledek["fwd"] or vysledek["konstantni_vyska"]
        delka = (max(res.x) - min(res.x)) * 1e9
        if delka > 0:
            radku_s.value = ("<span style='color:#555'>"
                             + T("p.radku_s", radku=rychlost.value / (2 * delka),
                                 delka=delka) + "</span>")
        hlaseni.value = shrnuti(vysledek)
        zneplatni()
        vykresli(graf_zoom, graf_udalost())
        prekresli_rezonanci()

    def prekresli_rezonanci(_=None):
        vysledek = stav["posledni"]
        if vysledek is None:
            vykresli(graf_rezonance, None)
            return
        if stav.get("prubeh_Q") != q_faktor.value or stav.get("prubeh_vysledek") is not vysledek:
            stav["prubeh"] = faze_podel_skenu(vysledek, q_faktor.value)
            stav["prubeh_Q"] = q_faktor.value
            stav["prubeh_vysledek"] = vysledek
        prubeh = stav["prubeh"]
        n = len(prubeh["x"])
        i = int(round(poloha.value / max(1, POCET_POLOH - 1) * (n - 1)))
        f0, Q = vysledek["parametry"]["f0"], q_faktor.value
        vykresli(graf_rezonance, fig_rezonance_ve_skenu(
            f0, Q, prubeh, i,
            lambda df, f_drive: odezva_pri_buzeni(df, f0, Q, f_drive), jazyk=jazyk))

    def nacti_preset(_=None):
        """Přepíše ovladače hodnotami presetu.

        Preset MUSÍ nastavit widgety, ne jen slovník - hodnoty se sbírají
        z ovladačů, takže co se do widgetu nepromítne, se hned zase
        přepíše zpátky a preset by nedělal nic.
        """
        pr = measured.PRESETY[preset.value]
        stav["nacitam"] = True
        try:
            d_set.value = pr["d_set"] * 1e9
            amplituda.value = pr["A"] * 1e9
            tau.value = pr["tau"] * 1e3
            t_sys.value = pr["T_SYS"] * 1e6
            rychlost.value = pr["v"] * 1e9
            k_p.value = pr["K_P"] * 1e9
            sum_frekvence.value = pr["sum_frekvence"]
            sum_amplitudy.value = pr["sum_amplitudy"]
        finally:
            stav["nacitam"] = False
        prekresli()

    def zamkni(_):
        if stav["posledni"] is not None:
            stav["overlay"] = (stav["posledni"]["fwd"]
                               or stav["posledni"]["konstantni_vyska"])
            prekresli()

    def uvolni(_):
        stav["overlay"] = None
        prekresli()

    def prepni_rezim(_=None):
        # Pevná výška má smysl jen bez smyčky, pracovní bod jen se smyčkou.
        z_fixed.disabled = zpetna_vazba.value
        for ovladac in (regulator, gain_mode, backward):
            ovladac.disabled = not zpetna_vazba.value

    def prepni_povrch(_=None):
        # U řady BODOVÝCH atomů si pracovní bod určuje vypocet_afm sám
        # (d_set z presetu je tam příliš daleko), posuvník by jen mátl.
        je_atoms_afm = povrch.value == "atoms-AFM"
        d_set.disabled = je_atoms_afm
        d_set.description = T("afm.pevne") if je_atoms_afm else "d_set [nm]:"
        for klic, ovladac in geometrie.items():
            zobraz(ovladac, klic in GEOMETRIE[povrch.value])

    for ovladac in (regulator, povrch, gain_mode, d_set, amplituda, tau, t_sys,
                    rychlost, k_p, mira_sumu, sum_frekvence, sum_amplitudy,
                    backward, zpetna_vazba, z_fixed, *geometrie.values()):
        ovladac.observe(prekresli, names="value")
    preset.observe(nacti_preset, names="value")
    for ovladac in (q_faktor, poloha):
        ovladac.observe(prekresli_rezonanci, names="value")
    zpetna_vazba.observe(prepni_rezim, names="value")
    povrch.observe(prepni_povrch, names="value")
    prepocitat.on_click(prekresli)
    zamknout.on_click(zamkni)
    uvolnit.on_click(uvolni)

    vlevo = w.VBox([preset, regulator, povrch, gain_mode,
                    w.HBox([sum_frekvence, sum_amplitudy]),
                    w.HBox([backward, zpetna_vazba]),
                    w.HBox([prepocitat, zamknout, uvolnit]),
                    w.HTML(f"<b>{T('p.geometrie')}</b>"),
                    *geometrie.values()],
                   layout=w.Layout(width="440px", flex="0 0 auto"))
    vpravo = w.VBox([d_set, amplituda, tau, t_sys, rychlost, radku_s, k_p,
                     mira_sumu, z_fixed],
                    layout=w.Layout(width="420px", flex="0 0 auto"))

    prepni_povrch()
    prepni_rezim()
    prekresli()

    panel = w.VBox([
        w.HTML(f"<h3>{T('afm.nadpis')}</h3>"
               f"<div style='color:#555'><i>{T('afm.nekalibrovano')}</i></div>"),
        w.HBox([vlevo, vpravo], layout=w.Layout(justify_content="flex-start")),
        hlaseni,
        zalozky,
        eom_popis,
        graf_zoom,
        w.HTML(f"<hr><h4>{T('afm.co_je_df')}</h4><div>{T('afm.co_je_df_popis')}</div>"
               f"<div style='margin-top:4px'>{T('afm.rez_popis')}</div>"),
        w.HBox([q_faktor, poloha, prehrat]),
        graf_rezonance,
        legenda(LEGENDA, jazyk),
    ])
    # Pro testy: jak panel skládá parametry z ovladačů (tests/test_interactive.py).
    panel.parametry = parametry
    return panel
