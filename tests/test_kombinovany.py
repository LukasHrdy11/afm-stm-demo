"""Korektnostní test kombinovaného STM/AFM skenu (afm_sim/sim_kombinovany.py).

Není to pytest test: skript vypíše [OK]/[SELHALO] pro každou kontrolu a na
konci souhrn.

Kombinovaná smyčka je nová fyzika, proto se kontroluje proti tomu, co už je
ověřené: v limitních případech musí dát totéž co stm_sim a afm_sim.
- režim "I" s A -> 0 (proud nestředovaný) = stm_sim.sim.run_loop,
- režim "df" = afm_sim.sim.run_loop bit po bitu (přesná cesta df_fn=None),
- režim "vypnuto" = afm_sim.sim.constant_height_scan (Δf) a pro A -> 0
  stm_sim.sim.constant_height_scan (proud).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import numpy as np


def main():
    from afm_sim import sim as afm_sim_mod
    from afm_sim.frequency_shift import frequency_shift
    from afm_sim.sim_kombinovany import c_stredovany, kombinovany_sken, tabulka_df
    from interactive import vypocet_kombinovany as vk
    from stm_sim import sim as stm_sim_mod
    from stm_sim.plant import FirstOrderPlant

    vysledky = []

    def check(description, ok, detail):
        vysledky.append(ok)
        print(f"[{'OK' if ok else 'SELHALO'}] {description}   ({detail})")

    p = dict(vk.VYCHOZI, sum_proudu=False, sum_frekvence=False)
    F = lambda r: vk.lj_force(r, p["U0"], p["Ra"])
    d_contact = vk.r_min(p["Ra"]) + p["A"]
    povrch = vk.sestav_povrch(p)

    # --- 1. režim I, A -> 0  ==  STM run_loop --------------------------------
    A0 = 1e-14
    pI = dict(p, rezim="I", A=A0)
    t_end, dt = vk.delka_skenu(pI)
    k = kombinovany_sken("I", povrch, p["v"], p["kappa"], p["V"], p["I_set"],
                         p["d_set"], F, A0, p["k_cant"], p["f0"], 0.0, d_contact, dt,
                         t_end, controller=vk.sestav_regulator(pI, F, d_contact),
                         plant=FirstOrderPlant(p["d_set"], p["T_SYS"]))
    s = stm_sim_mod.run_loop(vk.sestav_regulator(pI, F, d_contact),
                             FirstOrderPlant(p["d_set"], p["T_SYS"]), povrch, p["v"],
                             p["kappa"], p["V"], p["I_set"], p["d_set"], d_contact,
                             dt, t_end)
    rel = np.max(np.abs(np.array(k.z_tip) - np.array(s.z_tip))) / p["d_set"]
    check("Režim I s A -> 0 dá totéž co stm_sim.run_loop (dráha hrotu)",
          len(k.z_tip) == len(s.z_tip) and rel < 1e-9,
          f"kroků {len(k.z_tip)}/{len(s.z_tip)}, max rel. rozdíl {rel:.1e}")

    # --- 2. režim df  ==  AFM run_loop bit po bitu ---------------------------
    pdf = dict(p, rezim="df")
    t_end, dt = vk.delka_skenu(pdf)
    df_set = frequency_shift(p["d_set"], p["A"], p["k_cant"], p["f0"], F)
    k = kombinovany_sken("df", povrch, p["v"], p["kappa"], p["V"], p["I_set"],
                         p["d_set"], F, p["A"], p["k_cant"], p["f0"], df_set,
                         d_contact, dt, t_end,
                         controller=vk.sestav_regulator(pdf, F, d_contact),
                         plant=FirstOrderPlant(p["d_set"], p["T_SYS"]))
    a = afm_sim_mod.run_loop(vk.sestav_regulator(pdf, F, d_contact),
                             FirstOrderPlant(p["d_set"], p["T_SYS"]), povrch, p["v"],
                             F, p["A"], p["k_cant"], p["f0"], df_set, d_contact, dt,
                             t_end)
    check("Režim df dá bit-přesně totéž co afm_sim.run_loop (d i Δf)",
          k.d == a.d and k.df == a.df, f"kroků {len(k.d)}")

    # --- 3. konstantní výška == obě constant_height_scan ---------------------
    z_fix = 0.75e-9
    k = kombinovany_sken("vypnuto", povrch, p["v"], p["kappa"], p["V"], p["I_set"],
                         p["d_set"], F, p["A"], p["k_cant"], p["f0"], df_set,
                         d_contact, dt, t_end, z_fixed=z_fix)
    a = afm_sim_mod.constant_height_scan(povrch, p["v"], F, p["A"], p["k_cant"], p["f0"],
                                         d_contact, dt, t_end, z_fix)
    check("Konstantní výška: Δf bit-přesně jako afm_sim.constant_height_scan",
          k.df == a.df and k.d == a.d, f"kroků {len(k.df)}")
    k0 = kombinovany_sken("vypnuto", povrch, p["v"], p["kappa"], p["V"], p["I_set"],
                          p["d_set"], F, A0, p["k_cant"], p["f0"], df_set,
                          0.2e-9, dt, t_end, z_fixed=z_fix)
    s = stm_sim_mod.constant_height_scan(povrch, p["v"], p["kappa"], p["V"], p["I_set"],
                                         p["d_set"], 0.2e-9, dt, t_end, z_fix)
    rel = np.max(np.abs(np.array(k0.I) / np.array(s.I) - 1))
    check("Konstantní výška s A -> 0: proud jako stm_sim.constant_height_scan",
          rel < 1e-9, f"max rel. rozdíl {rel:.1e}")

    # --- 4. kalibrace středovaného proudu -----------------------------------
    c = c_stredovany(p["V"], p["kappa"], p["A"], p["d_set"], p["I_set"])
    theta = np.linspace(0, 2 * np.pi, 20001)[:-1]
    stredni = np.mean(p["V"] * c * np.exp(-2 * p["kappa"] * (p["d_set"] + p["A"] * np.sin(theta))))
    check("Proud středovaný přes kmit dá v d_set právě I_set (I0 Besselova funkce)",
          abs(stredni / p["I_set"] - 1) < 1e-6,
          f"⟨I⟩ = {stredni * 1e12:.4f} pA, I_set = {p['I_set'] * 1e12:.1f} pA")

    # --- 5. tabulka Δf -------------------------------------------------------
    df_fn = tabulka_df(p["A"], p["k_cant"], p["f0"], F, 0.98 * d_contact, 3.8e-9)
    chyba = max(abs(df_fn(x) - frequency_shift(x, p["A"], p["k_cant"], p["f0"], F))
                for x in np.linspace(d_contact, 3.5e-9, 777))
    check("Tabulka Δf(d) se liší od vzorce 17.15 o << šum Δf (0,08 Hz)",
          chyba < 1e-3, f"max chyba {chyba:.1e} Hz")

    # --- 6. panel -----------------------------------------------------------
    from interactive.widgets_kombinovany import build_kombinovany_panel
    panel = build_kombinovany_panel()
    check("Panel STM + AFM se sestaví", len(panel.children) > 0, "VBox")
    r = vk.spust(rezim="df")
    check("Režim df přes vypocet drží Δf kolem setpointu",
          abs(np.mean(r["fwd"].df) - r["df_set"]) < 0.2 and not r["fwd"].crashed,
          f"⟨Δf⟩ = {np.mean(r['fwd'].df):.3f} Hz, Δf_set = {r['df_set']:.3f} Hz")
    r = vk.spust(rezim="I")
    check("Režim I přes vypocet drží proud kolem setpointu",
          abs(np.exp(np.mean(np.log(r["fwd"].I))) / r["I_set"] - 1) < 0.1
          and not r["fwd"].crashed,
          f"geom. průměr I = {np.exp(np.mean(np.log(r['fwd'].I))) * 1e12:.1f} pA")

    print()
    print("VŠECHNY KONTROLY PROŠLY" if all(vysledky)
          else f"SELHALO {vysledky.count(False)} z {len(vysledky)}")
    return 0 if all(vysledky) else 1


if __name__ == "__main__":
    sys.exit(main())
