"""Sestavení webové verze nástroje (JupyterLite + Voici) do statických souborů.

Výsledek je složka HTML/JS souborů, které se dají dát na GitHub Pages (nebo
jakýkoli statický hosting) - Python běží v prohlížeči (Pyodide/WebAssembly),
uživatel nic neinstaluje. Ve veřejném repu to samé dělá GitHub Action
(.github/workflows/deploy.yml), tenhle skript je pro lokální zkoušku.

Do webu jde jen to, co nástroj za běhu potřebuje: stm_sim/, afm_sim/,
interactive/ (*.py + dashboard.ipynb). Žádná data - platí stejný invariant
přenositelnosti jako pro veřejné repo (viz publish.py).

Potřebuje (jen pro sestavení, ne pro běh nástroje):
    pip install voici-core==0.10.0 jupyterlite-core==0.7.0 \
        jupyterlite-pyodide-kernel==0.7.0 jupyterlab_widgets==3.0.17 ipywidgets==8.1.9

jupyterlite-core a pyodide-kernel musí sedět k JupyterLabu zabalenému ve
voici-core 0.10.0 (4.5.0 / jupyterlite 0.7.0); s 0.7.6 / 0.7.2 se kernel
nenačte a stránka visí na "No kernel available".

Pozor: šablona v ~/.local/share/jupyter/nbconvert/templates/lab přebije
šablonu voila a vznikne statická stránka bez kernelu. Pak stavět s čistým
HOME (HOME=/tmp/prazdny python3 build_web.py).

Spouští se z kořene repa:

    python3 build_web.py                 # -> _web/
    python3 -m http.server -d _web 8000  # pak v prohlížeči http://localhost:8000/
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KOREN = Path(__file__).resolve().parent
VYSTUP = KOREN / "_web"

# Co se kopíruje do obsahu webu. Adresáře po souborech *.py, ne rekurzivně
# (stejná opatrnost jako v publish.py).
SLOZKY = ("stm_sim", "afm_sim", "interactive")
NOTEBOOK = "interactive/dashboard.ipynb"


def priprav_obsah(cil):
    """Zkopíruje balíčky a notebook do dočasné složky obsahu."""
    for slozka in SLOZKY:
        (cil / slozka).mkdir(parents=True, exist_ok=True)
        for cesta in sorted((KOREN / slozka).glob("*.py")):
            shutil.copy2(cesta, cil / slozka / cesta.name)
    shutil.copy2(KOREN / NOTEBOOK, cil / NOTEBOOK)
    # Notebook do webu jde s vymazanými výstupy (jinak by se zobrazily staré).
    nb = json.loads((cil / NOTEBOOK).read_text())
    for bunka in nb["cells"]:
        if bunka["cell_type"] == "code":
            bunka["outputs"] = []
            bunka["execution_count"] = None
    (cil / NOTEBOOK).write_text(json.dumps(nb, ensure_ascii=False, indent=1))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        obsah = Path(tmp) / "obsah"
        priprav_obsah(obsah)
        if VYSTUP.exists():
            shutil.rmtree(VYSTUP)
        # --apps lab: vedle Voici dashboardu i plný JupyterLab (kdo chce vidět kód).
        prikaz = ["voici", "build", "--contents", str(obsah),
                  "--output-dir", str(VYSTUP), "--apps", "lab"]
        print("Spouštím:", " ".join(prikaz))
        subprocess.run(prikaz, check=True, cwd=tmp)
    # Úvodní stránka webu rovnou přesměruje na dashboard.
    (VYSTUP / "index.html").write_text(
        '<!doctype html><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0; url=voici/render/interactive/dashboard.html">'
        '<a href="voici/render/interactive/dashboard.html">dashboard</a>\n')
    print(f"\nHotovo: {VYSTUP}\n  python3 -m http.server -d {VYSTUP.name} 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
