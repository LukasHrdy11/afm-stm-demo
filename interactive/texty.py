"""Texty uživatelského rozhraní ve dvou jazycích (čeština / angličtina).

Všechno, co vidí uživatel dashboardu (popisky ovladačů, tlačítka, hlášky,
nápověda k parametrům, náměty pro výuku), je tady - widgety samy žádný
text nedrží. Kód, docstringy a výpisy testů zůstávají česky (konvence
repa); překládá se jen UI.

Popisky grafů jsou zvlášť v stm_sim/plotting.py a afm_sim/plotting.py,
protože ty moduly používají i dávkové skripty a nesmí záviset na
interactive/ (směr závislostí je jen interactive -> stm_sim/afm_sim).

Pravidlo: každý klíč má OBA jazyky a žádný není prázdný - hlídá to
tests/test_texty.py. Výchozí jazyk je čeština, popisky v ní se nesmí
měnit bez úpravy tests/test_interactive.py (ten hledá ovladače podle nich).
"""

JAZYKY = ("cs", "en")
VYCHOZI_JAZYK = "cs"

# ------------------------------ obecné texty --------------------------------
# klíč -> (česky, anglicky). Texty smí obsahovat {pojmenované} pole pro format.
_T = {
    # dashboard
    "dash.jazyk": ("Jazyk / Language:", "Language / Jazyk:"),
    "dash.tab_stm": ("STM", "STM"),
    "dash.tab_afm": ("FM-AFM", "FM-AFM"),
    "dash.tab_komb": ("STM + AFM", "STM + AFM"),
    "dash.namety": ("Náměty, co studentům ukázat", "Ideas for the classroom"),
    "dash.uvod": (
        "Simulace zpětnovazební smyčky tunelového mikroskopu (STM) a "
        "frekvenčně modulovaného AFM. Každá změna ovladače přepočítá "
        "simulaci a překreslí grafy. Najetím myši na ovladač se zobrazí "
        "jeho význam; přehled všech parametrů je v „Legendě parametrů“ "
        "pod každým panelem.",
        "Simulation of the feedback loop of a scanning tunnelling microscope "
        "(STM) and a frequency-modulation AFM. Every change of a control "
        "re-runs the simulation and redraws the plots. Hover over a control "
        "to see what it means; all parameters are summarised in the "
        "“Parameter legend” below each panel."),

    "dash.namety_html": (
        "<ol>"
        "<li><b>Co dělá regulátor (demystifikace).</b> V STM panelu klikni na "
        "„Načíst kroky“ a posouvej „Krok“. Vypíše se každý mezikrok smyčky: "
        "změřený proud → log-chyba e = ln(I/I_set) → příkaz regulátoru → nová "
        "poloha hrotu. Regulátor neví, kde povrch je - ví jen, jestli je proud "
        "větší nebo menší, než má být.</li>"
        "<li><b>Zpětná vazba zapnutá vs. vypnutá.</b> Odškrtni „zpětná vazba "
        "zapnutá“. Hrot přestane uhýbat a topografie se promítne rovnou do "
        "proudu (režim konstantní výšky). Stáhni „z_hrot“ pod výšku hrany: hrot "
        "do ní narazí, protože ho nemá co zvednout. Totéž jde v AFM panelu - "
        "tam se topografie promítne do Δf. Pro srovnání v jednom grafu nejdřív "
        "se zapnutou smyčkou klikni na „Zamknout křivku“, pak smyčku vypni.</li>"
        "<li><b>Kdy je šum neúnosný.</b> „Míra šumu“ je násobek skutečně "
        "změřeného šumu. Při 1× je šum jednotky pm proti rezervě stovek pm. "
        "Zvyšuj a sleduj, kdy regulátor ztrácí stopu povrchu a kdy rezerva do "
        "nárazu spadne k nule.</li>"
        "<li><b>P vs. I vs. PI.</b> Klikni „Zamknout křivku“, přepni regulátor "
        "a porovnej v jednom grafu. Samotná P-složka má jiný efekt než "
        "přeškálování zesílení jen při T_sys &gt; 0.</li>"
        "<li><b>Co je Δf.</b> V AFM panelu posuň „poloha ve skenu“ nad atom a "
        "sleduj, jak se celá rezonanční křivka posune proti volnému "
        "cantileveru. Δf není měřená veličina - je to posun celé rezonance, "
        "ze kterého se teprve odečítá.</li>"
        "<li><b>Ztráta stability u AFM.</b> Přepni citlivost na „local“ a "
        "povrch na atoms. Jakmile se hrot dostane za minimum Δf(d), citlivost "
        "změní znaménko a smyčka reguluje opačně. Je to očekávaný jev, ne "
        "chyba simulace.</li>"
        "<li><b>Proč STM vůbec funguje.</b> Záložka „Proud vs. mezera I(g)“: "
        "proud klesá 10× na každých ~0,17 nm, v log. ose je to přímka se sklonem "
        "-2κ. Oranžový pás je rozsah mezery během skenu - smyčka ho drží v "
        "pikometrech. Po „Načíst kroky“ ukazuje hvězdička polohu hrotu "
        "v zobrazeném kroku. Šedá čára je literaturová κ proti změřené.</li>"
        "<li><b>Proč je pracovní bod AFM choulostivý.</b> Záložka „Síla a Δf vs. "
        "vzdálenost“: Δf(d) má minimum; blíž ke vzorku smyčka reguluje opačně. "
        "Výřez ukazuje, jak malé je Δf v pracovním bodě proti pásu šumu - posuň "
        "d_set a sleduj, kdy kontrast zmizí v šumu.</li>"
        "<li><b>Fáze při sledování povrchu.</b> Pod AFM grafy posouvej „poloha "
        "ve skenu“ (nebo ▶): rezonance se nad atomy posouvá a fáze při buzení "
        "na f0 se mění o jednotky stupňů; oranžově se šumem Δf. Zmenši Q a "
        "sleduj, jak citlivost fáze klesne.</li>"
        "<li><b>Odkud se bere Δf.</b> Záložka „Pohybová rovnice vs. Δf“: "
        "frekvence spočítaná přímo z kmitu hrotu v poli síly sedí se vzorcem "
        "17.15 na setiny procenta. Síla působí jen u dolního bodu obratu.</li>"
        "<li><b>STM a AFM zároveň.</b> Záložka „STM + AFM“: jeden kmitající "
        "vodivý hrot. Přepni zpětnou vazbu mezi proudem a Δf a porovnej, jak "
        "stejný povrch vidí pasivní kanál. Bez zpětné vazby vidíš oba kontrasty "
        "najednou.</li>"
        "</ol>",
        "<ol>"
        "<li><b>What the controller does.</b> In the STM panel click “Load "
        "steps” and move “Step”. Every intermediate step of the loop is shown: "
        "measured current → log error e = ln(I/I_set) → controller command → "
        "new tip position. The controller does not know where the surface is - "
        "it only knows whether the current is larger or smaller than it should "
        "be.</li>"
        "<li><b>Feedback on vs. off.</b> Untick “feedback on”. The tip stops "
        "moving and the topography shows up directly in the current "
        "(constant-height mode). Lower “z_tip” below the edge height: the tip "
        "crashes, because nothing lifts it. The same works in the AFM panel, "
        "where the topography shows up in Δf. To compare both in one plot, "
        "first click “Lock curve” with the loop on, then switch it off.</li>"
        "<li><b>When the noise becomes too much.</b> “Noise level” is a "
        "multiple of the actually measured noise. At 1× the noise is a few pm "
        "against a margin of hundreds of pm. Increase it and watch when the "
        "controller loses track of the surface and when the margin to a crash "
        "drops to zero.</li>"
        "<li><b>P vs. I vs. PI.</b> Click “Lock curve”, switch the controller "
        "and compare in one plot. The P part has an effect different from "
        "just rescaling the gain only when T_sys &gt; 0.</li>"
        "<li><b>What Δf is.</b> In the AFM panel move “scan position” above an "
        "atom and watch the whole resonance curve shift against the free "
        "cantilever. Δf is not measured directly - it is the shift of the "
        "whole resonance from which it is read off.</li>"
        "<li><b>Loss of stability in AFM.</b> Set the sensitivity to “local” "
        "and the surface to atoms. Once the tip gets past the minimum of "
        "Δf(d), the sensitivity changes sign and the loop regulates the wrong "
        "way. This is expected behaviour, not a bug of the simulation.</li>"
        "<li><b>Why STM works at all.</b> Tab “Current vs. gap I(g)”: the "
        "current drops 10× every ~0.17 nm, on a log axis it is a line with "
        "slope -2κ. The orange band is the gap range during the scan - the loop "
        "keeps it within picometres. After “Load steps” the star shows the tip "
        "in the displayed step. The grey line is the literature κ against the "
        "measured one.</li>"
        "<li><b>Why the AFM working point is delicate.</b> Tab “Force and Δf "
        "vs. distance”: Δf(d) has a minimum; closer to the sample the loop "
        "regulates the wrong way. The zoom shows how small Δf is at the working "
        "point compared to the noise band - move d_set and watch when the "
        "contrast disappears in the noise.</li>"
        "<li><b>Phase while tracking the surface.</b> Below the AFM plots move "
        "“scan position” (or ▶): the resonance shifts above the atoms and the "
        "phase at the drive frequency f0 changes by a few degrees; orange with "
        "the Δf noise. Lower Q and watch the phase sensitivity drop.</li>"
        "<li><b>Where Δf comes from.</b> Tab “Equation of motion vs. Δf”: the "
        "frequency computed directly from the tip oscillation in the force "
        "field matches formula 17.15 to a hundredth of a percent. The force "
        "acts only near the lower turning point.</li>"
        "<li><b>STM and AFM at once.</b> Tab “STM + AFM”: one oscillating "
        "conducting tip. Switch the feedback between the current and Δf and "
        "compare how the passive channel sees the same surface. Without "
        "feedback you see both contrasts at once.</li>"
        "</ol>"),

    # společné pro panely
    "p.prepocitat": ("Přepočítat", "Recompute"),
    "p.zamknout": ("Zamknout křivku", "Lock curve"),
    "p.zamknout_tip": (
        "Uloží aktuální průběh jako šedé pozadí pro porovnání s dalším během",
        "Keeps the current run as a grey background curve to compare with "
        "the next run"),
    "p.uvolnit": ("Uvolnit", "Release"),
    "p.legenda": ("Legenda parametrů", "Parameter legend"),
    "p.leg_parametr": ("Parametr", "Parameter"),
    "p.leg_vyznam": ("Význam", "Meaning"),
    "p.leg_zdroj": ("Původ hodnoty", "Origin of the value"),
    "p.geometrie": ("Geometrie povrchu", "Surface geometry"),
    "p.tab_prubehy": ("Průběhy skenu", "Scan traces"),
    "stm.tab_Iz": ("Proud vs. mezera I(g)", "Current vs. gap I(g)"),
    "afm.tab_eom": ("Pohybová rovnice vs. Δf", "Equation of motion vs. Δf"),
    "afm.eom_popis": (
        "Odkud se bere Δf: v FM módu kmitá cantilever na své vlastní frekvenci "
        "a PLL ji jen měří. Body jsou frekvence spočítaná přímo z pohybové "
        "rovnice kmitu v poli síly (průchody nulou), čára je vzorec 17.15, "
        "který sílu jen váženě průměruje přes kmit. {rozdil}",
        "Where Δf comes from: in FM mode the cantilever oscillates at its own "
        "frequency and the PLL only measures it. The points are the frequency "
        "computed directly from the equation of motion in the force field "
        "(zero crossings), the line is formula 17.15, which only averages the "
        "force over the oscillation with a weight. {rozdil}"),
    "afm.eom_rozdil": ("V d_set: rovnice {num:+.4f} Hz, vzorec {vz:+.4f} Hz "
                       "(rozdíl {rel:.2g} %).",
                       "At d_set: equation {num:+.4f} Hz, formula {vz:+.4f} Hz "
                       "(difference {rel:.2g} %)."),
    "afm.tab_dfd": ("Síla a Δf vs. vzdálenost", "Force and Δf vs. distance"),
    "p.tab_schema": ("Schéma smyčky", "Loop diagram"),
    "p.referencni": ("referenční běh", "reference run"),
    "p.neprekreslil": ("Graf se nepřekreslil, oprav nastavení výše.",
                       "The plot was not redrawn, fix the settings above."),
    "p.radku_s": ("≈ {radku:.2f} řádku/s (tam i zpět přes {delka:.1f} nm)",
                  "≈ {radku:.2f} lines/s (forward + backward over {delka:.1f} nm)"),

    # STM panel
    "stm.nadpis": ("STM: zpětná vazba v režimu konstantního proudu",
                   "STM: feedback in constant-current mode"),
    "stm.naraz": ("<b style='color:#b00'>NÁRAZ</b> v x = {x:.3f} nm - model za "
                  "nárazem neplatí.",
                  "<b style='color:#b00'>CRASH</b> at x = {x:.3f} nm - the model "
                  "is not valid beyond the crash."),
    "stm.ok": ("Bez nárazu. Nejmenší mezera {g:.4f} nm, rezerva do nárazu "
               "<b style='color:{barva}'>{rezerva:.0f} pm</b>.",
               "No crash. Smallest gap {g:.4f} nm, margin to crash "
               "<b style='color:{barva}'>{rezerva:.0f} pm</b>."),
    "stm.gset_pod_kontaktem": (
        "<b style='color:#b00'>g_set musí být větší než g_contact</b> - "
        "hrot by startoval už v kontaktu.",
        "<b style='color:#b00'>g_set must be larger than g_contact</b> - the "
        "tip would start in contact."),
    "stm.titulek": ("{reg}, {povrch}, T_sys = {tsys:.0f} µs",
                    "{reg}, {povrch}, T_sys = {tsys:.0f} µs"),
    "stm.titulek_ch": ("{povrch}, bez zpětné vazby", "{povrch}, feedback off"),
    "stm.krokovani": ("Krokování smyčky", "Stepping through the loop"),
    "stm.krokovani_popis": (
        "Jeden krok simulace: změř proud → spočti log-chybu → regulátor z ní "
        "udělá příkaz → akční člen posune hrot. Nic jiného smyčka nedělá.",
        "One simulation step: measure the current → compute the log error → "
        "the controller turns it into a command → the actuator moves the tip. "
        "That is all the loop does."),
    "stm.nacti_kroky": ("Načíst kroky", "Load steps"),
    "stm.nacti_kroky_tip": (
        "Spustí simulaci s krokováním a nabídne listování mezikroky smyčky",
        "Runs the simulation with stepping and lets you browse the "
        "intermediate steps of the loop"),
    "stm.nejdriv_kroky": ("Nejdřív klikni na „Načíst kroky“.",
                          "Click “Load steps” first."),
    "stm.krok_z": ("--- krok {i} z {n} (rovnoměrně přes celý sken) ---",
                   "--- step {i} of {n} (evenly spread over the scan) ---"),

    # rozpis kroku (vypocet_stm.popis_kroku)
    "krok.povrch": ("h (povrch)", "h (surface)"),
    "krok.mezera": ("g (mezera)", "g (gap)"),
    "krok.I": ("1) I skutečný  ", "1) I true      "),
    "krok.Imer": ("   I měřený    ", "   I measured  "),
    "krok.Imer_pozn": ("(+ šum; regulátor vidí tohle)",
                       "(+ noise; this is what the controller sees)"),
    "krok.naraz": ("3) NÁRAZ - smyčka se zastavila, model za nárazem neplatí.",
                   "3) CRASH - the loop stopped, the model is not valid beyond it."),
    "krok.y": ("3) y = regulátor(e)", "3) y = controller(e)"),
    "krok.y_pozn": ("(příkaz, ne poloha)", "(a command, not a position)"),
    "krok.z": ("4) z_hrot = akční člen(y)", "4) z_tip = actuator(y)"),

    # AFM panel
    "afm.nadpis": ("FM-AFM: zpětná vazba na konstantní Δf",
                   "FM-AFM: feedback on constant Δf"),
    "afm.naraz": ("<b style='color:#b00'>NÁRAZ</b> v x = {x:.3f} nm.",
                  "<b style='color:#b00'>CRASH</b> at x = {x:.3f} nm."),
    "afm.nestabilita": (
        "<b style='color:#b00'>ZTRÁTA STABILITY</b> - hrot se dostal za "
        "minimum Δf(d), citlivost změnila znaménko a smyčka reguluje opačně. "
        "U režimu „local“ je to očekávaný jev, ne chyba.",
        "<b style='color:#b00'>LOSS OF STABILITY</b> - the tip went past the "
        "minimum of Δf(d), the sensitivity changed sign and the loop now "
        "regulates the wrong way. In the “local” mode this is the expected "
        "behaviour, not a bug."),
    "afm.ok": ("Bez nárazu i nestability. Nejmenší d = {d:.4f} nm, rezerva "
               "<b style='color:{barva}'>{rezerva:.0f} pm</b>, "
               "Δf setpoint = {df:.3f} Hz.",
               "No crash, no instability. Smallest d = {d:.4f} nm, margin "
               "<b style='color:{barva}'>{rezerva:.0f} pm</b>, "
               "Δf setpoint = {df:.3f} Hz."),
    "afm.chyba_dset": (
        "Pracovní bod d_set = {d_set:.3f} nm musí ležet ZA minimem Δf(d) "
        "(to je na {d_min:.3f} nm). Blíž ke vzorku je citlivost záporná a "
        "smyčka by regulovala opačně - posuň d_set dál od vzorku.",
        "The working point d_set = {d_set:.3f} nm must lie BEYOND the minimum "
        "of Δf(d) (which is at {d_min:.3f} nm). Closer to the sample the "
        "sensitivity is negative and the loop would regulate the wrong way - "
        "move d_set further from the sample."),
    "afm.titulek": ("{reg}, {povrch}, citlivost {mode}",
                    "{reg}, {povrch}, sensitivity {mode}"),
    "afm.titulek_ch": ("{povrch}, bez zpětné vazby", "{povrch}, feedback off"),
    "afm.nekalibrovano": (
        "Parametry hrotu (U0, Ra, K_P) nejsou kalibrované - jde o ilustrativní "
        "hodnoty typického qPlus senzoru; změřený je jen šum.",
        "Tip parameters (U0, Ra, K_P) are not calibrated - they are "
        "illustrative values of a typical qPlus sensor; only the noise is "
        "measured."),
    "afm.co_je_df": ("Co je vlastně Δf", "What Δf actually is"),
    "afm.rez_popis": (
        "Rezonanční křivka v bodě skenu, který vybereš posuvníkem (▶ přehraje "
        "celý sken). Cantilever se budí na volné rezonanci f0; nad povrchem se "
        "rezonance posune o Δf(x) a změní se fáze odezvy - modrá bez šumu, "
        "oranžová se změřeným šumem Δf. Posun je malý proti šířce rezonance "
        "f0/Q, proto je fáze tak citlivá. Ve FM módu (tahle simulace) PLL "
        "fázi drží zamčenou a informaci nese Δf; fáze zde ukazuje, co by "
        "změřila AM detekce při stejném posunu rezonance.",
        "Resonance curve at the scan position chosen with the slider (▶ plays "
        "the whole scan). The cantilever is driven at the free resonance f0; "
        "above the surface the resonance shifts by Δf(x) and the phase of the "
        "response changes - blue without noise, orange with the measured Δf "
        "noise. The shift is small compared to the resonance width f0/Q, which "
        "is why the phase is so sensitive. In FM mode (this simulation) the PLL "
        "keeps the phase locked and Δf carries the information; the phase here "
        "shows what AM detection would measure for the same resonance shift."),
    "afm.co_je_df_popis": (
        "Δf není měřená veličina - je to posun rezonance cantileveru, když na "
        "hrot začne působit síla od vzorku.",
        "Δf is not measured directly - it is the shift of the cantilever "
        "resonance caused by the tip-sample force."),
    "afm.fixed": ("fixed (z pracovního bodu)", "fixed (from the working point)"),
    "afm.local": ("local (přepočítává se)", "local (recomputed each step)"),
    "afm.pevne": ("d_set (pevné) [nm]:", "d_set (fixed) [nm]:"),

    # kombinovaný STM + AFM panel
    "kmb.nadpis": ("STM + AFM: jeden vodivý qPlus hrot, dva kanály",
                   "STM + AFM: one conducting qPlus tip, two channels"),
    "kmb.popis": (
        "Hrot kmitá (FM-AFM) a zároveň jím teče tunelový proud. Smyčka umí "
        "držet jen jeden signál - druhý se zaznamenává pasivně a ukazuje, jak "
        "na tentýž povrch reaguje jiný kontrastní mechanismus. Proud je "
        "středovaný přes kmit (teče hlavně v dolním bodě obratu). Parametry "
        "hrotu (síla) jsou ilustrativní, parametry proudu z reálného STM.",
        "The tip oscillates (FM-AFM) and a tunnelling current flows through it "
        "at the same time. The loop can keep only one signal constant - the "
        "other is recorded passively and shows how a different contrast "
        "mechanism sees the same surface. The current is averaged over the "
        "oscillation (it flows mostly at the lower turning point). The tip "
        "(force) parameters are illustrative, the current parameters come from "
        "the real STM."),
    "kmb.rezim_I": ("zpětná vazba na proud I", "feedback on current I"),
    "kmb.rezim_df": ("zpětná vazba na Δf", "feedback on Δf"),
    "kmb.rezim_vyp": ("bez zpětné vazby (konst. výška)", "no feedback (constant height)"),
    "kmb.ok": ("Bez nárazu. Nejmenší d = {d:.4f} nm, rezerva "
               "<b style='color:{barva}'>{rezerva:.0f} pm</b>; I_set = {I:.0f} pA, "
               "Δf_set = {df:.3f} Hz (oba v d_set).",
               "No crash. Smallest d = {d:.4f} nm, margin "
               "<b style='color:{barva}'>{rezerva:.0f} pm</b>; I_set = {I:.0f} pA, "
               "Δf_set = {df:.3f} Hz (both at d_set)."),
    "kmb.titulek": ("{rezim}, {reg}, {povrch}", "{rezim}, {reg}, {povrch}"),

    # volby dropdownů
    "v.bez_mezery": ("bez šumu mezery", "no gap noise"),
    "v.stojici": ("stojící hrot", "standing tip"),
    "v.skeny": ("ze skenů (nejhorší)", "from scans (worst case)"),
    "v.preset_realny": ("Reálný přístroj (změřené hodnoty)",
                        "Real instrument (measured values)"),
    "v.preset_ideal": ("Učebnicový ideál (bez šumu)",
                       "Textbook ideal (no noise)"),
    "v.preset_qplus": ("Typický qPlus", "Typical qPlus"),
}

