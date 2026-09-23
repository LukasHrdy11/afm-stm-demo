"""Korektnostní test textů UI (interactive/texty.py) - úplnost obou jazyků.

Není to pytest test: skript vypíše [OK]/[SELHALO] pro každou kontrolu a na
konci souhrn (stejně jako test_interactive.py).

Hlídá tři věci, které se při dopisování panelů snadno rozbijí:
- každý text má češtinu i angličtinu a žádná není prázdná,
- oba jazyky mají stejná {pole} pro format (jinak by překlad spadl až v UI),
- každý klíč, který kód panelů použije, v texty.py opravdu existuje.
"""

import re
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")

KOREN = Path(__file__).resolve().parent.parent


def _pole(text):
    return {f for _, f, _, _ in string.Formatter().parse(text) if f}


def main():
    from interactive import texty

    vysledky = []

    def check(description, ok, detail):
        vysledky.append(ok)
        print(f"[{'OK' if ok else 'SELHALO'}] {description}   ({detail})")

    obecne = texty.vsechny_klice()
    prazdne = [k for k, v in obecne.items() if len(v) != 2 or not all(x.strip() for x in v)]
    check("Každý obecný text má neprázdnou češtinu i angličtinu", not prazdne,
          f"{len(obecne)} klíčů" if not prazdne else f"chybí: {prazdne[:5]}")

    ruzna_pole = [k for k, (cs, en) in obecne.items() if _pole(cs) != _pole(en)]
    check("Oba jazyky mají stejná {pole} pro format", not ruzna_pole,
          "shoda" if not ruzna_pole else f"liší se: {ruzna_pole[:5]}")

    spatne_param = [k for k, v in texty.PARAMETRY.items()
                    if len(v) != 5 or not all(x.strip() for x in v[:4])
                    or v[4] not in texty.ZDROJE]
    check("Každý parametr má popisek i význam v obou jazycích a známý původ",
          not spatne_param,
          f"{len(texty.PARAMETRY)} parametrů" if not spatne_param
          else f"vadné: {spatne_param[:5]}")

    # Klíče použité v kódu panelů: t("..."), T("..."), posuvnik("...") apod.
    kod = "\n".join(p.read_text() for p in sorted((KOREN / "interactive").glob("*.py"))
                    if p.name != "texty.py")
    pouzite_t = set(re.findall(r"""\bT\(\s*["']([a-z_]+\.[a-z_0-9]+)["']""", kod))
    pouzite_t |= set(re.findall(r"""\bt\(\s*["']([a-z_]+\.[a-z_0-9]+)["']""", kod))
    chybi_t = sorted(k for k in pouzite_t if k not in obecne)
    check("Každý text použitý v panelech existuje v texty.py", not chybi_t,
          f"{len(pouzite_t)} použitých" if not chybi_t else f"chybí: {chybi_t}")

    pouzite_p = set(re.findall(
        r"""(?:posuvnik|rozbalovac|zaskrtavatko)\(\s*["']([a-z]+\.[A-Za-z_0-9]+)["']""", kod))
    pouzite_p |= set(re.findall(r"""["']((?:stm|afm|kmb)\.[A-Za-z_0-9]+)["']""",
                                "\n".join(re.findall(r"LEGENDA[A-Z_]* = \(([^)]*)\)", kod))))
    chybi_p = sorted(k for k in pouzite_p if k not in texty.PARAMETRY)
    check("Každý parametr použitý v panelech (a v legendě) má popis", not chybi_p,
          f"{len(pouzite_p)} použitých" if not chybi_p else f"chybí: {chybi_p}")

    # Panely a dashboard se postaví v obou jazycích.
    from interactive.dashboard_ui import build_dashboard
    for jazyk in texty.JAZYKY:
        try:
            ok = len(build_dashboard(jazyk).children) > 0
            detail = "sestaveno"
        except Exception as chyba:   # noqa: BLE001 - chceme vidět jakoukoli chybu
            ok, detail = False, repr(chyba)
        check(f"Dashboard se sestaví v jazyce {jazyk!r}", ok, detail)

    print()
    print("VŠECHNY KONTROLY PROŠLY" if all(vysledky)
          else f"SELHALO {vysledky.count(False)} z {len(vysledky)}")
    return 0 if all(vysledky) else 1


if __name__ == "__main__":
    sys.exit(main())
