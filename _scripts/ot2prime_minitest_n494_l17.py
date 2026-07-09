#!/usr/bin/env python
# OT-2'-Mini-Test N=494, ell=17 - Instanz-Zertifikat (KEIN abc-Claim).
#
# Design-Quelle (1:1 uebernommen): _codex/CODEX_OT2_ANTWORT_2026-07-02.md,
# Abschnitt "## 6. Mini-Test". Ziel: exakt entscheiden, ob die 17 aus
# deg phi = 68 = 2^2 * 17 als schwache Away-from-N-Kongruenz zwischen der
# Frey-Newform f_E und einer FREMDEN Newform-Orbit erscheint und ob sie durch
# U_2, U_13, U_19 getoetet wird.
#
# Reines Python (from sage.all import *) - KEIN .sage-File wegen Queue-
# Preparser-Bug (bekannt). Autor: LG.
#
# Zwei unabhaengige Instrumente auf dieselbe Frage:
#   (A) Codex-Kongruenz-Report ueber die Newform-Orbits von Gamma0(494):
#       pro Orbit good_away_from_N / good_plus_bad_U_p / full_sturm + killed_by_U_p.
#   (B) SNF-Zusatztest ("Pruefpunkt b"): zwei Varianten der Smith-Normalform von
#       M^+ / sum_{n} (T_n - a_n(E)) M^+  (integrale Struktur, Vorlage
#       _scripts/qe_snf_crosscheck_n1056.sage):
#         (i)  NUR away-from-N: n <= 140 mit gcd(n,494)=1,
#         (ii) VOLL: alle n <= 140 (inkl. n=2,13,19,... -> U_p-Anteile).
#       Jede odd-Torsion in (i), die in (ii) verschwindet, benennt exakt den
#       U_p-Kill. Erwartung laut Design: volle Variante nur 2-Gruppe (2,2,2,2).
#
# Laufprofil: 1 Kern, moderat RAM (dim ~74, kein PARI-Overflow), Minuten.
# Direct-Run auf Mac mit nice, parallel zum Grossjob zulaessig.

from sage.all import *

import argparse
import json
import time
from pathlib import Path

TOOL = "ot2prime_minitest_n494_l17"
DATE = "2026-07-10"

N = 494
ELL = 17
A_FREY, B_FREY = 13, 19   # Frey-Kurve y^2 = x(x-a)(x+b), a=13, b=19


# ---------------------------------------------------------------------------
# JSON-Serialisierung: Sage-Objekte (Ideale, Zahlkoerper) sind nicht
# JSON-serialisierbar. Ideale -> Norm + Generatoren-Strings; Koerper ->
# Grad + Definitionspolynom-String. Zusaetzlich ein default-Handler als
# Sicherheitsnetz gegen versehentlich durchgereichte Sage-Zahlen (z. B. weil
# `from sage.all import *` das builtin `round` mit einem RealDoubleElement-
# liefernden `round` ueberschreibt).
# ---------------------------------------------------------------------------
def _json_default(o):
    try:
        if isinstance(o, Integer):
            return int(o)
    except Exception:
        pass
    try:
        return float(o)
    except Exception:
        return str(o)


def ser_field(K):
    if K == QQ:
        return {"degree": 1, "defining_polynomial": "x"}
    return {"degree": int(K.degree()),
            "defining_polynomial": str(K.defining_polynomial())}


def ser_ideal(K, I):
    if K == QQ:
        g = ZZ(I.gen())
        return {"norm": str(abs(g)), "gens": [str(g)]}
    return {"norm": str(I.norm()), "gens": [str(g) for g in I.gens()]}


def order_and_ideal(K, diffs, ell):
    # Existenz eines Primideals ueber ell, das alle Differenzen enthaelt, ist
    # aequivalent dazu, dass das erzeugte Ideal ECHT ist (1 nicht enthalten).
    # WICHTIG (Bugfix ggue. Design-Skelett): Properness ueber Mengen-
    # Mitgliedschaft `1 not in I` pruefen, NICHT `I != ZZ` - ein ZZ-Ideal-Objekt
    # ist NIE gleich dem Ring-Objekt ZZ, sodass `I != ZZ` fuer JEDES Ideal (auch
    # das Einheitsideal) True liefert -> falsche Positivbefunde im QQ-Zweig
    # (empirisch beobachtet: norm-1-Ideale als kongruent gemeldet).
    if K == QQ:
        gens = [ZZ(ell)] + [ZZ(d) for d in diffs]
        I = ZZ.ideal(gens)
        return (ZZ(1) not in I), I
    OK = K.ring_of_integers()
    gens = [OK(ell)] + [OK(K(d)) for d in diffs]
    I = OK.ideal(gens)
    return (OK(1) not in I), I


