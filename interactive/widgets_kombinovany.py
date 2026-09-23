"""Interaktivní panel STM + AFM: jeden vodivý kmitající hrot, dva kanály.

Obdoba widgets_stm.py / widgets_afm.py. Výpočet je ve
vypocet_kombinovany.py, fyzika v afm_sim/sim_kombinovany.py, graf
v afm_sim/plotting.py (fig_kombinovany).
"""

import ipywidgets as w

from afm_sim.plotting import fig_kombinovany

from .ovladace import (
    legenda, posuvnik, rozbalovac, s_napovedou, zalozky_grafu, zaskrtavatko,
    zobraz,
)
from .texty import t
from .vypocet_afm import PracovniBodError
from .vypocet_kombinovany import VYCHOZI, spust

GEOMETRIE = {
    "step": ("H", "x_edge"),
    "ramp": ("H", "w", "x_edge"),
    "atoms": ("x_edge", "atoms_H", "atoms_spacing", "atoms_sigma", "atoms_pocet"),
}

LEGENDA = ("kmb.rezim", "kmb.controller", "kmb.surface", "kmb.d_set", "kmb.A",
           "kmb.tau_I", "kmb.tau_df", "kmb.T_SYS", "kmb.v", "kmb.mera_sumu",
           "kmb.sum_proudu", "kmb.sum_frekvence", "kmb.backward", "kmb.z_fixed",
           "kmb.H", "kmb.w", "kmb.x_edge", "kmb.atoms_H", "kmb.atoms_spacing",
           "kmb.atoms_sigma", "kmb.atoms_pocet")


