"""Korektnostní test nových grafů (I(g), Δf(d)) - kreslí to, co tvrdí.

Není to pytest test: skript vypíše [OK]/[SELHALO] pro každou kontrolu a na
konci souhrn. Grafy se kontrolují přes data čar v sestavené Figure, ne
pohledem - aby se chyba v kreslení (špatné jednotky, prohozené osy)
projevila i bez člověka u obrazovky.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    from interactive import vypocet_afm, vypocet_stm
    from afm_sim.plotting import fig_df_vs_d
    from stm_sim.plotting import fig_proud_vs_z

    vysledky = []

    def check(description, ok, detail):
        vysledky.append(ok)
        print(f"[{'OK' if ok else 'SELHALO'}] {description}   ({detail})")

    # --- I(g): v log. ose přímka se sklonem -2*kappa ------------------------
    p = vypocet_stm.VYCHOZI
    fig = fig_proud_vs_z(p["kappa"], p["V"], p["I_set"], p["g_set"], p["g_contact"])
    cara = fig.axes[1].lines[0]
    g = np.asarray(cara.get_xdata()) * 1e-9
    I = np.asarray(cara.get_ydata()) * 1e-12
    sklon = np.polyfit(g, np.log(I), 1)[0]
    check("I(g) v log. ose má sklon -2*kappa", abs(sklon / (-2 * p["kappa"]) - 1) < 1e-9,
          f"sklon = {sklon:.4e} 1/m, -2κ = {-2 * p['kappa']:.4e} 1/m")
    i_set = np.interp(p["g_set"], g, I)
    check("I(g) prochází pracovním bodem (g_set, I_set)",
          abs(i_set / p["I_set"] - 1) < 1e-3, f"I(g_set) = {i_set * 1e12:.2f} pA")
    plt.close(fig)

    # --- Δf(d): minimum sedí s tím, co hlídá vypocet_afm -------------------
    r = vypocet_afm.spust()
    pa = r["parametry"]
    d_min = vypocet_afm.d_minima_frequency_shift(pa, r["force_ref"], r["d_contact"])
    fig = fig_df_vs_d(pa["A"], pa["k_cant"], pa["f0"], r["force_ref"], r["d_contact"],
                      r["d_set"], r["df_set"], d_min)
    cara = [c for c in fig.axes[1].lines if len(c.get_xdata()) > 10][0]
    d = np.asarray(cara.get_xdata()) * 1e-9
    df = np.asarray(cara.get_ydata())
    krok = d[1] - d[0]
    check("Minimum Δf(d) v grafu sedí s d_minima_frequency_shift",
          abs(d[np.argmin(df)] - d_min) < 3 * krok,
          f"graf {d[np.argmin(df)] * 1e9:.3f} nm, výpočet {d_min * 1e9:.3f} nm")
    check("Δf(d) prochází pracovním bodem",
          abs(np.interp(r["d_set"], d, df) - r["df_set"]) < 1e-3 * abs(df).max(),
          f"Δf(d_set) = {np.interp(r['d_set'], d, df):.4f} Hz, df_set = {r['df_set']:.4f} Hz")
    plt.close(fig)

    # --- fáze podél skenu: stejný vzorec jako phase_shift (Cesta A) -------
    from afm_sim.phase_shift import resonance_phase
    from afm_sim.plotting import fig_rezonance_ve_skenu
    Q = 5000.0
    _, faze0 = vypocet_afm.odezva_pri_buzeni(0.0, pa["f0"], Q)
    check("Bez posunu rezonance je fáze při buzení na f0 přesně -90°",
          abs(faze0 + 90.0) < 1e-9, f"φ = {float(faze0):.6f}°")
    prubeh = vypocet_afm.faze_podel_skenu(r, Q)
    res = r["fwd"]
    rozdily = []
    for k in (len(res.d) // 10, len(res.d) // 2, 9 * len(res.d) // 10):
        ref = np.degrees(resonance_phase(res.d[k], pa["A"], pa["k_cant"], pa["f0"], Q,
                                         r["force_ref"]))
        rozdily.append(abs(prubeh["faze"][k] - ref))
    check("Fáze podél skenu sedí s phase_shift.resonance_phase ve 3 bodech",
          max(rozdily) < 0.05, f"max rozdíl {max(rozdily):.4f}°")
    check("Šum Δf se promítne do fáze (zašuměná fáze se liší)",
          np.std(prubeh["faze_meas"] - prubeh["faze"]) > 0.1,
          f"std rozdílu {np.std(prubeh['faze_meas'] - prubeh['faze']):.2f}°")
    fig = fig_rezonance_ve_skenu(
        pa["f0"], Q, prubeh, len(prubeh["x"]) // 2,
        lambda df, fd: vypocet_afm.odezva_pri_buzeni(df, pa["f0"], Q, fd))
    check("Graf rezonance ve skenu se sestaví", len(fig.axes) >= 3,
          f"{len(fig.axes)} os")
    plt.close(fig)

    # --- pohybová rovnice vs. vzorec 17.15 -------------------------------
    from afm_sim.frequency_shift import frequency_shift
    from afm_sim.pohybova_rovnice import df_z_pohybove_rovnice
    nula = df_z_pohybove_rovnice(1.0e-9, pa["A"], pa["k_cant"], pa["f0"], lambda x: 0.0 * x)
    check("Bez síly dá pohybová rovnice Δf = 0", abs(nula) < 1e-9, f"Δf = {nula:.2e} Hz")
    d_test = np.array([1.02 * d_min, 0.8e-9, 1.0e-9, 1.3e-9])
    df_num = df_z_pohybove_rovnice(d_test, pa["A"], pa["k_cant"], pa["f0"], r["force_ref"])
    df_vz = np.array([frequency_shift(x, pa["A"], pa["k_cant"], pa["f0"], r["force_ref"])
                      for x in d_test])
    rel = np.max(np.abs(df_num / df_vz - 1))
    check("Δf z pohybové rovnice sedí se vzorcem 17.15 (< 1 %) ve 4 vzdálenostech",
          rel < 0.01, f"max rel. rozdíl {rel:.2e}")
    ra = vypocet_afm.spust(surface="atoms-AFM")
    x = np.array([0.8e-9, 1.0e-9])
    rel_a = np.max(np.abs(df_z_pohybove_rovnice(x, pa["A"], pa["k_cant"], pa["f0"],
                                                 ra["force_ref"])
                          / np.array([frequency_shift(xi, pa["A"], pa["k_cant"], pa["f0"],
                                                      ra["force_ref"]) for xi in x]) - 1))
    check("Totéž pro síly bodových atomů (atoms-AFM)", rel_a < 0.01,
          f"max rel. rozdíl {rel_a:.2e}")

    print()
    print("VŠECHNY KONTROLY PROŠLY" if all(vysledky)
          else f"SELHALO {vysledky.count(False)} z {len(vysledky)}")
    return 0 if all(vysledky) else 1


if __name__ == "__main__":
    sys.exit(main())
