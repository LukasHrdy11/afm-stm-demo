"""Interaktivní STM panel pro dashboard.ipynb (ipywidgets).

Ovladače odpovídají bloku NASTAVENÍ v run_simulation.py - co se tam mění
editací kódu, se tady mění posuvníkem. Výpočet sám je ve vypocet_stm.py,
kreslení v stm_sim/plotting.py, texty v texty.py, společné prvky
v ovladace.py; tenhle modul je jen lepidlo mezi nimi.

Tři věci, kvůli kterým panel existuje (a které statický PNG neumí):
- krokování smyčky (proud -> chyba -> příkaz -> poloha hrotu),
- posuvník velikosti šumu až do bodu, kdy regulátor ztrácí stopu povrchu,
- přepínač zpětné vazby (režim konstantního proudu vs. konstantní výšky).

Grafy se renderují staticky do Output widgetu - nepotřebuje to ipympl,
stačí ipywidgets a matplotlib inline (funguje i ve webové verzi).
"""

import ipywidgets as w
from IPython.display import clear_output

from stm_sim import measured
from stm_sim.plotting import fig_konstantni_vyska, fig_proud_vs_z, fig_prubehy

from .ovladace import (
    legenda, posuvnik, rozbalovac, s_napovedou, vykresli, zalozky_grafu,
    zaskrtavatko, zobraz,
)
from .schema import fig_schema_stm
from .texty import popis, popisek, t
from .vypocet_stm import VYCHOZI, popis_kroku, posbirej_kroky, spust

# Literaturový odhad kappa (1,0e10 1/m), který změřená hodnota nahradila -
# kreslí se v I(g) pro srovnání.
KAPPA_LITERATURA = 1.0e10

# Kolik mezikroků se nabídne ke krokování (posuvník "Krok").
POCET_KROKU = 60

# Preset -> klíč textu s jeho názvem (názvy v measured.py jsou jen česky).
NAZVY_PRESETU = {"realny": "v.preset_realny", "ideal": "v.preset_ideal"}

# Které posuvníky geometrie patří ke kterému povrchu.
GEOMETRIE = {
    "step": ("H", "x_edge"),
    "ramp": ("H", "w", "x_edge"),
    "MGE": ("H", "x_edge", "mge_pocet", "mge_rozestup"),
    "atoms": ("x_edge", "atoms_H", "atoms_spacing", "atoms_sigma", "atoms_pocet"),
}

# Pořadí parametrů v legendě.
LEGENDA = ("stm.preset", "stm.controller", "stm.surface", "stm.T_SYS",
           "stm.tau", "stm.v", "stm.K_P", "stm.I_set", "stm.g_set",
           "stm.g_contact", "stm.kappa", "stm.mera_sumu", "stm.sum_proudu",
           "stm.sum_cary", "stm.sum_mezery", "stm.backward", "stm.zpetna_vazba",
           "stm.z_fixed", "stm.H", "stm.w", "stm.x_edge", "stm.atoms_H",
           "stm.atoms_spacing", "stm.atoms_sigma", "stm.atoms_pocet",
           "stm.mge_pocet", "stm.mge_rozestup", "stm.krok")


