#!/usr/bin/env python
# F17-Strukturtest N=494 (b'''') - Multiplicity-One-Spannung. KEIN abc-Claim.
#
# Kontext: Bei N=494 existiert die all-p-Kongruenz mod lam|17 mit einer fremden
# Newform-Orbit (Befund ot2prime_minitest_n494_l17), ABER der ambiente
# SNF-Quotient Q_E = 2^4 hat KEINE 17-Torsion. Waere M^+_m frei vom Rang 1 ueber
# T_m (multiplicity one + Freiheit), muesste M^+_m/I_f M^+_m ~= T_m/I_f != 0 die
# 17 zeigen - tut sie nicht. Welches Glied versagt?
#
# Messung in M^+ = ModularSymbols(494,2,sign=1) tensor F_17 (integrale Struktur
# wie im SNF-Test, hecke_side row). Konvention SNF-konsistent: die Untermodul-
# Bildung Sum (T_n - a_n(E)) M^+ = ROW-Span der A_n (wie qe_snf_crosscheck /
# ot2prime SNF-Test, die #Q_E=2^4 gegen bekannte Werte validiert haben).
#
#   (a) dim des Ko-Eigenraums (Ko-Invarianten):
#       dim M^+ tensor F17 / Sum_{n<=140} (T_n - a_n(E)) (M^+ tensor F17)
#       = d - rank_F17(vertikaler Stack der A_n)  [Erwartung 1]
#   (b) dim des VERALLGEMEINERTEN m-Eigenraums:
#       dim {v : (T_n - a_n(E))^d v = 0 fuer alle n}  [Erwartung >= 2]
#   (c) SPLIT-TEST: Liegt ein simultaner Eigenvektor (Eigenwerte a_n(E) mod 17)
#       im BILD Sum (T_n - a_n) (M^+ tensor F17) (= row-span)?  [Erwartung ja]
#   (d) dim M^+ tensor F17 gesamt + Rang des (T_n - a_n)-Stacks mod 17.
#
# Interpretation: (b)>=2 UND (a)=1 UND (c)=ja  ==>  nicht-split-Verklebung
# mechanisch bestaetigt (Jordan-Block), Ko-Invarianten-Blindheit erklaert.
# Sonst: Befund roh dokumentieren.
#
# Reines Python (from sage.all import *), kein .sage. Autor: LG.

from sage.all import *

import argparse
import json
import time
from pathlib import Path

TOOL = "f17_structure_n494"
DATE = "2026-07-10"

N = 494
ELL = 17
A_FREY, B_FREY = 13, 19
STURM_EXPECT = 140


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


