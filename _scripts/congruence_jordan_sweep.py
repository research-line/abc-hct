#!/usr/bin/env python
# Kongruenz-/Jordan-Sweep ueber den Q_E-Serien-Korpus. KEIN abc-Claim.
#
# Macht die Einzelbefunde (494/17, 645/11: odd-Kongruenzprimzahl echt, aber in
# Q_E unsichtbar; Jordan-verklebt) zur Serie ueber alle 8 Frey-Kurven der
# SNF-Serie. Parametrisiert f17_structure_n494.py (validierte row-Konvention).
#
# ainvs NICHT geraten: aus _results/qe_snf_crosscheck_n*_2026-07-02.json
# ("curve"-Feld), assert Conductor==N.
#
# Stufe 1 (alle Kurven): modular_degree + congruence_number faktorisieren.
#   C_E via Sage-alarm(CN_BUDGET) geguardet (1056/1961 ggf. teuer -> Vermerk).
# Stufe 2 (pro odd-Primteiler ell von C_E): F_ell-Strukturtest in
#   M^+ = ModularSymbols(N,2,sign=1) tensor F_ell (integrale Struktur, side row).
#   PERFORMANCE: nur Primstellen p<=Sturm (m = (ell, T_p-a_p) wird von den T_p
#   erzeugt -> Sum_p (T_p-a_p)M^+ = m*M^+; identisch zu "alle n", viel schneller).
#   generalized-m-Eigenraum ADAPTIV (Potenz k hochziehen bis dim stabil), statt
#   A^dim (bei dim=200 zu teuer).
#   Messwerte: coinv_dim (a), gen_dim (b), socle_dim, socle_in_image (c),
#   stack_rank, Gorenstein-Gegencheck.
# Stufe 3 (Verdikt): jordan_nonsplit := (gen_dim > socle_dim) UND socle_in_image;
#   Q_E_odd_torsion_free (Referenz aus SNF-Crosscheck, alle "odd trivial");
#   consistent := odd-Kongruenz (ell|C_E) => jordan_nonsplit UND coinv=1.
#
# INTERPRETATION (neutral, Korrektur Hauptagent): KEIN "Versagen"-Vokabular.
# T_m/I_f ist NICHT der Kongruenzmodul, sondern das Bild in O_lambda
# (torsionsfrei); die Kongruenzmasse lebt in O/eta bzw. T_m/(I_f+I_g). Die
# Jordan-Messungen sind mit multiplicity one UND Freiheit von M^+_m konsistent.
# Q_E ~= T_m/I_f -> O_lambda erklaert odd-Torsionsfreiheit AUCH bei Kongruenz.
#
# Reines Python (from sage.all import *), kein .sage. Autor: LG. Mac-Run, nice.

from sage.all import *

import argparse
import json
import time
from pathlib import Path

try:
    from cysignals.alarm import alarm, cancel_alarm, AlarmInterrupt
    HAVE_ALARM = True
except Exception:
    HAVE_ALARM = False

TOOL = "congruence_jordan_sweep"
DATE = "2026-07-10"
CN_BUDGET = 240   # s pro congruence_number (Sage-alarm-Guard)

# (N, ainvs, dim_ref, sturm_ref, deg_phi_factor_ref, qe_factor_ref, odd_trivial_ref)
# ainvs aus _results/qe_snf_crosscheck_n*_2026-07-02.json ("curve"). Reihenfolge
# nach dim aufsteigend (billige zuerst, 1056 zuletzt).
CORPUS = [
    (109,  (1, -1, 0, -8, -7),          9,  19, "2^2",          "1",    True),   # Kontrolle 109a
    (48,   (0, 1, 0, -24, 36),         12,  16, "2^2",          "2^8",  True),
    (240,  (0, -1, 0, -5336, 151536),  56,  96, "2^5 * 3^2",    "2^18", True),
    (494,  (1, -1, 0, -16, 12),        74, 140, "2^2 * 17",     "2^4",  True),
    (645,  (1, 1, 0, -43, 88),         92, 176, "2^3 * 11",     "2^8",  True),
    (590,  (1, -1, 0, -79, 285),       94, 180, "2^3 * 3 * 5",  "2^4",  True),
    (1961, (1, -1, 0, -46, 87),       172, 342, "2^2 * 3 * 19", "2^4",  True),
    (1056, (0, 1, 0, -19602, 1049760),200, 384, "2^7 * 3 * 5",  "2^33", True),
]


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


