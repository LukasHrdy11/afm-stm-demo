"""Celý dashboard jako jeden widget: přepínač jazyka, záložky panelů, náměty.

Notebook (dashboard.ipynb) jen zavolá build_dashboard() - všechno ostatní
je tady, aby šlo sestavení testovat bez notebooku a aby webová verze
(Voici) měla co nejjednodušší notebook.
"""

import ipywidgets as w

from .texty import JAZYKY, VYCHOZI_JAZYK, t
from .widgets_afm import build_afm_panel
from .widgets_kombinovany import build_kombinovany_panel
from .widgets_stm import build_stm_panel


def build_dashboard(jazyk=VYCHOZI_JAZYK):
    """Sestaví dashboard; přepnutí jazyka panely postaví znovu.

    Panely drží texty v sobě (popisky, tooltipy, grafy), takže přepnutí
    jazyka = nové panely. Nastavení ovladačů se tím vrátí na výchozí -
    jazyk se typicky volí jednou na začátku, takže to nevadí.
    """
    prepinac = w.ToggleButtons(options=[("Čeština", "cs"), ("English", "en")],
                               value=jazyk, style={"button_width": "90px"})
    popisek = w.HTML()
    obsah = w.VBox()

    def postav(_=None):
        j = prepinac.value
        popisek.value = f"<b>{t('dash.jazyk', j)}</b>"
        zalozky = w.Tab(children=[build_stm_panel(j), build_afm_panel(j),
                                  build_kombinovany_panel(j)])
        zalozky.set_title(0, t("dash.tab_stm", j))
        zalozky.set_title(1, t("dash.tab_afm", j))
        zalozky.set_title(2, t("dash.tab_komb", j))
        namety = w.Accordion(children=[w.HTML(t("dash.namety_html", j))])
        namety.set_title(0, t("dash.namety", j))
        namety.selected_index = None
        obsah.children = [w.HTML(f"<p>{t('dash.uvod', j)}</p>"), zalozky, namety]

    prepinac.observe(postav, names="value")
    postav()
    return w.VBox([w.HBox([popisek, prepinac]), obsah])


assert set(JAZYKY) == {"cs", "en"}