def log(state, path):
    state["seconds"] = float(round(time.time() - state["_t0"], 3))
    clean = {k: v for k, v in state.items() if not k.startswith("_")}
    tmp = str(path) + ".tmp"
    Path(tmp).write_text(json.dumps(clean, ensure_ascii=False, indent=2,
                                    default=_json_default), encoding="utf-8")
    import os
    os.replace(tmp, str(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", default="_results/f17_structure_n494_2026-07-10.json")
    ap.add_argument("--out-md", default="_results/f17_structure_n494_2026-07-10.md")
    ap.add_argument("--status-json", default="_results/f17_structure_n494_2026-07-10.status.json")
    args = ap.parse_args()

    t0 = time.time()
    st = {"_t0": t0, "tool": TOOL, "date": DATE, "phase": "starting"}
    log(st, args.status_json)

    a, b = A_FREY, B_FREY
    E = EllipticCurve([0, b - a, 0, -a * b, 0])
    cond = int(E.conductor())
    assert cond == N, "Conductor %s != %s" % (cond, N)
    B = int(floor(2 * Gamma0(N).index() / 12))
    assert B == STURM_EXPECT, "Sturm %s != %s" % (B, STURM_EXPECT)

    all_ns = list(range(1, B + 1))
    anE = [None] + [ZZ(E.an(n)) for n in range(1, B + 1)]
    st.update({"conductor": cond, "sturm_bound": B, "ell": ELL, "phase": "modsym"})
    log(st, args.status_json)

    # ---- Integrale Struktur + Hecke (row-Konvention, wie SNF-Test) ----
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
    assert side is not None, "Hecke auf L nicht integral."
    st.update({"dim": d, "hecke_side_convention": side, "phase": "build_A"})
    log(st, args.status_json)

    def hecke_on_L(n):
        T = M.hecke_matrix(n)
        A = Bmat * T * Bi if side == "row" else Bmat * T.transpose() * Bi
        return A.change_ring(ZZ)

    F = GF(ELL)
    # A_n = (T_n - a_n(E)) auf L, direkt mod ELL reduziert.
    Abar = []
    for k, n in enumerate(all_ns):
        Aint = hecke_on_L(n) - int(anE[n]) * identity_matrix(ZZ, d)
        Abar.append(Aint.change_ring(F))
        if (k + 1) % 20 == 0 or k == len(all_ns) - 1:
            st.update({"A_built": int(k + 1)})
            log(st, args.status_json)
    kk = len(Abar)

    # ---- (d) + (a): vertikaler Stack (row-span = Bild Sum(T_n-a_n)M^+) ----
    st["phase"] = "stack_rank"
    log(st, args.status_json)
    Sv = matrix(F, kk * d, d, [x for A in Abar for x in A.list()])
    rank_stack = int(Sv.rank())
    coinv_dim = int(d - rank_stack)            # (a) Ko-Invarianten
    Im_basis = Sv.row_space().basis_matrix()   # Basis des Bildes (row-span)

    # Gorenstein-Gegencheck: rank des A^T-Stacks (Sum colspaces) sollte gleich sein.
    SvT = matrix(F, kk * d, d, [x for A in Abar for x in A.transpose().list()])
    rank_stack_T = int(SvT.rank())

    # ---- socle: simultane Eigenvektoren v (Zeile) mit v*A_n = 0 fuer alle n ----
    # {v : v A_n = 0} = {v : A_n^T v^T = 0} = right-kernel(SvT).
    st["phase"] = "socle"
    log(st, args.status_json)
    socle = SvT.right_kernel()
    socle_dim = int(socle.dimension())         # geometrische Vielfachheit

    # ---- (b) verallgemeinerter m-Eigenraum: {v : A_n^d v = 0 alle n} ----
    st["phase"] = "generalized"
    log(st, args.status_json)
    Apow = [A ** d for A in Abar]              # A_n^d ueber F17 (Nilpotenzindex <= d)
    SvP = matrix(F, kk * d, d, [x for A in Apow for x in A.list()])
    gen_dim = int(d - SvP.rank())              # (b) algebraische Vielfachheit

    # ---- (c) Split-Test: liegt socle im Bild (row-span Sv)? ----
    st["phase"] = "split_test"
    log(st, args.status_json)
    in_image = None
    socle_is_eigen = None
    socle_vec = None
    if socle_dim >= 1:
        # socle-Basisvektoren (als Spalten aus right_kernel) -> Zeilen w
        rows = [matrix(F, 1, d, list(v)) for v in socle.basis()]
        # Selbstvalidierung: w A_n = 0 fuer alle n?
        socle_is_eigen = all((w * A).is_zero() for w in rows for A in Abar)
        # Bild-Mitgliedschaft: alle socle-Vektoren in row-span(Sv)?
        stacked = Sv
        for w in rows:
            stacked = stacked.stack(w)
        in_image = bool(stacked.rank() == rank_stack)
        socle_vec = [int(x) for x in socle.basis()[0]]

    interp_nonsplit = bool(gen_dim >= 2 and coinv_dim == 1 and in_image is True)

    seconds = float(round(time.time() - t0, 3))
    payload = {
        "tool": TOOL, "date": DATE,
        "note": "F17-Strukturtest N=494 (Multiplicity-One-Spannung). Kein abc-Claim.",
        "conductor": cond, "ell": ELL, "sturm_bound": B,
        "ambient": "ModularSymbols(%d,2,sign=1)" % N,
        "hecke_side_convention": side,
        "dim_total_M_plus_F17": d,                       # (d)
        "rank_stack_mod_ell": rank_stack,                # (d)
        "rank_stack_transpose_mod_ell": rank_stack_T,    # Gorenstein-Gegencheck
        "gorenstein_ranks_equal": bool(rank_stack == rank_stack_T),
        "a_coinvariants_dim": coinv_dim,                 # (a) Erwartung 1
        "socle_dim_geometric_mult": socle_dim,           # geometrische Vielfachheit
        "socle_is_joint_eigenvector": socle_is_eigen,    # Selbstvalidierung
        "b_generalized_eigenspace_dim": gen_dim,         # (b) Erwartung >=2
        "c_socle_in_image": in_image,                    # (c) Erwartung True
        "socle_vector_first": socle_vec,
        "interpretation_nonsplit_confirmed": interp_nonsplit,
        "seconds": seconds,
    }
    Path(args.out_json).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8")

    # ---- MD ----
    if interp_nonsplit:
        verdict = ("**Nicht-split-Verklebung mechanisch bestaetigt.** (b)=%d>=2 "
                   "(verallgemeinerter m-Eigenraum) UND (a)=%d=1 (Ko-Invarianten) "
                   "UND (c)=ja (Eigenvektor im Bild). f_E und die kongruente "
                   "g-Linie sitzen in EINEM Jordan-Block; der Ko-Invarianten-"
                   "Quotient Q_E sieht nur die Spitze (dim 1), daher die "
                   "17-Blindheit von Q_E trotz echter Kongruenz. OT-2-KI-"
                   "Beweisziel = genau dieses Nilpotenz-/Jordan-Argument."
                   % (gen_dim, coinv_dim))
    else:
        verdict = ("**Roh-Befund (Interpretationszeile nicht erfuellt).** "
                   "(a)=%d, (b)=%d, (c)=%s, socle_dim=%d. Erwartet war (a)=1, "
                   "(b)>=2, (c)=ja. Abweichung dokumentiert, nicht interpretiert."
                   % (coinv_dim, gen_dim, in_image, socle_dim))

    lines = []
    lines.append("# F17-Strukturtest N=494 (b'''') - Multiplicity-One-Spannung")
    lines.append("")
    lines.append("Autor: LG. Kein abc-Claim. Ambient: `ModularSymbols(%d,2,sign=1)` "
                 "tensor F%d, integrale Struktur, Hecke-Konvention: %s." % (N, ELL, side))
    lines.append("")
    lines.append("## Verdikt")
    lines.append("")
    lines.append(verdict)
    lines.append("")
    lines.append("## Messwerte")
    lines.append("")
    lines.append("| Groesse | Wert | Erwartung |")
    lines.append("|---|---|---|")
    lines.append("| (d) dim M^+ tensor F17 gesamt | %d | 74 |" % d)
    lines.append("| (d) Rang (T_n-a_n)-Stack mod 17 | %d | 73 |" % rank_stack)
    lines.append("| Rang A^T-Stack (Gorenstein-Check) | %d | == %d |" % (rank_stack_T, rank_stack))
    lines.append("| (a) Ko-Invarianten dim | %d | 1 |" % coinv_dim)
    lines.append("| socle dim (geom. Vielfachheit) | %d | 1 |" % socle_dim)
    lines.append("| socle sind echte Eigenvektoren | %s | True |" % socle_is_eigen)
    lines.append("| (b) verallg. m-Eigenraum dim | %d | >= 2 |" % gen_dim)
    lines.append("| (c) socle im Bild Sum(T_n-a_n)M^+ | %s | True |" % in_image)
    lines.append("")
    lines.append("## Deutung der Glieder")
    lines.append("")
    lines.append("- (a)=1: M^+_m ist ueber T_m zyklisch (von 1 Element erzeugt); "
                 "Ko-Invarianten rang 1.")
    lines.append("- (b)>=2: T_m hat Laenge >= 2 - echte 17-Kongruenztiefe (f_E + g "
                 "reduzieren beide in m, Restgrad 1).")
    lines.append("- (a)=1 UND (b)>=2: M^+_m zyklisch, aber T_m KEIN Koerper -> "
                 "Jordan-Block. Der Ko-Invarianten-Quotient sieht nur die "
                 "Jordan-Spitze -> Q_E blind fuer die 17.")
    lines.append("- (c)=ja: der (einzige) Eigenvektor liegt im Bild m*M^+_m -> "
                 "nicht-split (Jordan), konsistent mit (a)=1 & (b)>=2.")
    lines.append("")
    lines.append("Kontext: Befund `_results/ot2prime_minitest_n494_l17_2026-07-10.md` "
                 "(Orbit 4, all-p-Kongruenz mod lam|17); SNF-Q_E=2^4 ohne 17-Torsion.")
    lines.append("")
    lines.append("Laufzeit: %.1f s." % seconds)
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")

    st.update({"phase": "finished", "a_coinv": coinv_dim, "b_gen": gen_dim,
               "c_in_image": in_image, "socle_dim": socle_dim,
               "interpretation_nonsplit_confirmed": interp_nonsplit})
    log(st, args.status_json)

    print(json.dumps({
        "a_coinvariants_dim": coinv_dim,
        "b_generalized_eigenspace_dim": gen_dim,
        "c_socle_in_image": in_image,
        "socle_dim": socle_dim,
        "socle_is_joint_eigenvector": socle_is_eigen,
        "dim_total": d, "rank_stack_mod_ell": rank_stack,
        "gorenstein_ranks_equal": bool(rank_stack == rank_stack_T),
        "interpretation_nonsplit_confirmed": interp_nonsplit,
        "seconds": seconds,
    }, ensure_ascii=False, default=_json_default))


if __name__ == "__main__":
    main()