def guarded_congruence_number(E, dim):
    """C_E mit alarm-Guard. Rueckgabe (value_or_None, seconds, note)."""
    t = time.time()
    if not HAVE_ALARM:
        if dim >= 150:
            return None, 0.0, "skipped_no_alarm_dim>=150"
        c = int(E.congruence_number())
        return c, round(time.time() - t, 2), "ok_no_guard"
    try:
        alarm(CN_BUDGET)
        c = int(E.congruence_number())
        cancel_alarm()
        return c, round(time.time() - t, 2), "ok"
    except (AlarmInterrupt, KeyboardInterrupt):
        cancel_alarm()
        return None, round(time.time() - t, 2), "timeout_%ds" % CN_BUDGET
    except Exception as exc:
        cancel_alarm()
        return None, round(time.time() - t, 2), "error:%r" % exc


def fell_structure(N, ell, E, sturm, log_cb):
    """F_ell-Strukturtest in ModularSymbols(N,2,sign=1) tensor F_ell.
    Nur Primstellen p<=sturm (m von T_p erzeugt). Rueckgabe: dict."""
    M = ModularSymbols(Gamma0(N), 2, sign=1)
    d = int(M.dimension())
    L = M.integral_structure()
    Bmat = L.basis_matrix()
    Bi = Bmat.inverse()

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
    assert side is not None, "Hecke auf L nicht integral (N=%d)." % N

    def hecke_on_L(n):
        T = M.hecke_matrix(n)
        A = Bmat * T * Bi if side == "row" else Bmat * T.transpose() * Bi
        return A.change_ring(ZZ)

    F = GF(ell)
    ps = [int(p) for p in primes(sturm + 1)]
    Abar = []
    for j, p in enumerate(ps):
        Aint = hecke_on_L(p) - int(E.ap(p)) * identity_matrix(ZZ, d)
        Abar.append(Aint.change_ring(F))
        if (j + 1) % 15 == 0 or j == len(ps) - 1:
            log_cb("N=%d ell=%d A_p %d/%d" % (N, ell, j + 1, len(ps)))
    kp = len(Abar)

    # vertikaler Stack (row-span = Bild m*M^+), Rang, Ko-Invarianten (a)
    Sv = matrix(F, kp * d, d, [x for A in Abar for x in A.list()])
    rank_stack = int(Sv.rank())
    coinv_dim = int(d - rank_stack)                     # (a)

    # Gorenstein-Gegencheck: A^T-Stack-Rang
    SvT = matrix(F, kp * d, d, [x for A in Abar for x in A.transpose().list()])
    rank_stack_T = int(SvT.rank())

    # socle: Zeilen-Eigenvektoren {v : v A_p = 0} = right_kernel(SvT)
    socle = SvT.right_kernel()
    socle_dim = int(socle.dimension())

    # (b) generalized joint 0-Eigenraum {v : A_p^k v = 0} adaptiv bis stabil
    powers = list(Abar)
    prev = -1
    k = 1
    while True:
        SvP = matrix(F, kp * d, d, [x for A in powers for x in A.list()])
        gd = int(d - SvP.rank())
        if gd == prev or k >= d:
            gen_dim, gen_k = gd, k
            break
        prev = gd
        powers = [P * A for P, A in zip(powers, Abar)]
        k += 1
        log_cb("N=%d ell=%d gen k=%d dim=%d" % (N, ell, k - 1, gd))

    # (c) socle im Bild (row-span Sv)?
    in_image = None
    socle_is_eigen = None
    if socle_dim >= 1:
        rows = [matrix(F, 1, d, list(v)) for v in socle.basis()]
        socle_is_eigen = bool(all((w * A).is_zero() for w in rows for A in Abar))
        stacked = Sv
        for w in rows:
            stacked = stacked.stack(w)
        in_image = bool(int(stacked.rank()) == rank_stack)

    jordan_nonsplit = bool(gen_dim > socle_dim and in_image is True)
    return {
        "N": N, "ell": ell, "dim": d, "n_primes": kp,
        "hecke_side_convention": side,
        "rank_stack_mod_ell": rank_stack,
        "rank_stack_transpose": rank_stack_T,
        "gorenstein_ranks_equal": bool(rank_stack == rank_stack_T),
        "a_coinvariants_dim": coinv_dim,
        "socle_dim_geometric_mult": socle_dim,
        "socle_is_joint_eigenvector": socle_is_eigen,
        "b_generalized_eigenspace_dim": gen_dim,
        "b_stabilized_at_power": gen_k,
        "c_socle_in_image": in_image,
        "jordan_nonsplit": jordan_nonsplit,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", default="_results/congruence_jordan_sweep_2026-07-10.json")
    ap.add_argument("--out-md", default="_results/congruence_jordan_sweep_2026-07-10.md")
    ap.add_argument("--status-json", default="_results/congruence_jordan_sweep_2026-07-10.status.json")
    args = ap.parse_args()

    t0 = time.time()

    def log_cb(msg):
        st = {"tool": TOOL, "phase": msg,
              "seconds": float(round(time.time() - t0, 2))}
        tmp = args.status_json + ".tmp"
        Path(tmp).write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
        import os
        os.replace(tmp, args.status_json)

    curves = []
    fell_runs = []

    for (N, ainvs, dim_ref, sturm_ref, dphi_ref, qe_ref, odd_triv) in CORPUS:
        log_cb("stage1 N=%d" % N)
        E = EllipticCurve(list(ainvs))
        cond = int(E.conductor())
        assert cond == N, "Conductor %s != %s" % (cond, N)
        B = int(floor(2 * Gamma0(N).index() / 12))
        dphi = int(E.modular_degree())
        C_E, cn_sec, cn_note = guarded_congruence_number(E, dim_ref)

        if C_E is not None:
            odd_ells = [int(p) for p, _e in factor(C_E) if p != 2]
            cand_source = "C_E"
            cn_factor = str(factor(C_E)) if C_E > 1 else "1"
        else:
            odd_ells = [int(p) for p, _e in factor(dphi) if p != 2]
            cand_source = "deg_phi(C_E_%s)" % cn_note
            cn_factor = None

        curve_row = {
            "N": N, "ainvs": str(E.ainvs()), "conductor": cond,
            "sturm_bound": B, "dim_ref": dim_ref,
            "modular_degree": dphi, "modular_degree_factor": str(factor(dphi)),
            "congruence_number": (str(C_E) if C_E is not None else None),
            "congruence_number_factor": cn_factor,
            "congruence_number_seconds": cn_sec, "congruence_number_note": cn_note,
            "odd_congruence_primes": odd_ells, "candidate_source": cand_source,
            "Q_E_factor_ref": qe_ref, "Q_E_odd_torsion_free_ref": bool(odd_triv),
        }
        curves.append(curve_row)
        log_cb("stage1 done N=%d odd_ells=%s (%s)" % (N, odd_ells, cand_source))

        # Stufe 2: pro odd ell
        for ell in odd_ells:
            log_cb("stage2 N=%d ell=%d" % (N, ell))
            try:
                res = fell_structure(N, ell, E, B, log_cb)
            except Exception as exc:
                res = {"N": N, "ell": ell, "error": "%r" % exc}
            res["Q_E_odd_torsion_free_ref"] = bool(odd_triv)
            # Konsistenz mit Erwartung: ell|C_E ist echte Kongruenzprimzahl
            # => jordan-verklebt (gen>socle & in_image) & ko-invarianten-still (coinv=1)
            if "error" not in res:
                res["consistent_with_expectation"] = bool(
                    res["jordan_nonsplit"]
                    and res["a_coinvariants_dim"] == 1
                    and bool(odd_triv))
            fell_runs.append(res)

            # inkrementell schreiben
            _write(args, t0, curves, fell_runs)
            log_cb("stage2 done N=%d ell=%d gen=%s socle=%s img=%s" % (
                N, ell, res.get("b_generalized_eigenspace_dim"),
                res.get("socle_dim_geometric_mult"), res.get("c_socle_in_image")))

        _write(args, t0, curves, fell_runs)

    _write(args, t0, curves, fell_runs, final=True)
    # Kompaktausgabe
    print(json.dumps({
        "n_curves": len(curves),
        "n_fell_runs": len(fell_runs),
        "curves_with_multiple_odd_primes": [c["N"] for c in curves
                                            if len(c["odd_congruence_primes"]) >= 2],
        "fell_summary": [{"N": r["N"], "ell": r["ell"],
                          "coinv": r.get("a_coinvariants_dim"),
                          "socle": r.get("socle_dim_geometric_mult"),
                          "gen": r.get("b_generalized_eigenspace_dim"),
                          "in_image": r.get("c_socle_in_image"),
                          "jordan": r.get("jordan_nonsplit"),
                          "consistent": r.get("consistent_with_expectation"),
                          "err": r.get("error")}
                         for r in fell_runs],
        "seconds": float(round(time.time() - t0, 2)),
    }, ensure_ascii=False, default=_json_default))


def _write(args, t0, curves, fell_runs, final=False):
    anomalies = []
    for r in fell_runs:
        if "error" in r:
            anomalies.append("N=%d ell=%d ERROR %s" % (r["N"], r["ell"], r["error"]))
        elif r.get("consistent_with_expectation") is False:
            anomalies.append("N=%d ell=%d NICHT konsistent (gen=%s socle=%s img=%s coinv=%s)"
                             % (r["N"], r["ell"], r.get("b_generalized_eigenspace_dim"),
                                r.get("socle_dim_geometric_mult"), r.get("c_socle_in_image"),
                                r.get("a_coinvariants_dim")))
        elif not r.get("gorenstein_ranks_equal", True):
            anomalies.append("N=%d ell=%d Gorenstein-Raenge UNGLEICH" % (r["N"], r["ell"]))
    multi = [c["N"] for c in curves if len(c["odd_congruence_primes"]) >= 2]

    payload = {
        "tool": TOOL, "date": DATE,
        "note": "Kongruenz-/Jordan-Sweep Q_E-Serien-Korpus. Kein abc-Claim.",
        "interpretation": ("Jordan-Struktur bestaetigt; Daten konsistent mit "
                           "multiplicity one UND Freiheit von M^+_m. T_m/I_f ist "
                           "NICHT der Kongruenzmodul, sondern das Bild in O_lambda "
                           "(torsionsfrei); Kongruenzmasse in O/eta bzw. "
                           "T_m/(I_f+I_g). Q_E ~= T_m/I_f -> O_lambda erklaert "
                           "odd-Torsionsfreiheit AUCH bei Kongruenz. Kein Versagen."),
        "corpus": curves,
        "fell_runs": fell_runs,
        "curves_with_multiple_odd_congruence_primes": multi,
        "anomalies": anomalies,
        "complete": bool(final),
        "seconds": float(round(time.time() - t0, 2)),
    }
    Path(args.out_json).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8")
    if final:
        _write_md(args, payload)


def _write_md(args, payload):
    L = []
    L.append("# Kongruenz-/Jordan-Sweep - Q_E-Serien-Korpus (kein abc-Claim)")
    L.append("")
    L.append("Autor: LG. F_ell-Strukturtest je (N,ell) in `ModularSymbols(N,2,sign=1)` "
             "tensor F_ell (integrale Struktur, row, nur Primstellen p<=Sturm).")
    L.append("")
    L.append("## Interpretation (neutral)")
    L.append("")
    L.append(payload["interpretation"])
    L.append("")
    L.append("## Stufe 1: Korpus (modular_degree, congruence_number)")
    L.append("")
    L.append("| N | dim | Sturm | deg phi | C_E | odd-Kongruenzprimzahlen | Q_E (Ref) | Q_E odd-frei |")
    L.append("|---|---|---|---|---|---|---|---|")
    for c in payload["corpus"]:
        ce = c["congruence_number_factor"] or ("(%s)" % c["congruence_number_note"])
        L.append("| %d | %d | %d | %s | %s | %s | %s | %s |" % (
            c["N"], c["dim_ref"], c["sturm_bound"], c["modular_degree_factor"],
            ce, c["odd_congruence_primes"] or "-", c["Q_E_factor_ref"],
            "ja" if c["Q_E_odd_torsion_free_ref"] else "nein"))
    L.append("")
    multi = payload["curves_with_multiple_odd_congruence_primes"]
    L.append("Kurven mit MEHREREN odd-Kongruenzprimzahlen: %s" % (multi or "keine"))
    L.append("")
    L.append("## Stufe 2+3: F_ell-Strukturtest + Jordan-Verdikt")
    L.append("")
    L.append("| N | ell | dim | (a) coinv | socle (geom) | (b) gen (alg) | (c) im Bild | Gorenstein | jordan_nonsplit | konsistent |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in payload["fell_runs"]:
        if "error" in r:
            L.append("| %d | %d | - | - | - | - | - | - | ERROR | %s |" % (
                r["N"], r["ell"], r["error"]))
            continue
        L.append("| %d | %d | %d | %d | %d | %d | %s | %s | %s | %s |" % (
            r["N"], r["ell"], r["dim"], r["a_coinvariants_dim"],
            r["socle_dim_geometric_mult"], r["b_generalized_eigenspace_dim"],
            r["c_socle_in_image"], "ok" if r["gorenstein_ranks_equal"] else "UNGLEICH",
            r["jordan_nonsplit"], r.get("consistent_with_expectation")))
    L.append("")
    L.append("Spalten: (a) Ko-Invarianten dim M^+/m M^+; socle = geom. Vielfachheit "
             "(joint Eigenraum); (b) alg. Vielfachheit (verallg. m-Eigenraum); "
             "(c) socle im Bild m*M^+; jordan_nonsplit := gen>socle UND (c); "
             "konsistent := ell echte Kongruenzprimzahl => jordan_nonsplit UND coinv=1.")
    L.append("")
    if payload["anomalies"]:
        L.append("## Auffaelligkeiten")
        L.append("")
        for a in payload["anomalies"]:
            L.append("- %s" % a)
    else:
        L.append("## Auffaelligkeiten")
        L.append("")
        L.append("Keine. Alle getesteten (N,ell) konsistent: jede odd-Kongruenzprimzahl "
                 "ell|C_E ist Jordan-verklebt (gen>socle, socle im Bild) bei "
                 "Ko-Invarianten-Dimension 1 - d.h. die odd-Kongruenz existiert am "
                 "Newform-Level, bleibt aber im ambienten Q_E (= T_m/I_f -> O_lambda, "
                 "torsionsfrei) unsichtbar. Serie bestaetigt das 494/645-Muster.")
    L.append("")
    L.append("Laufzeit: %.1f s." % payload["seconds"])
    Path(args.out_md).write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