def build_stm_panel(jazyk="cs"):
    """Sestaví a vrátí celý STM panel jako jeden widget.

    Args:
        jazyk: "cs" nebo "en" - jazyk popisků, hlášek i grafů.

    Returns:
        ipywidgets.Widget k zobrazení (display(build_stm_panel())).
    """
    T = lambda klic, **pole: t(klic, jazyk, **pole)
    stav = {"overlay": None, "kroky": [], "posledni": None, "nacitam": False}

    # ------------------------------ ovladače -------------------------------
    preset = rozbalovac("stm.preset", jazyk,
                        [(T(NAZVY_PRESETU[k]), k) for k in measured.PRESETY],
                        "realny")
    regulator = rozbalovac("stm.controller", jazyk, ["P", "I", "PI"],
                           VYCHOZI["controller"])
    povrch = rozbalovac("stm.surface", jazyk, ["step", "ramp", "MGE", "atoms"],
                        VYCHOZI["surface"])
    sum_mezery = rozbalovac("stm.sum_mezery", jazyk,
                            [(T("v.bez_mezery"), None), (T("v.stojici"), "stojici"),
                             (T("v.skeny"), "skeny")], VYCHOZI["sum_mezery"])

    t_sys = posuvnik("stm.T_SYS", jazyk, VYCHOZI["T_SYS"] * 1e6, 0.0, 500.0, 10.0,
                     format=".0f")
    tau = posuvnik("stm.tau", jazyk, VYCHOZI["tau"] * 1e6, 20.0, 2000.0, 20.0,
                   format=".0f")
    rychlost = posuvnik("stm.v", jazyk, VYCHOZI["v"] * 1e9, 5.0, 500.0, 5.0,
                        format=".0f")
    k_p = posuvnik("stm.K_P", jazyk, VYCHOZI["K_P"] * 1e9, 0.0, 1.0, 0.001)
    i_set = posuvnik("stm.I_set", jazyk, VYCHOZI["I_set"] * 1e12, 1.0, 3.5, 0.05,
                     format=".0f", log=True)
    g_set = posuvnik("stm.g_set", jazyk, VYCHOZI["g_set"] * 1e9, 0.3, 1.2, 0.01)
    g_contact = posuvnik("stm.g_contact", jazyk, VYCHOZI["g_contact"] * 1e9,
                         0.05, 0.5, 0.01)
    mira_sumu = posuvnik("stm.mera_sumu", jazyk, 1.0, 0.0, 10.0, 0.25, format=".2f")
    # Pevná výška hrotu; má smysl jen s VYPNUTOU zpětnou vazbou. Nízká
    # hodnota je ta zajímavá: ukáže, že bez regulátoru hrot do hrany narazí.
    z_fixed = posuvnik("stm.z_fixed", jazyk, VYCHOZI["g_set"] * 1e9, 0.3, 1.5, 0.01)
    radku_s = w.HTML()

    geometrie = {
        "H": posuvnik("stm.H", jazyk, VYCHOZI["H"] * 1e9, 0.02, 1.0, 0.01),
        "w": posuvnik("stm.w", jazyk, VYCHOZI["w"] * 1e9, 0.02, 3.0, 0.02),
        "x_edge": posuvnik("stm.x_edge", jazyk, VYCHOZI["x_edge"] * 1e9,
                           1.0, 10.0, 0.1, format=".1f"),
        "atoms_H": posuvnik("stm.atoms_H", jazyk, VYCHOZI["atoms_H"] * 1e9,
                            0.02, 0.5, 0.01),
        "atoms_spacing": posuvnik("stm.atoms_spacing", jazyk,
                                  VYCHOZI["atoms_spacing"] * 1e9, 0.2, 1.5, 0.05,
                                  format=".2f"),
        "atoms_sigma": posuvnik("stm.atoms_sigma", jazyk,
                                VYCHOZI["atoms_sigma"] * 1e9, 0.03, 0.4, 0.01,
                                format=".2f"),
        "atoms_pocet": posuvnik("stm.atoms_pocet", jazyk, VYCHOZI["atoms_pocet"],
                                1, 15, 1, cele=True),
        "mge_pocet": posuvnik("stm.mge_pocet", jazyk, VYCHOZI["mge_pocet"],
                              1, 15, 1, cele=True),
        "mge_rozestup": posuvnik("stm.mge_rozestup", jazyk,
                                 VYCHOZI["mge_rozestup"] * 1e9, 0.2, 2.0, 0.05,
                                 format=".2f"),
    }

    sum_proudu = zaskrtavatko("stm.sum_proudu", jazyk, VYCHOZI["sum_proudu"])
    sum_cary = zaskrtavatko("stm.sum_cary", jazyk, VYCHOZI["sum_proudu_cary"])
    backward = zaskrtavatko("stm.backward", jazyk, VYCHOZI["backward"])
    zpetna_vazba = zaskrtavatko("stm.zpetna_vazba", jazyk, True)

    prepocitat = w.Button(description=T("p.prepocitat"), button_style="primary",
                          icon="refresh")
    zamknout = s_napovedou(w.Button(description=T("p.zamknout"), icon="lock"),
                           T("p.zamknout_tip"))
    uvolnit = w.Button(description=T("p.uvolnit"), icon="unlock")

    krok = posuvnik("stm.krok", jazyk, 0, 0, 0, 1, cele=True)
    krokovat = s_napovedou(w.Button(description=T("stm.nacti_kroky"),
                                    icon="list-ol"), T("stm.nacti_kroky_tip"))
    hlaseni = w.HTML()
    vypis_kroku = w.Output()
    graf_schema = w.Output()

    # ------------------------------ logika ---------------------------------
    def parametry():
        """Posbírá hodnoty ze všech ovladačů do slovníku pro spust()."""
        p = dict(VYCHOZI)
        # Z presetu se berou jen hodnoty, které nemají vlastní ovladač
        # (kappa, V); zbytek je na widgetech.
        p.update(measured.PRESETY[preset.value])
        g = {k: v.value for k, v in geometrie.items()}
        p.update(
            controller=regulator.value, surface=povrch.value,
            T_SYS=t_sys.value * 1e-6, tau=tau.value * 1e-6,
            v=rychlost.value * 1e-9, K_P=k_p.value * 1e-9,
            I_set=i_set.value * 1e-12, g_set=g_set.value * 1e-9,
            g_contact=g_contact.value * 1e-9,
            mera_sumu=mira_sumu.value, z_fixed=z_fixed.value * 1e-9,
            sum_proudu=sum_proudu.value, sum_proudu_cary=sum_cary.value,
            sum_mezery=sum_mezery.value, backward=backward.value,
            zpetna_vazba=zpetna_vazba.value,
            H=g["H"] * 1e-9, w=g["w"] * 1e-9, x_edge=g["x_edge"] * 1e-9,
            atoms_start=g["x_edge"] * 1e-9, atoms_H=g["atoms_H"] * 1e-9,
            atoms_spacing=g["atoms_spacing"] * 1e-9,
            atoms_sigma=g["atoms_sigma"] * 1e-9, atoms_pocet=g["atoms_pocet"],
            mge_pocet=g["mge_pocet"], mge_rozestup=g["mge_rozestup"] * 1e-9,
        )
        return p

    def shrnuti(vysledek):
        """Jedna věta o tom, jak běh dopadl (náraz / rezerva do nárazu)."""
        p = vysledek["parametry"]
        res = vysledek["fwd"] or vysledek["konstantni_vyska"]
        g_min = min(res.g)
        rezerva = (g_min - p["g_contact"]) * 1e12
        if res.crashed:
            return T("stm.naraz", x=res.x[-1] * 1e9)
        return T("stm.ok", g=g_min * 1e9, rezerva=rezerva,
                 barva="#b00" if rezerva < 50 else "#060")

    def graf_prubehy():
        vysledek = stav["posledni"]
        if vysledek is None:
            return None
        p = vysledek["parametry"]
        if vysledek["fwd"] is None:
            # Zamknutá křivka ze smyčky (pozná se podle log-chyby, kterou
            # sken v konstantní výšce nemá) se vykreslí pro přímé srovnání
            # obou režimů nad stejnou hranou.
            zamknuta = stav["overlay"]
            return fig_konstantni_vyska(
                result=vysledek["konstantni_vyska"],
                surface_fn=vysledek["surface_fn"], I_set=p["I_set"],
                g_contact=p["g_contact"],
                titulek=T("stm.titulek_ch", povrch=p["surface"]),
                result_smycka=(zamknuta if hasattr(zamknuta, "e") else None),
                jazyk=jazyk)
        return fig_prubehy(
            result_fwd=vysledek["fwd"], surface_fn=vysledek["surface_fn"],
            g_contact=p["g_contact"], result_bwd=vysledek["bwd"],
            titulek=T("stm.titulek", reg=p["controller"], povrch=p["surface"],
                      tsys=p["T_SYS"] * 1e6),
            overlay=stav["overlay"], jazyk=jazyk)

    def graf_proud():
        vysledek = stav["posledni"]
        if vysledek is None:
            return None
        p = vysledek["parametry"]
        g_vse = []
        for res in (vysledek["fwd"], vysledek["bwd"], vysledek["konstantni_vyska"]):
            if res is not None:
                g_vse += list(res.g)
        g_bod = None
        if stav["kroky"] and zpetna_vazba.value:
            g_bod = stav["kroky"][min(krok.value, len(stav["kroky"]) - 1)]["g"]
        # Srovnávací křivka: u změřené kappa literaturová a naopak.
        zmerena = p["kappa"] == measured.KAPPA
        return fig_proud_vs_z(
            kappa=p["kappa"], V=p["V"], I_set=p["I_set"], g_set=p["g_set"],
            g_contact=p["g_contact"], g_skenu=(min(g_vse), max(g_vse)),
            g_bod=g_bod, kappa_ref=KAPPA_LITERATURA if zmerena else measured.KAPPA,
            zdroj_kappa="zmereno" if zmerena else "literatura", jazyk=jazyk)

    grafy = [(T("p.tab_prubehy"), graf_prubehy), (T("stm.tab_Iz"), graf_proud)]
    zalozky, zneplatni = zalozky_grafu(grafy)

    def prekresli(_=None):
        if stav["nacitam"]:
            return   # probíhá načítání presetu, překreslí se až nakonec
        p = parametry()
        if p["g_set"] <= p["g_contact"]:
            hlaseni.value = T("stm.gset_pod_kontaktem")
            return
        vysledek = spust(p)
        stav["posledni"] = vysledek
        res = vysledek["fwd"] or vysledek["konstantni_vyska"]
        delka = (max(res.x) - min(res.x)) * 1e9
        if delka > 0:
            radku_s.value = ("<span style='color:#555'>"
                             + T("p.radku_s", radku=rychlost.value / (2 * delka),
                                 delka=delka) + "</span>")
        hlaseni.value = shrnuti(vysledek)
        zneplatni()

    def nacti_preset(_=None):
        """Přepíše ovladače hodnotami presetu.

        Preset MUSÍ nastavit widgety, ne jen slovník: hodnoty se sbírají
        z ovladačů, takže cokoli, co se do widgetu nepromítne, by se hned
        zase přepsalo starou hodnotou a preset by nic nedělal.
        """
        pr = measured.PRESETY[preset.value]
        stav["nacitam"] = True
        try:
            t_sys.value = pr["T_SYS"] * 1e6
            tau.value = pr["tau"] * 1e6
            rychlost.value = pr["v"] * 1e9
            k_p.value = pr["K_P"] * 1e9
            i_set.value = pr["I_set"] * 1e12
            g_set.value = pr["g_set"] * 1e9
            g_contact.value = pr["g_contact"] * 1e9
            sum_proudu.value = pr["sum_proudu"]
            sum_mezery.value = pr["sum_mezery"]
        finally:
            stav["nacitam"] = False
        prekresli()

    def zamkni(_):
        if stav["posledni"] is None:
            return
        # Zamkne se to, co je zrovna na obrazovce - se smyčkou i bez ní.
        stav["overlay"] = (stav["posledni"]["fwd"]
                           or stav["posledni"]["konstantni_vyska"])
        prekresli()

    def uvolni(_):
        stav["overlay"] = None
        prekresli()

    def nacti_kroky(_):
        vysledek, kroky = posbirej_kroky(parametry(), pocet=POCET_KROKU)
        stav["kroky"] = kroky
        stav["posledni"] = vysledek
        krok.max = max(0, len(kroky) - 1)
        krok.value = 0
        zobraz_krok()

    def zobraz_krok(_=None):
        # Schéma smyčky s hodnotami zobrazeného kroku (bez kroků prázdné).
        krok_stav = (stav["kroky"][min(krok.value, len(stav["kroky"]) - 1)]
                     if stav["kroky"] else None)
        vykresli(graf_schema, fig_schema_stm(regulator.value, krok_stav, jazyk))
        with vypis_kroku:
            clear_output(wait=True)
            if not stav["kroky"]:
                print(T("stm.nejdriv_kroky"))
                return
            i = min(krok.value, len(stav["kroky"]) - 1)
            p = stav["posledni"]["parametry"]
            print(T("stm.krok_z", i=i + 1, n=len(stav["kroky"])))
            print(popis_kroku(stav["kroky"][i], p, jazyk))
        zneplatni([1])   # I(g) ukazuje polohu hrotu v zobrazeném kroku

    def prepni_rezim(_=None):
        # Krokování má smysl jen se smyčkou, pevná výška naopak jen bez ní.
        for ovladac in (krokovat, krok, regulator, backward):
            ovladac.disabled = not zpetna_vazba.value
        z_fixed.disabled = zpetna_vazba.value

    def prepni_sum(_=None):
        # Čáry se přidávají k šumu proudu - bez něj nemají k čemu.
        sum_cary.disabled = not sum_proudu.value

    def prepni_povrch(_=None):
        for klic, ovladac in geometrie.items():
            zobraz(ovladac, klic in GEOMETRIE[povrch.value])

    def zmena_regulatoru(_=None):
        # Kroky patří starému regulátoru - zahodit, schéma ukázat bez hodnot.
        stav["kroky"] = []
        krok.max = 0
        zobraz_krok()

    regulator.observe(zmena_regulatoru, names="value")
    for ovladac in (regulator, povrch, sum_mezery, t_sys, tau, rychlost, k_p,
                    i_set, g_set, g_contact, mira_sumu, z_fixed, sum_proudu,
                    sum_cary, backward, zpetna_vazba, *geometrie.values()):
        ovladac.observe(prekresli, names="value")
    preset.observe(nacti_preset, names="value")
    zpetna_vazba.observe(prepni_rezim, names="value")
    sum_proudu.observe(prepni_sum, names="value")
    povrch.observe(prepni_povrch, names="value")
    prepocitat.on_click(prekresli)
    zamknout.on_click(zamkni)
    uvolnit.on_click(uvolni)
    krokovat.on_click(nacti_kroky)
    krok.observe(zobraz_krok, names="value")

    # ------------------------------ rozvržení ------------------------------
    vlevo = w.VBox([preset, regulator, povrch, sum_mezery,
                    w.HBox([sum_proudu, sum_cary]),
                    w.HBox([backward, zpetna_vazba]),
                    w.HBox([prepocitat, zamknout, uvolnit]),
                    w.HTML(f"<b>{T('p.geometrie')}</b>"),
                    *geometrie.values()],
                   layout=w.Layout(width="440px", flex="0 0 auto"))
    vpravo = w.VBox([t_sys, tau, rychlost, radku_s, k_p, i_set, g_set,
                     g_contact, mira_sumu, z_fixed],
                    layout=w.Layout(width="420px", flex="0 0 auto"))

    krokovani = w.VBox([
        w.HTML(f"<h4>{T('stm.krokovani')}</h4><div>{T('stm.krokovani_popis')}</div>"),
        w.HBox([krokovat, krok]),
        graf_schema,
        vypis_kroku,
    ])

    prepni_povrch()
    prepni_sum()
    prepni_rezim()
    prekresli()
    zobraz_krok()

    panel = w.VBox([
        w.HTML(f"<h3>{T('stm.nadpis')}</h3>"),
        w.HBox([vlevo, vpravo], layout=w.Layout(justify_content="flex-start")),
        hlaseni,
        zalozky,
        w.HTML("<hr>"),
        krokovani,
        legenda(LEGENDA, jazyk),
    ])
    # Pro testy: jak panel skládá parametry z ovladačů (tests/test_interactive.py).
    panel.parametry = parametry
    return panel