# ------------------------------ původ hodnot -------------------------------
# Kategorie z measured.py - UI je musí držet oddělené (co je měření a co ne).
ZDROJE = {
    "zmereno": ("změřeno na přístroji", "measured on the instrument"),
    "nastaveno": ("nastavení při měření", "setting used in the measurement"),
    "literatura": ("odhad z literatury", "literature estimate"),
    "nekalibrovano": ("nekalibrováno, ilustrativní", "not calibrated, illustrative"),
    "volba": ("volba pro demonstraci", "chosen for the demonstration"),
    "ovladani": ("ovládání simulace", "simulation control"),
}

# ------------------------------ parametry ----------------------------------
# klíč -> (popisek cs, popisek en, význam cs, význam en, zdroj)
# Popisky v češtině jsou zároveň hodnoty `description` widgetů, podle kterých
# je hledá tests/test_interactive.py - neměnit bez úpravy testu.
PARAMETRY = {
    # ---------------------------------- STM ----------------------------------
    "stm.preset": (
        "Preset:", "Preset:",
        "Nastaví všechny parametry naráz: reálný přístroj (změřené hodnoty) "
        "nebo učebnicový ideál (bez šumu, okamžitý akční člen).",
        "Sets all parameters at once: the real instrument (measured values) "
        "or a textbook ideal (no noise, instantaneous actuator).",
        "ovladani"),
    "stm.controller": (
        "Regulátor:", "Controller:",
        "P: příkaz úměrný chybě (zůstává trvalá odchylka). I: integruje chybu, "
        "hrot se zastaví až při nulové chybě. PI: obojí.",
        "P: command proportional to the error (leaves a steady-state offset). "
        "I: integrates the error, the tip stops only at zero error. PI: both.",
        "ovladani"),
    "stm.surface": (
        "Povrch:", "Surface:",
        "step: ostrý schod výšky H; ramp: schod s konečnou šířkou hrany w; "
        "MGE: chaotické terasy (Mackey-Glassova rovnice); atoms: řada atomů.",
        "step: sharp step of height H; ramp: step with a finite edge width w; "
        "MGE: chaotic terraces (Mackey-Glass equation); atoms: a row of atoms.",
        "volba"),
    "stm.T_SYS": (
        "T_sys [µs]:", "T_sys [µs]:",
        "Setrvačnost akčního členu (pieza): za jak dlouho hrot dožene příkaz "
        "regulátoru. 0 = okamžitě.",
        "Lag of the actuator (piezo): how long the tip needs to follow the "
        "controller command. 0 = instantaneous.",
        "nastaveno"),
    "stm.tau": (
        "tau [µs]:", "tau [µs]:",
        "Časová konstanta I-složky: za jak dlouho smyčka vyrovná skok mezery "
        "(zesílení K_I = 1/(2·kappa·tau)).",
        "Time constant of the I part: how fast the loop corrects a step in "
        "the gap (gain K_I = 1/(2·kappa·tau)).",
        "nastaveno"),
    "stm.v": (
        "v [nm/s]:", "v [nm/s]:",
        "Rychlost pojezdu hrotu podél x.",
        "Speed of the tip along x.",
        "nastaveno"),
    "stm.K_P": (
        "K_P [nm]:", "K_P [nm]:",
        "Proporcionální zesílení: o kolik se hrot okamžitě posune na jednotku "
        "log-chyby. Hodnota z hlavičky .sxm.",
        "Proportional gain: how far the tip moves instantly per unit of log "
        "error. Value taken from the .sxm header.",
        "zmereno"),
    "stm.I_set": (
        "I_set [pA]:", "I_set [pA]:",
        "Setpoint proudu - proud, který smyčka drží.",
        "Current setpoint - the current the loop keeps constant.",
        "nastaveno"),
    "stm.g_set": (
        "g_set [nm]:", "g_set [nm]:",
        "Mezera hrot-vzorek, při které teče I_set. Dynamika smyčky na ní "
        "nezávisí (chyba e = ln(I/I_set) ji vykrátí), mění jen rezervu do nárazu.",
        "Tip-sample gap at which I_set flows. The loop dynamics do not depend "
        "on it (the error e = ln(I/I_set) cancels it), it only sets the margin "
        "to a crash.",
        "literatura"),
    "stm.g_contact": (
        "g_contact [nm]:", "g_contact [nm]:",
        "Mezera, při které se hlásí náraz hrotu do vzorku.",
        "Gap at which a tip crash is reported.",
        "literatura"),
    "stm.kappa": (
        "kappa [1/nm]", "kappa [1/nm]",
        "Rozpadová konstanta tunelového proudu, I ~ exp(-2·kappa·g). Změřeno "
        "ze závislosti proudu na Z (6,8 /nm), literatura uvádí ~10 /nm. Mění "
        "ji preset.",
        "Decay constant of the tunnelling current, I ~ exp(-2·kappa·g). "
        "Measured from the current-vs-Z curve (6.8 /nm), the literature gives "
        "~10 /nm. Set by the preset.",
        "zmereno"),
    "stm.mera_sumu": (
        "Míra šumu [x]:", "Noise level [×]:",
        "Násobek změřené velikosti šumu. 0 = bez šumu, 1 = jako na přístroji. "
        "Zvyšuj a sleduj, kdy regulátor ztratí stopu povrchu.",
        "Multiple of the measured noise. 0 = no noise, 1 = as on the "
        "instrument. Increase it and watch when the controller loses track of "
        "the surface.",
        "zmereno"),
    "stm.z_fixed": (
        "z_hrot [nm]:", "z_tip [nm]:",
        "Pevná výška hrotu v režimu konstantní výšky (jen s vypnutou zpětnou "
        "vazbou). Pod výškou hrany hrot narazí.",
        "Fixed tip height in constant-height mode (only with the feedback "
        "off). Below the edge height the tip crashes.",
        "volba"),
    "stm.sum_proudu": (
        "šum proudu", "current noise",
        "Šum předzesilovače přičtený k měřenému proudu (σ = 2,83 pA, pásmo "
        "7 kHz). Regulátor vidí zašuměný proud, skutečný proud se nemění.",
        "Preamplifier noise added to the measured current (σ = 2.83 pA, "
        "7 kHz bandwidth). The controller sees the noisy current, the true "
        "current is unchanged.",
        "zmereno"),
    "stm.sum_cary": (
        "+ čáry 312/623 Hz", "+ 312/623 Hz lines",
        "Přidá k šumu proudu dvě změřené spektrální čáry (rušení).",
        "Adds two measured spectral lines (interference) to the current noise.",
        "zmereno"),
    "stm.sum_mezery": (
        "Šum mezery:", "Gap noise:",
        "Mechanický šum vzdálenosti hrot-vzorek: ze stojícího hrotu (horní "
        "odhad) nebo ze skenů (nejhorší varianta, spektrum 1/f).",
        "Mechanical noise of the tip-sample distance: from a standing tip "
        "(upper estimate) or from scans (worst case, 1/f spectrum).",
        "zmereno"),
    "stm.backward": (
        "zpětný průjezd", "backward scan",
        "Po průjezdu tam jede hrot stejnou linkou zpět, smyčka běží bez "
        "přerušení - rozdíl tam/zpět ukazuje zpoždění regulace.",
        "After the forward pass the tip returns along the same line with the "
        "loop still running - the forward/backward difference shows the lag "
        "of the regulation.",
        "ovladani"),
    "stm.zpetna_vazba": (
        "zpětná vazba zapnutá", "feedback on",
        "Vypnutím se přejde do režimu konstantní výšky: hrot stojí a "
        "topografie se promítne přímo do proudu.",
        "Switching it off gives the constant-height mode: the tip stays put "
        "and the topography shows up directly in the current.",
        "ovladani"),
    "stm.H": (
        "H [nm]:", "H [nm]:",
        "Výška schodu (u MGE největší výška terasy).",
        "Step height (for MGE the largest terrace height).",
        "volba"),
    "stm.w": (
        "w [nm]:", "w [nm]:",
        "Šířka hrany schodu (lineární náběh). Pro w → 0 přejde v ostrý schod.",
        "Width of the step edge (linear ramp). For w → 0 it becomes a sharp "
        "step.",
        "volba"),
    "stm.x_edge": (
        "x_hrany [nm]:", "x_edge [nm]:",
        "Poloha hrany (u MGE začátek teras, u atomů první atom).",
        "Position of the edge (for MGE the start of the terraces, for atoms "
        "the first atom).",
        "volba"),
    "stm.atoms_H": (
        "výška atomů [nm]:", "atom height [nm]:",
        "Výška jednoho atomu (gaussovský hrbol).",
        "Height of a single atom (Gaussian bump).",
        "volba"),
    "stm.atoms_spacing": (
        "rozestup [nm]:", "spacing [nm]:",
        "Vzdálenost sousedních atomů.",
        "Distance between neighbouring atoms.",
        "volba"),
    "stm.atoms_sigma": (
        "šířka σ [nm]:", "width σ [nm]:",
        "Šířka atomu (směrodatná odchylka gaussovky).",
        "Width of an atom (standard deviation of the Gaussian).",
        "volba"),
    "stm.atoms_pocet": (
        "počet atomů:", "number of atoms:",
        "Kolik atomů leží v řadě.",
        "How many atoms are in the row.",
        "volba"),
    "stm.mge_pocet": (
        "počet teras:", "number of terraces:",
        "Kolik schodů (teras) má chaotický povrch.",
        "How many steps (terraces) the chaotic surface has.",
        "volba"),
    "stm.mge_rozestup": (
        "rozestup teras [nm]:", "terrace spacing [nm]:",
        "Vzdálenost mezi schody chaotického povrchu.",
        "Distance between the steps of the chaotic surface.",
        "volba"),
    "stm.krok": (
        "Krok:", "Step:",
        "Který mezikrok smyčky se vypíše (rovnoměrně přes celý sken).",
        "Which intermediate step of the loop is shown (evenly spread over "
        "the scan).",
        "ovladani"),

    # ---------------------------------- AFM ----------------------------------
    "afm.preset": (
        "Preset:", "Preset:",
        "Nastaví všechny parametry naráz: typický qPlus senzor (šum "
        "změřený, parametry hrotu ilustrativní) nebo učebnicový ideál.",
        "Sets all parameters at once: a typical qPlus sensor (measured "
        "noise, illustrative tip parameters) or a textbook ideal.",
        "ovladani"),
    "afm.controller": (
        "Regulátor:", "Controller:",
        "P / I / PI regulátor na chybu e = Δf_set - Δf.",
        "P / I / PI controller acting on the error e = Δf_set - Δf.",
        "ovladani"),
    "afm.surface": (
        "Povrch:", "Surface:",
        "step / ramp / atoms: výška povrchu h(x) a Lennard-Jonesova síla "
        "podle vzdálenosti. atoms-AFM: řada BODOVÝCH atomů - síly se sčítají "
        "ve 3D, hrot atom cítí i mimo pozici nad ním.",
        "step / ramp / atoms: surface height h(x) and a Lennard-Jones force "
        "depending on the distance. atoms-AFM: a row of POINT atoms - the "
        "forces are summed in 3D, so the tip feels an atom even when it is "
        "not directly above it.",
        "volba"),
    "afm.gain_mode": (
        "Citlivost:", "Sensitivity:",
        "fixed: zesílení z citlivosti dΔf/dd v pracovním bodě. local: "
        "citlivost se přepočítává v každém kroku a smyčka umí ohlásit ztrátu "
        "stability (za minimem Δf(d)).",
        "fixed: gain from the sensitivity dΔf/dd at the working point. local: "
        "the sensitivity is recomputed each step and the loop can report a "
        "loss of stability (beyond the minimum of Δf(d)).",
        "ovladani"),
    "afm.d_set": (
        "d_set [nm]:", "d_set [nm]:",
        "Pracovní vzdálenost hrot-vzorek (střední poloha kmitu). Musí ležet "
        "dál od vzorku než minimum Δf(d).",
        "Working tip-sample distance (centre of the oscillation). It must lie "
        "further from the sample than the minimum of Δf(d).",
        "volba"),
    "afm.A": (
        "A [nm]:", "A [nm]:",
        "Amplituda kmitu cantileveru.",
        "Oscillation amplitude of the cantilever.",
        "literatura"),
    "afm.tau": (
        "tau [ms]:", "tau [ms]:",
        "Časová konstanta I-složky regulátoru.",
        "Time constant of the I part of the controller.",
        "volba"),
    "afm.T_SYS": (
        "T_sys [µs]:", "T_sys [µs]:",
        "Setrvačnost akčního členu (pieza). 0 = okamžitě.",
        "Lag of the actuator (piezo). 0 = instantaneous.",
        "volba"),
    "afm.v": (
        "v [nm/s]:", "v [nm/s]:",
        "Rychlost pojezdu hrotu podél x.",
        "Speed of the tip along x.",
        "nastaveno"),
    "afm.K_P": (
        "K_P [nm/Hz]:", "K_P [nm/Hz]:",
        "Proporcionální zesílení: o kolik se hrot okamžitě posune na 1 Hz "
        "chyby Δf. Není kalibrované.",
        "Proportional gain: how far the tip moves instantly per 1 Hz of Δf "
        "error. Not calibrated.",
        "nekalibrovano"),
    "afm.mera_sumu": (
        "Míra šumu [x]:", "Noise level [×]:",
        "Násobek změřeného šumu Δf a amplitudy. 0 = bez šumu, 1 = jako na "
        "přístroji.",
        "Multiple of the measured Δf and amplitude noise. 0 = no noise, "
        "1 = as on the instrument.",
        "zmereno"),
    "afm.sum_frekvence": (
        "šum Δf", "Δf noise",
        "Šum měřeného posunu frekvence (změřený, σ = 0,08 Hz).",
        "Noise of the measured frequency shift (measured, σ = 0.08 Hz).",
        "zmereno"),
    "afm.sum_amplitudy": (
        "šum amplitudy", "amplitude noise",
        "Šum amplitudy kmitu (změřený, 1,9 pm); na Δf má zanedbatelný vliv.",
        "Noise of the oscillation amplitude (measured, 1.9 pm); negligible "
        "effect on Δf.",
        "zmereno"),
    "afm.backward": (
        "zpětný průjezd", "backward scan",
        "Po průjezdu tam jede hrot stejnou linkou zpět, smyčka běží dál.",
        "After the forward pass the tip returns along the same line, the "
        "loop keeps running.",
        "ovladani"),
    "afm.zpetna_vazba": (
        "zpětná vazba zapnutá", "feedback on",
        "Vypnutím se přejde do režimu konstantní výšky: topografie se "
        "promítne přímo do Δf.",
        "Switching it off gives the constant-height mode: the topography "
        "shows up directly in Δf.",
        "ovladani"),
    "afm.z_fixed": (
        "z_hrot [nm]:", "z_tip [nm]:",
        "Pevná výška hrotu v režimu konstantní výšky (jen s vypnutou vazbou).",
        "Fixed tip height in constant-height mode (only with the feedback off).",
        "volba"),
    "afm.H": (
        "H [nm]:", "H [nm]:",
        "Výška schodu.", "Step height.", "volba"),
    "afm.w": (
        "w [nm]:", "w [nm]:",
        "Šířka hrany schodu (ramp).", "Width of the step edge (ramp).", "volba"),
    "afm.x_edge": (
        "x_hrany [nm]:", "x_edge [nm]:",
        "Poloha hrany (u atomů první atom).",
        "Position of the edge (for atoms the first atom).", "volba"),
    "afm.atoms_H": (
        "výška atomů [nm]:", "atom height [nm]:",
        "Výška jednoho atomu (gaussovský hrbol).",
        "Height of a single atom (Gaussian bump).", "volba"),
    "afm.atoms_spacing": (
        "rozestup [nm]:", "spacing [nm]:",
        "Vzdálenost sousedních atomů.", "Distance between neighbouring atoms.",
        "volba"),
    "afm.atoms_sigma": (
        "šířka σ [nm]:", "width σ [nm]:",
        "Šířka atomu (směrodatná odchylka gaussovky).",
        "Width of an atom (standard deviation of the Gaussian).", "volba"),
    "afm.atoms_afm_spacing": (
        "rozestup bodů [nm]:", "point spacing [nm]:",
        "Vzdálenost sousedních bodových atomů.",
        "Distance between neighbouring point atoms.", "volba"),
    "afm.atoms_afm_pocet": (
        "počet bodů:", "number of points:",
        "Kolik bodových atomů leží v řadě.",
        "How many point atoms are in the row.", "volba"),
    "afm.atoms_afm_y": (
        "boční posun y [nm]:", "lateral offset y [nm]:",
        "O kolik je linka skenu posunutá vedle řady atomů. Ukazuje, že hrot "
        "atom cítí i mimo pozici přímo nad ním.",
        "How far the scan line is shifted sideways from the atom row. Shows "
        "that the tip feels an atom even when not directly above it.",
        "volba"),
    "afm.Q": (
        "Q:", "Q:",
        "Činitel jakosti cantileveru - šířka rezonance f0/Q.",
        "Quality factor of the cantilever - resonance width f0/Q.",
        "literatura"),
    "afm.poloha": (
        "poloha ve skenu:", "scan position:",
        "Který bod skenu (forward průjezd) se zobrazí v rezonanční křivce.",
        "Which point of the scan (forward pass) is shown in the resonance curve.",
        "ovladani"),
    "afm.df_posun": (
        "Δf [Hz]:", "Δf [Hz]:",
        "Posun rezonance pro ukázku (bez vazby na simulaci).",
        "Resonance shift for illustration (not linked to the simulation).",
        "volba"),
}