def build_kombinovany_panel(jazyk="cs"):
    """Sestaví a vrátí panel STM + AFM jako jeden widget."""
    T = lambda klic, **pole: t(klic, jazyk, **pole)
    stav = {"overlay": None, "posledni": None}

    rezim = rozbalovac("kmb.rezim", jazyk,
                       [(T("kmb.rezim_I"), "I"), (T("kmb.rezim_df"), "df"),
                        (T("kmb.rezim_vyp"), "vypnuto")], VYCHOZI["rezim"])
    regulator = rozbalovac("kmb.controller", jazyk, ["P", "I", "PI"],
                           VYCHOZI["controller"])
    povrch = rozbalovac("kmb.surface", jazyk, ["step", "ramp", "atoms"],
                        VYCHOZI["surface"])

    d_set = posuvnik("kmb.d_set", jazyk, VYCHOZI["d_set"] * 1e9, 0.68, 1.5, 0.01)
    amplituda = posuvnik("kmb.A", jazyk, VYCHOZI["A"] * 1e9, 0.05, 1.0, 0.05)
    tau_i = posuvnik("kmb.tau_I", jazyk, VYCHOZI["tau_I"] * 1e6, 20.0, 2000.0, 20.0,
                     format=".0f")
    tau_df = posuvnik("kmb.tau_df", jazyk, VYCHOZI["tau_df"] * 1e3, 0.1, 10.0, 0.1,
                      format=".1f")
    t_sys = posuvnik("kmb.T_SYS", jazyk, VYCHOZI["T_SYS"] * 1e6, 0.0, 500.0, 10.0,
                     format=".0f")
    rychlost = posuvnik("kmb.v", jazyk, VYCHOZI["v"] * 1e9, 5.0, 500.0, 5.0,
                        format=".0f")
    mira_sumu = posuvnik("kmb.mera_sumu", jazyk, 1.0, 0.0, 10.0, 0.25, format=".2f")
    z_fixed = posuvnik("kmb.z_fixed", jazyk, VYCHOZI["d_set"] * 1e9, 0.6, 1.5, 0.01)

    geometrie = {
        "H": posuvnik("kmb.H", jazyk, VYCHOZI["H"] * 1e9, 0.02, 0.5, 0.01),
        "w": posuvnik("kmb.w", jazyk, VYCHOZI["w"] * 1e9, 0.02, 3.0, 0.02),
        "x_edge": posuvnik("kmb.x_edge", jazyk, VYCHOZI["x_edge"] * 1e9,
                           1.0, 10.0, 0.1, format=".1f"),
        "atoms_H": posuvnik("kmb.atoms_H", jazyk, VYCHOZI["atoms_H"] * 1e9,
                            0.02, 0.4, 0.01),
        "atoms_spacing": posuvnik("kmb.atoms_spacing", jazyk,
                                  VYCHOZI["atoms_spacing"] * 1e9, 0.2, 1.5, 0.05,
                                  format=".2f"),
        "atoms_sigma": posuvnik("kmb.atoms_sigma", jazyk,
                                VYCHOZI["atoms_sigma"] * 1e9, 0.03, 0.4, 0.01,
                                format=".2f"),
        "atoms_pocet": posuvnik("kmb.atoms_pocet", jazyk, VYCHOZI["atoms_pocet"],
                                1, 12, 1, cele=True),
    }

    sum_proudu = zaskrtavatko("kmb.sum_proudu", jazyk, VYCHOZI["sum_proudu"])
    sum_frekvence = zaskrtavatko("kmb.sum_frekvence", jazyk, VYCHOZI["sum_frekvence"])
    backward = zaskrtavatko("kmb.backward", jazyk, VYCHOZI["backward"])

    prepocitat = w.Button(description=T("p.prepocitat"), button_style="primary",
                          icon="refresh")
    zamknout = s_napovedou(w.Button(description=T("p.zamknout"), icon="lock"),
                           T("p.zamknout_tip"))
    uvolnit = w.Button(description=T("p.uvolnit"), icon="unlock")
    hlaseni = w.HTML()

    def parametry():
        p = dict(VYCHOZI)
        g = {k: v.value for k, v in geometrie.items()}
        p.update(
            rezim=rezim.value, controller=regulator.value, surface=povrch.value,
            d_set=d_set.value * 1e-9, A=amplituda.value * 1e-9,
            tau_I=tau_i.value * 1e-6, tau_df=tau_df.value * 1e-3,
            T_SYS=t_sys.value * 1e-6, v=rychlost.value * 1e-9,
            mera_sumu=mira_sumu.value, sum_proudu=sum_proudu.value,
            sum_frekvence=sum_frekvence.value, backward=backward.value,
            z_fixed=z_fixed.value * 1e-9,
            H=g["H"] * 1e-9, w=g["w"] * 1e-9, x_edge=g["x_edge"] * 1e-9,
            atoms_start=g["x_edge"] * 1e-9, atoms_H=g["atoms_H"] * 1e-9,
            atoms_spacing=g["atoms_spacing"] * 1e-9,
            atoms_sigma=g["atoms_sigma"] * 1e-9, atoms_pocet=g["atoms_pocet"],
        )
        return p

    def graf():
        vysledek = stav["posledni"]
        if vysledek is None:
            return None
        p = vysledek["parametry"]
        nazvy = {"I": T("kmb.rezim_I"), "df": T("kmb.rezim_df"),
                 "vypnuto": T("kmb.rezim_vyp")}
        return fig_kombinovany(
            vysledek["fwd"], vysledek["surface_fn"], vysledek["I_set"],
            vysledek["df_set"], vysledek["d_contact"], result_bwd=vysledek["bwd"],
            titulek=T("kmb.titulek", rezim=nazvy[p["rezim"]], reg=p["controller"],
                      povrch=p["surface"]),
            overlay=stav["overlay"], jazyk=jazyk)

    zalozky, zneplatni = zalozky_grafu([(T("p.tab_prubehy"), graf)])

    def prekresli(_=None):
        p = parametry()
        try:
            vysledek = spust(p)
        except PracovniBodError as chyba:
            hlaseni.value = ("<b style='color:#b00'>"
                             + T("afm.chyba_dset", d_set=chyba.d_set * 1e9,
                                 d_min=chyba.d_min * 1e9) + "</b>")
            stav["posledni"] = None
            zneplatni()
            return
        stav["posledni"] = vysledek
        res = vysledek["fwd"]
        d_min = min(res.d)
        rezerva = (d_min - vysledek["d_contact"]) * 1e12
        if res.crashed:
            hlaseni.value = T("afm.naraz", x=res.x[-1] * 1e9)
        else:
            hlaseni.value = T("kmb.ok", d=d_min * 1e9, rezerva=rezerva,
                              I=vysledek["I_set"] * 1e12, df=vysledek["df_set"],
                              barva="#b00" if rezerva < 50 else "#060")
        zneplatni()

    def zamkni(_):
        if stav["posledni"] is not None:
            stav["overlay"] = stav["posledni"]["fwd"]
            prekresli()

    def uvolni(_):
        stav["overlay"] = None
        prekresli()

    def prepni_rezim(_=None):
        smycka = rezim.value != "vypnuto"
        z_fixed.disabled = smycka
        for ovladac in (regulator, backward):
            ovladac.disabled = not smycka
        tau_i.disabled = rezim.value != "I"
        tau_df.disabled = rezim.value != "df"

    def prepni_povrch(_=None):
        for klic, ovladac in geometrie.items():
            zobraz(ovladac, klic in GEOMETRIE[povrch.value])

    for ovladac in (rezim, regulator, povrch, d_set, amplituda, tau_i, tau_df, t_sys,
                    rychlost, mira_sumu, z_fixed, sum_proudu, sum_frekvence,
                    backward, *geometrie.values()):
        ovladac.observe(prekresli, names="value")
    rezim.observe(prepni_rezim, names="value")
    povrch.observe(prepni_povrch, names="value")
    prepocitat.on_click(prekresli)
    zamknout.on_click(zamkni)
    uvolnit.on_click(uvolni)

    vlevo = w.VBox([rezim, regulator, povrch,
                    w.HBox([sum_proudu, sum_frekvence]), backward,
                    w.HBox([prepocitat, zamknout, uvolnit]),
                    w.HTML(f"<b>{T('p.geometrie')}</b>"), *geometrie.values()],
                   layout=w.Layout(width="440px", flex="0 0 auto"))
    vpravo = w.VBox([d_set, amplituda, tau_i, tau_df, t_sys, rychlost, mira_sumu,
                     z_fixed], layout=w.Layout(width="420px", flex="0 0 auto"))

    prepni_povrch()
    prepni_rezim()
    prekresli()

    panel = w.VBox([
        w.HTML(f"<h3>{T('kmb.nadpis')}</h3><div style='color:#555'>"
               f"<i>{T('kmb.popis')}</i></div>"),
        w.HBox([vlevo, vpravo], layout=w.Layout(justify_content="flex-start")),
        hlaseni,
        zalozky,
        legenda(LEGENDA, jazyk),
    ])
    panel.parametry = parametry
    return panel
