"""Společné stavební prvky panelů: ovladače s nápovědou, legenda, záložky grafů.

Tenhle modul drží jen "jak" (vzhled a chování widgetů), žádná čísla fyziky
ani texty - texty jsou v texty.py, výpočet ve vypocet_*.py.
"""

import ipywidgets as w
import matplotlib.pyplot as plt
from IPython.display import clear_output, display

from .texty import legenda_html, popis, popisek, t

STYL = {"description_width": "130px"}
SIRKA = "380px"


def s_napovedou(widget, text):
    """Nastaví tooltip (ipywidgets 8 `tooltip`, starší `description_tooltip`)."""
    if "tooltip" in widget.trait_names():
        widget.tooltip = text
    else:
        widget.description_tooltip = text
    return widget


def posuvnik(param, jazyk, hodnota, mini, maxi, krok, format=".3f",
             log=False, cele=False):
    """Posuvník s popiskem a nápovědou podle texty.PARAMETRY[param].

    log=True: FloatLogSlider (mini/maxi jsou exponenty desítky).
    cele=True: IntSlider.
    """
    spolecne = dict(description=popisek(param, jazyk), continuous_update=False,
                    style=STYL, layout=w.Layout(width=SIRKA))
    if cele:
        widget = w.IntSlider(value=int(hodnota), min=mini, max=maxi, step=krok,
                             **spolecne)
    elif log:
        widget = w.FloatLogSlider(value=hodnota, base=10, min=mini, max=maxi,
                                  step=krok, readout_format=format, **spolecne)
    else:
        widget = w.FloatSlider(value=hodnota, min=mini, max=maxi, step=krok,
                               readout_format=format, **spolecne)
    return s_napovedou(widget, popis(param, jazyk))


def rozbalovac(param, jazyk, moznosti, hodnota, sirka=SIRKA):
    widget = w.Dropdown(options=moznosti, value=hodnota,
                        description=popisek(param, jazyk), style=STYL,
                        layout=w.Layout(width=sirka))
    return s_napovedou(widget, popis(param, jazyk))


def zaskrtavatko(param, jazyk, hodnota):
    widget = w.Checkbox(value=hodnota, description=popisek(param, jazyk),
                        indent=False, layout=w.Layout(width="auto"))
    return s_napovedou(widget, popis(param, jazyk))


def zobraz(widget, viditelny):
    """Skryje/ukáže widget, aniž by se vyřadil z rozvržení."""
    widget.layout.display = "" if viditelny else "none"


def legenda(parametry, jazyk):
    """Sbalitelná legenda parametrů panelu (funguje i na dotykových zařízeních)."""
    obsah = w.HTML(legenda_html(parametry, jazyk))
    acc = w.Accordion(children=[obsah])
    acc.set_title(0, t("p.legenda", jazyk))
    acc.selected_index = None
    return acc


def vykresli(output, fig):
    """Vykreslí figuru do Output widgetu a zavře ji (jinak se hromadí v paměti)."""
    with output:
        clear_output(wait=True)
        if fig is not None:
            display(fig)
            plt.close(fig)


def zalozky_grafu(polozky):
    """Záložky s grafy, které se kreslí až při zobrazení.

    Kreslení matplotlibem je (hlavně ve webové verzi) nejdražší část
    překreslení, proto se kreslí jen viditelná záložka; ostatní se dokreslí,
    až je uživatel otevře.

    Args:
        polozky: seznam (titulek, funkce) - funkce bez argumentů vrací
            Figure (nebo None, když není co kreslit).

    Returns:
        (tab, zneplatni) - widget záložek a funkce, která po novém výpočtu
        označí všechny grafy za zastaralé a překreslí viditelný.
    """
    vystupy = [w.Output() for _ in polozky]
    tab = w.Tab(children=vystupy)
    for i, (titulek, _) in enumerate(polozky):
        tab.set_title(i, titulek)
    platne = set()

    def nakresli(i):
        if i is None or i in platne:
            return
        vykresli(vystupy[i], polozky[i][1]())
        platne.add(i)

    def zneplatni(indexy=None):
        """Označí grafy za zastaralé (všechny, nebo jen `indexy`)."""
        if indexy is None:
            platne.clear()
        else:
            platne.difference_update(indexy)
        nakresli(tab.selected_index)

    tab.observe(lambda zmena: nakresli(zmena["new"]), names="selected_index")
    return tab, zneplatni