PARAMETRY.update({
    "kmb.rezim": (
        "Zpětná vazba:", "Feedback:",
        "Který signál smyčka drží konstantní: proud (STM), posun frekvence "
        "(AFM), nebo žádný (konstantní výška, oba kanály pasivně).",
        "Which signal the loop keeps constant: the current (STM), the "
        "frequency shift (AFM), or none (constant height, both channels "
        "passive).",
        "ovladani"),
    "kmb.controller": PARAMETRY["stm.controller"][:4] + ("ovladani",),
    "kmb.surface": (
        "Povrch:", "Surface:",
        "step / ramp / atoms - stejný povrch vidí oba kanály.",
        "step / ramp / atoms - both channels see the same surface.",
        "volba"),
    "kmb.d_set": (
        "d_set [nm]:", "d_set [nm]:",
        "Společný pracovní bod (střed kmitu). Proud se kalibruje tak, aby "
        "v d_set tekl I_set; Δf_set je Δf(d_set). Musí ležet za minimem Δf(d).",
        "Common working point (centre of the oscillation). The current is "
        "calibrated so that I_set flows at d_set; Δf_set is Δf(d_set). It must "
        "lie beyond the minimum of Δf(d).",
        "volba"),
    "kmb.A": PARAMETRY["afm.A"],
    "kmb.tau_I": (
        "tau (I) [µs]:", "tau (I) [µs]:",
        "Časová konstanta I-složky při zpětné vazbě na proud.",
        "Time constant of the I part with feedback on the current.",
        "nastaveno"),
    "kmb.tau_df": (
        "tau (Δf) [ms]:", "tau (Δf) [ms]:",
        "Časová konstanta I-složky při zpětné vazbě na Δf.",
        "Time constant of the I part with feedback on Δf.",
        "volba"),
    "kmb.T_SYS": PARAMETRY["stm.T_SYS"],
    "kmb.v": PARAMETRY["stm.v"],
    "kmb.mera_sumu": (
        "Míra šumu [x]:", "Noise level [×]:",
        "Násobek změřeného šumu proudu (STM) i Δf (AFM).",
        "Multiple of the measured current (STM) and Δf (AFM) noise.",
        "zmereno"),
    "kmb.sum_proudu": PARAMETRY["stm.sum_proudu"],
    "kmb.sum_frekvence": PARAMETRY["afm.sum_frekvence"],
    "kmb.backward": PARAMETRY["stm.backward"],
    "kmb.z_fixed": (
        "z_hrot [nm]:", "z_tip [nm]:",
        "Pevná výška středu kmitu bez zpětné vazby.",
        "Fixed height of the oscillation centre without feedback.",
        "volba"),
    "kmb.H": PARAMETRY["stm.H"], "kmb.w": PARAMETRY["stm.w"],
    "kmb.x_edge": PARAMETRY["stm.x_edge"], "kmb.atoms_H": PARAMETRY["stm.atoms_H"],
    "kmb.atoms_spacing": PARAMETRY["stm.atoms_spacing"],
    "kmb.atoms_sigma": PARAMETRY["stm.atoms_sigma"],
    "kmb.atoms_pocet": PARAMETRY["stm.atoms_pocet"],
})