def log(state, path):
    state["seconds"] = float(round(time.time() - state["_t0"], 3))
    clean = {k: v for k, v in state.items() if not k.startswith("_")}
    tmp = str(path) + ".tmp"
    Path(tmp).write_text(json.dumps(clean, ensure_ascii=False, indent=2,
                                    default=_json_default),
                         encoding="utf-8")
    import os
    os.replace(tmp, str(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json",
                    default="_results/ot2prime_minitest_n494_l17_2026-07-10.json")
    ap.add_argument("--out-md",
                    default="_results/ot2prime_minitest_n494_l17_2026-07-10.md")
    ap.add_argument("--status-json",
                    default="_results/ot2prime_minitest_n494_l17_2026-07-10.status.json")
    args = ap.parse_args()

    t0 = time.time()
    st = {"_t0": t0, "tool": TOOL, "date": DATE, "phase": "starting"}
    log(st, args.status_json)

    # ---- Frey-Kurve + Sturm-Bound (Design-Asserts; bei Fehlschlag Abbruch) ----
    a, b = A_FREY, B_FREY
    E = EllipticCurve([0, b - a, 0, -a * b, 0])   # y^2 = x(x-a)(x+b)
    cond = int(E.conductor())
    assert cond == N, "Conductor %s != erwartet %s - Abbruch (nicht raten)." % (cond, N)

    B = int(floor(2 * Gamma0(N).index() / 12))
    assert B == 140, "Sturm-Bound %s != 140 - Abbruch (nicht raten)." % B

    bad_primes = [int(p) for p in prime_divisors(N)]          # [2, 13, 19]
    good_ns = [n for n in range(1, B + 1) if gcd(n, N) == 1]
    all_ns = list(range(1, B + 1))

    st.update({"curve_ainvs": str(E.ainvs()), "conductor": cond,
               "index_gamma0": int(Gamma0(N).index()), "sturm_bound": B,
               "bad_primes": bad_primes, "n_good_ns": len(good_ns),
               "n_all_ns": len(all_ns), "phase": "an_cache"})
    log(st, args.status_json)

    # a_n(E) fuer n <= B (an(p) == ap(p) an Primstellen, inkl. schlechte).
    anE = [None] + [ZZ(E.an(n)) for n in range(1, B + 1)]

    # =======================================================================
    # (A) Codex-Kongruenz-Report ueber Newform-Orbits
    # =======================================================================
    st["phase"] = "newforms"
    log(st, args.status_json)
    forms = Newforms(Gamma0(N), 2, names='a')
    st.update({"n_orbits": len(forms), "phase": "target_id"})
    log(st, args.status_json)

    # q-Entwicklungen einmalig cachen (Praezision B+2 -> Index bis B+1).
    qexps = [f.q_expansion(B + 2) for f in forms]
    fields = [f.base_ring() for f in forms]

    def qc(i, n):
        return fields[i](qexps[i][n])

    # Frey-Newform-Orbit identifizieren (Design: erste 20 gute Primstellen).
    test_primes = [int(p) for p in primes(B) if p not in bad_primes][:20]
    target = []
    for i in range(len(forms)):
        K = fields[i]
        if all(qc(i, p) == K(anE[p]) for p in test_primes):
            target.append(i)
    st.update({"target_orbit_indices": target, "phase": "congruence_report"})
    log(st, args.status_json)

    def congruence_report(i):
        K = fields[i]
        diffs_good = [qc(i, n) - K(anE[n]) for n in good_ns]
        diffs_all = [qc(i, n) - K(anE[n]) for n in all_ns]
        diffs_badp = [qc(i, p) - K(anE[p]) for p in bad_primes]

        good_ok, I_good = order_and_ideal(K, diffs_good, ELL)
        all_ok, I_all = order_and_ideal(K, diffs_all, ELL)
        bad_ok, I_bad = order_and_ideal(K, diffs_good + diffs_badp, ELL)

        killed_by = []
        for p in bad_primes:
            ok_p, _ = order_and_ideal(
                K, diffs_good + [qc(i, p) - K(anE[p])], ELL)
            if good_ok and not ok_p:
                killed_by.append(int(p))

        return {
            "orbit_index": i,
            "is_target": (i in target),
            "field": ser_field(K),
            "good_away_from_N": bool(good_ok),
            "good_plus_bad_U_p": bool(bad_ok),
            "full_sturm": bool(all_ok),
            "killed_by_U_p": killed_by,
            "I_good": ser_ideal(K, I_good),
            "I_bad": ser_ideal(K, I_bad),
            "I_all": ser_ideal(K, I_all),
        }

    # Unabhaengige Gegenprobe zum Ideal-Kriterium: reduziere a_n(f_i) modulo
    # jeder Primstelle lam|17 in O_K und vergleiche mit a_n(E) mod 17 fuer ALLE
    # n <= B (Sturm-zertifiziert). Rein ueber Residuenkoerper-Reduktion, ohne
    # Ideal-Properness-Logik -> deckt einen etwaigen Restfehler des Ideal-Wegs auf.
    def direct_verify_full(i):
        K = fields[i]
        qe = qexps[i]
        if K == QQ:
            ok = all((ZZ(qe[n]) - anE[n]) % ELL == 0 for n in all_ns)
            return ok, (str(ELL) if ok else None)
        for lam, _e in K.ideal(ELL).factor():
            F = lam.residue_field()
            try:
                if all(F(qe[n]) == F(ZZ(anE[n])) for n in all_ns):
                    return True, str(lam.norm())
            except Exception:
                continue
        return False, None

    # Report fuer ALLE Orbits (auch Negativbefunde ins JSON).
    reports = [congruence_report(i) for i in range(len(forms))]
    for r in reports:
        v_ok, v_lam = direct_verify_full(r["orbit_index"])
        r["direct_verify_full_congruence"] = bool(v_ok)
        r["direct_verify_lambda_norm"] = v_lam

    nt = [r for r in reports if not r["is_target"]]
    any_good_away = any(r["good_away_from_N"] for r in nt)
    any_full_ideal = any(r["full_sturm"] for r in nt)
    verified_full_orbits = [r["orbit_index"] for r in nt
                            if r["direct_verify_full_congruence"]]
    killed_reports = [r for r in nt
                      if r["good_away_from_N"] and not r["good_plus_bad_U_p"]]

    # Konsistenz Ideal-Kriterium vs. direkte Gegenprobe (beide muessen fuer
    # Nicht-Target-Orbits denselben full-congruence-Befund liefern).
    ideal_full_orbits = [r["orbit_index"] for r in nt if r["full_sturm"]]
    ideal_vs_direct_agree = (sorted(ideal_full_orbits) == sorted(verified_full_orbits))

    # Welcher der 3 Design-Ausgaenge? Headline auf die DIREKTE Gegenprobe stuetzen.
    if verified_full_orbits:
        design_outcome = 3          # OT-2-Gegenbeispiel: all-p-Kongruenz fremder Orbit
    elif any_good_away:
        design_outcome = 2          # away ja, aber durch U_p getoetet
    else:
        design_outcome = 1          # keine Away-from-N-17-Kongruenz

    killed_primes = sorted({p for r in killed_reports for p in r["killed_by_U_p"]})

    # =======================================================================
    # (B) SNF-Zusatztest (Pruefpunkt b) - zwei Varianten
    # =======================================================================
    st["phase"] = "snf_modular_symbols"
    log(st, args.status_json)

    M = ModularSymbols(Gamma0(N), 2, sign=1)
    d = int(M.dimension())
    L = M.integral_structure()
    Bmat = L.basis_matrix()
    Bi = Bmat.inverse()
    st.update({"snf_ambient": "ModularSymbols(%d,2,sign=1)" % N, "snf_dim": d})
    log(st, args.status_json)

    # Seitenkonvention einmalig bestimmen + per Integralitaet validieren
    # (Hecke muss die Integralstruktur L erhalten).
    side = None
    T2 = M.hecke_matrix(2)
    for cand, name in ((Bmat * T2 * Bi, "row"),
                       (Bmat * T2.transpose() * Bi, "col")):
        try:
            cand.change_ring(ZZ)
            side = name
            break
        except (TypeError, ValueError):
            continue
    assert side is not None, "Hecke-Wirkung auf L in keiner Konvention integral - Abbruch."
    st["hecke_side_convention"] = side
    log(st, args.status_json)

    def hecke_on_L(n):
        T = M.hecke_matrix(n)
        A = Bmat * T * Bi if side == "row" else Bmat * T.transpose() * Bi
        return A.change_ring(ZZ)   # wirft, falls nicht integral -> Selbstvalidierung

    # A_n = (T_n - a_n(E)) auf L, einmalig fuer alle n <= B (fuer beide Varianten).
    Amats = {}
    for k, n in enumerate(all_ns):
        Amats[n] = hecke_on_L(n) - int(anE[n]) * identity_matrix(ZZ, d)
        if (k + 1) % 20 == 0 or k == len(all_ns) - 1:
            st.update({"snf_hecke_built": int(k + 1)})
            log(st, args.status_json)

    def snf_of(ns):
        blocks = [Amats[n] for n in ns]
        stack = matrix(ZZ, len(blocks) * d, d,
                       [x for A in blocks for x in A.list()])
        red = stack.hermite_form(include_zero_rows=False)
        divs = red.elementary_divisors()
        nz = [ZZ(x) for x in divs if x != 0]
        free_rank = int(d - red.nrows()) + sum(1 for x in divs if x == 0)
        tors = [ZZ(x) for x in nz if x > 1]
        order = ZZ(1)
        for x in tors:
            order *= x
        per_ell = {}
        for ell in (2, 3, 5, 7, 17):
            per_ell[str(ell)] = int(sum(ZZ(x).valuation(ell) for x in nz))
        return {
            "n_generators": len(ns),
            "free_rank": free_rank,
            "torsion_invariant_factors": [str(x) for x in tors],
            "torsion_order": str(order),
            "torsion_order_factor": str(factor(order)) if order > 1 else "1",
            "length_per_ell": per_ell,
        }

    st["phase"] = "snf_away"
    log(st, args.status_json)
    snf_away = snf_of(good_ns)          # Variante (i): nur away-from-N
    st["phase"] = "snf_full"
    log(st, args.status_json)
    snf_full = snf_of(all_ns)           # Variante (ii): voll (inkl. U_p)

    # Differenz: welche ell-Torsion verschwindet von (i) nach (ii)?
    snf_killed_ell = []
    for ell in (2, 3, 5, 17):
        li = snf_away["length_per_ell"][str(ell)]
        lf = snf_full["length_per_ell"][str(ell)]
        if li > lf:
            snf_killed_ell.append({"ell": ell, "length_away": li,
                                   "length_full": lf, "killed": li - lf})
    snf_full_is_2group = (snf_full["length_per_ell"]["17"] == 0 and
                          all(snf_full["length_per_ell"][str(e)] == 0
                              for e in (3, 5, 7)))

    # =======================================================================
    # Payload + Ausgaben
    # =======================================================================
    seconds = float(round(time.time() - t0, 3))
    payload = {
        "tool": TOOL, "date": DATE,
        "note": "Instanz-Zertifikat fuer N=494/ell=17. Kein abc-Claim.",
        "curve_ainvs": str(E.ainvs()), "conductor": cond,
        "frey_ab": [a, b], "ell": ELL,
        "index_gamma0": int(Gamma0(N).index()), "sturm_bound": B,
        "bad_primes": bad_primes,
        "deg_phi": int(E.modular_degree()),
        "deg_phi_factor": str(factor(E.modular_degree())),
        "n_orbits": len(forms),
        "target_orbit_indices": target,
        "design_outcome": design_outcome,
        "design_outcome_label": {
            1: "keine_away_from_N_17_kongruenz",
            2: "away_ja_durch_U_p_getoetet",
            3: "full_sturm_fremde_orbit_OT2_gegenbeispiel",
        }[design_outcome],
        "killed_by_U_p_primes": killed_primes,
        "verified_full_congruence_orbits": verified_full_orbits,
        "ideal_full_congruence_orbits": ideal_full_orbits,
        "ideal_vs_direct_agree": bool(ideal_vs_direct_agree),
        "congruence_reports": reports,
        "snf_test": {
            "ambient": "ModularSymbols(%d,2,sign=1)" % N,
            "dim": d,
            "hecke_side_convention": side,
            "variant_i_away_from_N": snf_away,
            "variant_ii_full": snf_full,
            "killed_ell_away_to_full": snf_killed_ell,
            "full_is_2group_only": bool(snf_full_is_2group),
        },
        "seconds": seconds,
    }
    Path(args.out_json).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2,
                   default=_json_default), encoding="utf-8")

    # -- Menschenlesbares MD --
    outcome_txt = {
        1: ("**Ausgang 1 - keine Away-from-N-17-Kongruenz.** Keine fremde "
            "Newform-Orbit ist away-from-N mod einer Primstelle ueber 17 zu "
            "f_E kongruent. Die 17 aus deg phi erklaert also KEINE "
            "Newform-Kongruenz; sie liegt in einem anderen Objekt als "
            "T_N^full/I_f (Gitter-/Periodenrelation)."),
        2: ("**Ausgang 2 - Away-from-N-Kongruenz ja, aber durch U_p getoetet.** "
            "Feature-These exakt bestaetigt: die 17 erscheint away-from-N und "
            "scheitert an U_p an der/den Primstelle(n) %s." % killed_primes),
        3: ("**Ausgang 3 - all-p-Kongruenz (inkl. U_p) einer FREMDEN Orbit.** "
            "Die Orbit(s) %s sind mod einer Primstelle ueber 17 an ALLEN n <= B "
            "(inkl. U_2,U_13,U_19) zu f_E kongruent - unabhaengig per "
            "Residuenkoerper-Reduktion verifiziert (Ideal-Kriterium und direkte "
            "Gegenprobe stimmen ueberein: %s). Damit ist die naive OT-2 (kein "
            "g!=f_E mit all-p-Kongruenz) in der N=494/ell=17-Instanz am "
            "Newform-Level FALSCH. Der ambiente SNF-Quotient Q_E (unten) zeigt "
            "hingegen KEINE 17-Torsion - genau die von Codex (Abschnitt 4/6) "
            "benannte Objekttrennung: Q_E misst NICHT das volle "
            "Newform-Kongruenzmodul."
            % (verified_full_orbits, "ja" if ideal_vs_direct_agree else "NEIN")),
    }[design_outcome]

    lines = []
    lines.append("# OT-2'-Mini-Test - N=494, ell=17 (Instanz-Zertifikat)")
    lines.append("")
    lines.append("Autor: LG. Design: `_codex/CODEX_OT2_ANTWORT_2026-07-02.md`, Abschnitt 6.")
    lines.append("Kein abc-Claim - reines Instanz-Zertifikat.")
    lines.append("")
    lines.append("## Kernbefund")
    lines.append("")
    lines.append(outcome_txt)
    lines.append("")
    lines.append("| Groesse | Wert |")
    lines.append("|---|---|")
    lines.append("| Frey-Kurve (a,b) | (%d, %d), ainvs=%s |" % (a, b, E.ainvs()))
    lines.append("| Conductor N | %d |" % cond)
    lines.append("| Index [SL2:Gamma0(N)] | %d |" % Gamma0(N).index())
    lines.append("| Sturm-Bound B | %d |" % B)
    lines.append("| schlechte Primstellen | %s |" % bad_primes)
    lines.append("| deg phi | %d = %s |" % (E.modular_degree(),
                                            factor(E.modular_degree())))
    lines.append("| Newform-Orbits | %d |" % len(forms))
    lines.append("| Target-Orbit-Index (f_E) | %s |" % target)
    lines.append("| Design-Ausgang | %d (%s) |" % (
        design_outcome, payload["design_outcome_label"]))
    lines.append("")
    lines.append("## Kongruenz-Report pro Orbit")
    lines.append("")
    lines.append("| Orbit | Koerper (Grad) | target | good_away_from_N | good_plus_bad_U_p | full_sturm | killed_by_U_p | direkt-verif. (N(lam)) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in reports:
        dv = ("ja (N=%s)" % r["direct_verify_lambda_norm"]
              if r["direct_verify_full_congruence"] else "-")
        lines.append("| %d | Q(deg %d) | %s | %s | %s | %s | %s | %s |" % (
            r["orbit_index"], r["field"]["degree"],
            "ja" if r["is_target"] else "-",
            r["good_away_from_N"], r["good_plus_bad_U_p"],
            r["full_sturm"], r["killed_by_U_p"] or "-", dv))
    lines.append("")
    lines.append("Ideal-Kriterium vs. direkte Residuenkoerper-Gegenprobe (Nicht-Target): "
                 "%s. Verifizierte all-p-Kongruenz-Orbits: %s."
                 % ("stimmen ueberein" if ideal_vs_direct_agree else "WIDERSPRUCH",
                    verified_full_orbits or "keine"))
    lines.append("")
    lines.append("## SNF-Zusatztest (Pruefpunkt b): M^+ / sum (T_n - a_n(E)) M^+")
    lines.append("")
    lines.append("Ambient: `ModularSymbols(%d,2,sign=1)`, dim=%d, Hecke-Konvention: %s."
                 % (N, d, side))
    lines.append("")
    lines.append("| Variante | #Generatoren n | free_rank | Torsions-Invariantenfaktoren | Torsionsordnung | len_2 | len_3 | len_5 | len_17 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for name, s in (("(i) away-from-N", snf_away), ("(ii) VOLL", snf_full)):
        pe = s["length_per_ell"]
        lines.append("| %s | %d | %d | %s | %s | %d | %d | %d | %d |" % (
            name, s["n_generators"], s["free_rank"],
            ", ".join(s["torsion_invariant_factors"]) or "-",
            s["torsion_order_factor"], pe["2"], pe["3"], pe["5"], pe["17"]))
    lines.append("")
    if snf_killed_ell:
        lines.append("Von (i) nach (ii) getoetete ell-Torsion (U_p-Kill sichtbar): %s"
                     % ", ".join("ell=%d: %d->%d" % (k["ell"], k["length_away"],
                                                     k["length_full"])
                                 for k in snf_killed_ell))
    else:
        lines.append("Von (i) nach (ii) verschwindet KEINE Torsion "
                     "(away-from-N und voll identisch in der Torsionsstruktur).")
    lines.append("")
    if snf_full_is_2group and not verified_full_orbits:
        lines.append("Die VOLLE Variante ist nur eine 2-Gruppe (keine odd-Torsion) "
                     "UND es gibt keine verifizierte fremde all-p-Kongruenz "
                     "=> all-p-OT-2 fuer N=494 ist SNF-zertifiziert. Objekttrennung "
                     "zu deg phi (Faktor 17) bleibt erklaerungsbeduerftig.")
    elif snf_full_is_2group and verified_full_orbits:
        lines.append("ACHTUNG Objekttrennung: Die VOLLE SNF-Variante ist nur eine "
                     "2-Gruppe (Q_E = %s, keine 17-Torsion), ABER der Newform-"
                     "Kongruenz-Report weist eine verifizierte all-p-Kongruenz mod "
                     "17 mit Orbit %s nach. Der ambiente Manin-/SNF-Quotient Q_E "
                     "misst also NICHT das volle Newform-Kongruenzmodul (Codex "
                     "Abschnitt 4/6). Die SNF allein wuerde OT-2 faelschlich als "
                     "zertifiziert ausweisen." % (snf_full["torsion_order_factor"],
                                                  verified_full_orbits))
    else:
        lines.append("Die VOLLE Variante enthaelt odd-Torsion "
                     "=> all-p-OT-2 fuer N=494 NICHT SNF-zertifiziert (Ausgang 3 pruefen).")
    lines.append("")
    lines.append("Laufzeit: %.1f s. Kontext-Vorlage: `_scripts/qe_snf_crosscheck_n1056.sage`, "
                 "`_results/qe_snf_crosscheck_n494_2026-07-02.json`." % seconds)
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")

    st.update({"phase": "finished", "design_outcome": design_outcome,
               "snf_full_is_2group": bool(snf_full_is_2group)})
    log(st, args.status_json)

    print(json.dumps({
        "design_outcome": design_outcome,
        "design_outcome_label": payload["design_outcome_label"],
        "target_orbit_indices": target,
        "n_orbits": len(forms),
        "killed_by_U_p_primes": killed_primes,
        "verified_full_congruence_orbits": verified_full_orbits,
        "ideal_vs_direct_agree": bool(ideal_vs_direct_agree),
        "snf_away_torsion": snf_away["torsion_order_factor"],
        "snf_full_torsion": snf_full["torsion_order_factor"],
        "snf_away_free_rank": snf_away["free_rank"],
        "snf_full_free_rank": snf_full["free_rank"],
        "snf_killed_ell": snf_killed_ell,
        "seconds": seconds,
    }, ensure_ascii=False, default=_json_default))


if __name__ == "__main__":
    main()
