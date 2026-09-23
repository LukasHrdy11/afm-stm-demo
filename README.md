# STM and FM-AFM feedback loop simulation — interactive demonstration

*[Česká verze níže](#česky)*

A teaching tool for scanning probe microscopy: it simulates the feedback loop
of a scanning tunnelling microscope (STM, constant-current mode) and of a
frequency-modulation AFM (qPlus), and lets you play with it using sliders
instead of editing code. The interface is available in English and Czech.

## Open in the browser (no installation)

**https://lukashrdy11.github.io/afm-stm-demo/**

Python runs directly in the browser (JupyterLite / Pyodide). The first load
takes about 10–30 s; after that every change of a control re-runs the
simulation within a second or two. Nothing is sent anywhere.

## Run locally (optional)

```bash
git clone https://github.com/LukasHrdy11/afm-stm-demo.git
cd afm-stm-demo
pip install --user -r requirements.txt
jupyter notebook interactive/dashboard.ipynb
```

Then Run → Run All Cells. Locally the simulation is about 2–3× faster than
in the browser.

## What it shows

- **STM:** P / I / PI controller, step / ramp / chaotic / atomic surface,
  current and gap noise scaled from measured values, forward and backward
  scan, constant-current vs. constant-height mode, stepping through the loop
  (also drawn in the block diagram), current vs. gap I(g).
- **FM-AFM:** the same loop on constant Δf, force F(d) and Δf(d) with the
  stable branch, resonance and phase along the scan (with noise), Δf computed
  from the equation of motion vs. formula 17.15, loss of stability beyond the
  Δf minimum.
- **STM + AFM:** one oscillating conducting tip; the loop regulates either the
  current or Δf (the other channel is recorded passively), or runs at constant
  height with both channels.

Every control has a tooltip, and each panel has a “Parameter legend” that
states where each value comes from (measured / setting / literature / not
calibrated).

## Contents

| Folder | Contents |
|---|---|
| `stm_sim/` | STM physics: controllers, actuator, surfaces, tunnelling current, noise |
| `afm_sim/` | FM-AFM physics: frequency shift, tip force models, equation of motion, combined STM/AFM scan, noise |
| `interactive/` | interactive panels, texts (CZ/EN) and `dashboard.ipynb` (the only entry point) |
| `tests/` | correctness tests; run them directly, they print `[OK]`/`[SELHALO]` (= failed) |

The batch scripts `run_simulation.py` and `run_simulation_afm.py` compute the
same and save static PNGs (useful for slides). That the panels compute
exactly the same as the batch scripts is checked by
`tests/test_interactive.py`. `build_web.py` builds the browser version; the
GitHub Action in `.github/workflows/deploy.yml` does this on every push.

## Model limits (important for conclusions)

- **Only the loop dynamics are real, not absolute distances.** The error
  `e = ln(I/I_set) = -2·kappa·(g - g_set)` cancels the prefactor, so `g_set`
  and `g_contact` are literature estimates. Conclusions like “the safe
  distance is X nm” are beyond this model.
- **For STM, `kappa` is measured** (from a measured current-vs-Z curve) **and
  `K_P`** (from the instrument headers), as is the noise level. The other
  values are measurement settings.
- **For AFM nothing except the noise is calibrated.** An attempt to fit the
  tip parameters (U0, Ra) to a measured Δf(z) failed — the atomic
  Lennard-Jones model cannot explain how slowly the measured Δf decays. The
  values in `afm_sim/measured.py` are illustrative, and the panel says so.
- **The combined STM + AFM scan** uses one mean distance for both channels
  and a current averaged over the oscillation; it is a qualitative
  illustration.
- **Some limits are numerical, not physical.** The stability limit of `K_P`
  is an artefact of the Euler step, not a property of the instrument.

The origin of every constant is documented next to it: `stm_sim/measured.py`,
`afm_sim/measured.py`, `stm_sim/noise.py`, `afm_sim/noise.py`.

## Literature

Background for the panels: B. Voigtländer, *Scanning Probe Microscopy*
(Springer). Chapters 5.7–5.9 (feedback controller and its implementation in
STM), 17.1.1 and 17.2.2 (FM mode, the Δf formula, PLL tracking), 18 (noise in
AFM), 20.6 (constant-current vs. constant-height mode). The block diagrams in
the tool are drawn independently.

## License

MIT (see `LICENSE`) — use in teaching and modifications are welcome.

Author: Lukáš Hrdý. The tool was created as part of a thesis on the STM
feedback loop; the measured data and analyses remain in a separate
(non-public) repository, only the resulting constants with their origin are
here.

---

## Česky

Výukový nástroj k rastrovací sondové mikroskopii: simuluje zpětnovazební
smyčku tunelového mikroskopu (STM, režim konstantního proudu) a frekvenčně
modulovaného AFM (qPlus) a nechává si s ní hrát posuvníkem, ne editací kódu.
Rozhraní je česky i anglicky (přepínač nahoře v dashboardu).

**V prohlížeči bez instalace:** https://lukashrdy11.github.io/afm-stm-demo/
(Python běží přímo v prohlížeči; první načtení trvá ~10–30 s).

**Lokálně:** `pip install --user -r requirements.txt` a
`jupyter notebook interactive/dashboard.ipynb`, pak Run → Run All Cells.

**Co ukazuje:** STM smyčku (P/I/PI, různé povrchy, šum ze změřených hodnot,
krokování smyčky i v blokovém schématu, I(g)), FM-AFM smyčku (F(d) a Δf(d),
rezonance a fáze podél skenu, Δf z pohybové rovnice vs. vzorec 17.15, ztráta
stability) a kombinovaný STM + AFM sken jedním kmitajícím vodivým hrotem.
Každý ovladač má nápovědu a každý panel „Legendu parametrů“ s původem hodnot.

**Meze modelu:** reálná je dynamika smyčky, ne absolutní vzdálenosti
(`g_set`, `g_contact` jsou odhady z literatury). U STM je změřená `kappa`,
`K_P` a šum; u AFM je kalibrovaný jen šum, parametry hrotu jsou ilustrativní.
Kombinovaný sken je kvalitativní ilustrace. Mez stability `K_P` je artefakt
Eulerova kroku. Původ každé konstanty je v komentáři u ní.

Literatura: B. Voigtländer, *Scanning Probe Microscopy* (Springer), kap.
5.7–5.9, 17.1.1, 17.2.2, 18, 20.6. Licence MIT. Autor: Lukáš Hrdý.