def t(klic, jazyk=VYCHOZI_JAZYK, **pole):
    """Text pro klíč v daném jazyce; `pole` se dosadí přes str.format."""
    text = _T[klic][JAZYKY.index(jazyk)]
    return text.format(**pole) if pole else text


def popisek(param, jazyk=VYCHOZI_JAZYK):
    """Krátký popisek ovladače (hodnota `description` widgetu)."""
    return PARAMETRY[param][JAZYKY.index(jazyk)]


def popis(param, jazyk=VYCHOZI_JAZYK):
    """Význam parametru + původ hodnoty (pro tooltip)."""
    i = JAZYKY.index(jazyk)
    zdroj = ZDROJE[PARAMETRY[param][4]][i]
    return f"{PARAMETRY[param][2 + i]} [{zdroj}]"


def legenda_html(parametry, jazyk=VYCHOZI_JAZYK):
    """HTML tabulka parametrů panelu (popisek, význam, původ hodnoty).

    Tooltip na dotykových zařízeních nefunguje, proto je všechno i tady.
    """
    i = JAZYKY.index(jazyk)
    radky = [
        f"<tr><th style='text-align:left'>{t('p.leg_parametr', jazyk)}</th>"
        f"<th style='text-align:left'>{t('p.leg_vyznam', jazyk)}</th>"
        f"<th style='text-align:left'>{t('p.leg_zdroj', jazyk)}</th></tr>"]
    for param in parametry:
        zaznam = PARAMETRY[param]
        radky.append(
            f"<tr><td style='vertical-align:top;padding-right:10px'>"
            f"<b>{zaznam[i].rstrip(':')}</b></td>"
            f"<td style='vertical-align:top;padding-right:10px'>{zaznam[2 + i]}</td>"
            f"<td style='vertical-align:top'><i>{ZDROJE[zaznam[4]][i]}</i></td></tr>")
    return ("<table style='border-collapse:collapse;font-size:90%'>"
            + "".join(radky) + "</table>")


def vsechny_klice():
    """Všechny klíče obecných textů (pro test úplnosti)."""
    return dict(_T)
