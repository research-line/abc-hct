#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""merel_invariant_gauge_n109.py -- v1 (2026-07-10)

Symplektische Eichung: existiert ein KANONISCHES Klassen-Zertifikat fuer die
Nichtverschwindung von phi'(r_N)? Reformuliert die Allowance-Korrektur als
Vektor-Raum-Objekt W_I und testet, ob B auf W_I nicht-degeneriert ist
(symplektisches Komplement -> kanonische Projektion pi -> eichinvariante
Auswertung inv := phi'(pi(r_N))).

Baut UNVERAENDERT auf merel_delta_allowance_n109.py (v3 / interne version 4)
auf. Uebernommen (Objekt-Konstruktion identisch, Funktionen mit Quellkommentar
kopiert; v3 NICHT veraendert):
  - Witness-Bridge nach M0 (I-Orbit-Mittelung, q=3863)
  - Paarung B = A^-T * Bsym * A^-1 (Petersson-Pullback via mseval-Dualitaet),
    selbstadjungiert + alternierend
  - 26 Source-Zeilen (18 manin_T + 8 T5-Batch) + Repair-Zeile r_N aus
    mixed_rows.jsonl
  - volle T7-Restlinien-Allowance-Familie {A_c = B((T7-a7)e_c, -)}
  - der v3-phi'-Solve (voller full_t7res-Pfad, deterministischer solve_right)
  - N(S)-Schnitt-Zeugnis psi

Spec (Session team-lead "symplektische Eichung N=109", 2026-07-10), exakt:
  1. W_A := Span_F{ w_c := (T7-a7)*e_c : c Witness-Spalte } als VEKTOREN in M0.
     Reporte dim W_A und dim(W_A mod ker B).
  2. W_I := { w in W_A : B(w,s)=0 fuer alle 26 Source-Zeilen s }.
     Vektor-Gegenstueck zu I = N(S) cap Allowance-Span. Match-Check gegen den
     v3-Schnitt (Dimension + gegenseitige Enthaltenseins-Checks). Erwartet:
     dim(mod ker B) = 2.
  3. Gram g := B(u1,u2) auf Basis u1,u2 von W_I (mod ker B); Verdikt
     WI_symplectic_nondegenerate := (g != 0).
  4. Kanonische Projektion (nur falls g!=0):
     pi(v) := v - [B(u2,v)/B(u2,u1)]*u1 - [B(u1,v)/B(u1,u2)]*u2.
     Basisfreiheit numerisch: 2. zufaellig transformierte W_I-Basis ->
     pi(r_N) muss identisch sein.
  5. inv := phi'(pi(r_N)) fuer den v3-Loesungsrepraesentanten phi'.
  6. Invarianz-Selbsttest (Pflicht): fuer mehrere zufaellige w in W_I sei
     phi'' := phi' + B(w,-). Es MUSS phi''(pi(r_N)) == inv gelten UND fuer
     mind. ein w phi''(r_N) != phi'(r_N) (Negativkontrolle). Zusaetzlich:
     pi(r_N) in W_I^perpB (B(u,pi(r_N))=0 fuer u=u1,u2).
  7. Schritte 1-6 fuer BEIDE a_p-Konventionen (standard a5=3/a7=2;
     frey a5=2/a7=0).
  8. Optional (billig): rank Span{B((T_l-a_l)e_c,-)} fuer l in {7,11,13}.

Auftragserweiterung (team-lead, CFR-Beweistext-Audit 2026-07-10):
  - inv_q7 := phi'(pi(h7e0)) mit h7e0 = 2e0+e1+...+e6 (Fan-Kombi der
    Witness-Spalten 0-6, M0-Koord. via derselben Bridge). Nur falls g!=0
    kanonisch (sonst n/a, wie inv fuer r_N). Zusaetzlich IMMER berechnet:
    q7_ungauged = phi'(h7e0) (v3-Soll "Q7"=0), q7_ungauged_T7e0 = phi'(T7 e0).
  - N(S)-Landkarte: (psi(r_N), psi(h7e0)) pro Basisvektor von N(S) (dim 9)
    -> welche Annihilator-Loesungen tragen die CFR-5-Eigenschaft (!=0 auf
    h7e0), und ist r_N-/h7e0-Sichtbarkeit entkoppelt? Entscheidend:
    h7e0_in_source_span <=> psi(h7e0)=0 fuer ALLE psi (Fall 3).
  - I-Basis-Auswertung psi_q7_*: war Q7=0 eich-abhaengig (Allowance-Eichung)?
  - verdict_cfr5: 3-Fall-Interpretation (siehe interpret_cfr5).

Hinweis q'=5077 (Spec Punkt 7, optional): NICHT durchgefuehrt. Die
Witness-Zeilen in mixed_rows.jsonl sind bereits als GF(3863)-Residuen
gespeichert (z.B. Wert 3862 = -1 mod 3863), nicht als Rohintegers. Ein
Reduzieren dieser Residuen mod 5077 waere mathematisch falsch (3862 waere
dort nicht -1). Ein faithful q'-Rerun braeuchte die Roh-Integer-Zeilen aus
dem Zertifikatsgenerator, die in diesem Artefakt nicht vorliegen.

Referenz-Sollwerte (Selbstvalidierung, Standard-a_p-Konvention):
  phi'(r_N)=1772, psi(r_N)=687, dim(N(S) cap Allowance)=2, Allowance-Rang 8.
  Frey-Konvention: phi'(r_N)=-1065 (= 2798 mod 3863).

Nur-lesend gegenueber Registern; schreibt NUR _results/-Artefakte.
"""

import json
import time
from pathlib import Path

from sage.all import (EllipticCurve, GF, Gamma0, ModularSymbols, QQ,
                      identity_matrix, matrix, pari, set_random_seed, vector)

t0 = time.time()
N = 109
OUTDATE = "2026-07-10"
CASE_DIR = Path("_results/h3a_wait_postprocess_smoke_n109_2026-05-16/"
                "N109_raw_sign1_splitlast")

# Referenz-Sollwerte fuer die Selbstvalidierung (aus v3-Laeufen 2026-07-02).
REF_STD_PHI_RN = 1772
REF_STD_PSI_RN = 687
REF_STD_INTER = 2
REF_STD_ALLOW_RANK = 8
REF_STD_PHI_VEC = [0, -1068, -462, -1305, -1644, 511, 1909, -130, 18, 0,
                   -789, 345, -1708, 511, -1398, -72, 0]
REF_FREY_PHI_RN = -1065

out = {
    "tool": "merel_invariant_gauge_n109",
    "version": 1,
    "date": OUTDATE,
    "N": N,
    "spec_session": "team-lead symplektische Eichung N=109 (2026-07-10)",
    "builds_on": "merel_delta_allowance_n109.py (v3 / version 4)",
    "q_prime_5077_note": ("SKIPPED: mixed_rows.jsonl-Zeilen sind GF(3863)-"
                          "Residuen, kein Rohinteger -> mod-5077-Reduktion "
                          "waere falsch (3862 != -1 mod 5077)."),
}

# ==========================================================================
# QQ-Objekte (Konvention- UND q-unabhaengig) -- verbatim aus v3
# ==========================================================================
M0 = ModularSymbols(Gamma0(N), 2, sign=0)
n0 = int(M0.dimension())
out["n0"] = n0
E = EllipticCurve("109a1")

pp = pari.msinit(N, 2)
assert int(pari.msdim(pp)) == n0, "msdim != Sage dim"
Bsym = matrix(QQ, n0, n0, [[QQ(pari.mspetersson(pp)[i][j]) for j in range(n0)]
                           for i in range(n0)])


def gen_path(bi):
    g = M0.manin_generators()[bi]
    a, b, c, d = [int(x) for x in g.lift_to_sl2z()]
    p0 = pari("oo") if d == 0 else pari(QQ(b) / QQ(d))
    p1 = pari("oo") if c == 0 else pari(QQ(a) / QQ(c))
    return [p0, p1]


basis_gens = list(M0.manin_basis())
A = matrix(QQ, n0, n0)
for i, bi in enumerate(basis_gens):
    path = gen_path(bi)
    for j in range(n0):
        ej = pari(vector(QQ, [1 if k == j else 0
                              for k in range(n0)]).list()).mattranspose()
        val = pari.mseval(pp, ej, path)
        A[i, j] = QQ(val[0]) if hasattr(val, "__len__") and len(val) else QQ(val)
assert A.rank() == n0, "Transfer-Matrix nicht invertierbar"
Ai = A.inverse()
B_QQ = Ai.transpose() * Bsym * Ai
T5_QQ = M0.hecke_matrix(5)
T7_QQ = M0.hecke_matrix(7)
eis_QQ = [b.element() for b in M0.eisenstein_submodule().basis()]
ap_curve = {ell: int(E.ap(ell)) for ell in (5, 7, 11, 13)}
out["ap_curve_109a1"] = ap_curve


def redw_field(Fw, mat):
    """Dichte Reduktion einer QQ-Matrix nach Fw (wie v3.redw)."""
    return matrix(Fw, mat.nrows(), mat.ncols(),
                  {(i, j): Fw(v) for (i, j), v in mat.dict().items()},
                  sparse=True)


# ==========================================================================
# mod-q-Objekte (Bridge, Sources, r_N, phi) -- verbatim aus v3
# ==========================================================================
def build_mod_q(qw):
    Fw = GF(qw)
    B = redw_field(Fw, B_QQ)
    T5w = redw_field(Fw, T5_QQ)
    T7w = redw_field(Fw, T7_QQ)
    Ww = redw_field(Fw, M0.atkin_lehner_operator(N).matrix())
    Idm = identity_matrix(Fw, n0)

    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
    from sage.modular.modsym.relation_matrix import (modI_relations,
                                                     modS_relations,
                                                     sparse_2term_quotient)
    manifest = json.loads((CASE_DIR / "manifest.json").read_text(encoding="utf-8"))
    ncols = int(manifest["ncols"])
    syms = ManinSymbolList_gamma0(N, 2)
    rels = set(modS_relations(syms))
    rels.update(modI_relations(syms, 1))
    mod = sparse_2term_quotient(rels, len(syms), Fw)
    g2b = M0.manin_gens_to_basis()
    g2b_F = matrix(Fw, [[Fw(v) for v in g2b.row(j)] for j in range(g2b.nrows())])
    rep_to_col, cls = {}, {}
    for j, entry in enumerate(mod):
        rep, scalar = entry
        if scalar == 0:
            continue
        rep_i = int(rep)
        if rep_i not in rep_to_col:
            rep_to_col[rep_i] = len(rep_to_col)
        cls.setdefault(rep_to_col[rep_i], []).append((j, Fw(scalar)))
    col_to_m0 = {}
    for col, members in cls.items():
        if col < ncols:
            acc = vector(Fw, n0)
            for j, scalar in members:
                acc += scalar * g2b_F.row(j)
            col_to_m0[col] = acc / Fw(len(members))

    def row_to_m0(rowpairs):
        v = vector(Fw, n0)
        for col, value in rowpairs:
            c = int(col)
            if c in col_to_m0:
                v += Fw(int(value)) * col_to_m0[c]
        return v

    rows_path = CASE_DIR / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    target = manifest.get("repair_only_row_id")
    sources, r_m0 = [], None
    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("origin") == "source":
            sources.append((row["row_id"], row_to_m0(row["row"])))
        elif row.get("origin") == "repair_only" and row.get("row_id") == target:
            r_m0 = row_to_m0(row["row"])
    assert r_m0 is not None, "Repair-Zeile nicht gefunden"

    kerB = B.right_kernel()
    ker_basis = kerB.basis()
    k_w = ker_basis[0] if ker_basis else vector(Fw, n0)
    try:
        eis_row = vector(Fw, [Fw(x) for x in eis_QQ[0]])
    except (ZeroDivisionError, TypeError):
        eis_row = None
    phi = B * r_m0

    def signed(x):
        xi = int(x)
        return xi - qw if xi > qw // 2 else xi

    return dict(Fw=Fw, qw=qw, B=B, T5w=T5w, T7w=T7w, Ww=Ww, Idm=Idm,
                col_to_m0=col_to_m0, sources=sources, r_m0=r_m0, phi=phi,
                k_w=k_w, eis_row=eis_row, signed=signed, kerB=kerB,
                bridged_cols=len(col_to_m0))


# ==========================================================================
# v3-Helfer (verbatim aus merel_delta_allowance_n109.py, parametrisiert)
# ==========================================================================
def span_solve_eval(Fw, funcs, rows, rhs_vals):
    names = list(funcs.keys())
    Mx = matrix(Fw, [[funcs[n] * s for s in rows] for n in names]).transpose()
    b = vector(Fw, rhs_vals)
    res = {"names": names, "system_rank": int(Mx.rank())}
    try:
        sol = Mx.solve_right(b)
        res["solvable"] = True
        res["_sol"] = sol
        res["_kernel"] = Mx.right_kernel().basis()
    except ValueError:
        res["solvable"] = False
    return res


def phi_prime_from(phi, funcs, res):
    """Sucht im Loesungsraum ein c mit phi' = phi - sum c_i A_i != 0
    (v3-Determinismus: erst Partikulaerloesung, dann Kernel-Shifts)."""
    if not res.get("solvable"):
        return None
    names = res["names"]

    def build(sol):
        return phi - sum(c * funcs[n] for c, n in zip(sol, names))

    cands = [res["_sol"]] + [res["_sol"] + d for d in res["_kernel"]]
    for sol in cands:
        pp_ = build(sol)
        if not pp_.is_zero():
            return sol, pp_
    return None


def v3_ns_witness(Fw, funcs, NS, r_m0, T7w, e0, signed):
    """Reproduziert das v3-T4-Schnitt-Zeugnis (allowance cap N(S)):
    erstes nicht-triviales Element, dessen psi_rN gegen 687/-1552 gated."""
    names = list(funcs.keys())
    span_m = matrix(Fw, [list(funcs[n]) for n in names])
    psi_basis = NS.basis()
    ns_m = matrix(Fw, [list(p) for p in psi_basis])
    stacked = span_m.stack(ns_m)
    inter_dim = int(span_m.rank() + ns_m.rank() - stacked.rank())
    res = {"inter_dim": inter_dim, "psi_rN": None}
    if inter_dim > 0:
        aug = span_m.transpose().augment(-ns_m.transpose())
        for kv in aug.right_kernel().basis():
            c_part = kv[:len(names)]
            cand = sum(c * funcs[n] for c, n in zip(c_part, names))
            v = vector(Fw, cand)
            if not v.is_zero():
                res["psi_rN"] = signed(v * r_m0)
                res["Q7"] = signed(v * (T7w * e0))
                # Zeugnis liegt per Konstruktion in N(S) (aug-Kernel-Element).
                break
    return res


# ==========================================================================
# Interpretation (Spec-Zeilen fuers MD)
# ==========================================================================
def interpret(g, inv):
    if g is not None and g != 0 and inv is not None and inv != 0:
        return ("g!=0 und inv!=0: kanonisches Nichtverschwindens-Zertifikat auf "
                "Klassen-Ebene EXISTIERT (symplektische Eichung); gate_invariant-"
                "Luecke geschlossen im geeichten Sinn. KEIN abc-Claim.")
    if g is not None and g != 0 and inv == 0:
        return ("g!=0 und inv=0: Nichtverschwindung von phi'(r_N) lebte "
                "vollstaendig in der Eich-Ambiguitaet; Klassen-Zertifikat in "
                "dieser Form NICHT existent -- integrale Normalisierungs-Route "
                "wird Pflicht.")
    return ("g=0: W_I isotrop; symplektische Eichung nicht kanonisch verfuegbar "
            "-- Befund dokumentieren, integrale Route.")


def cfr5_case(target, inv_val, exists_psi, in_source_span, coupled_to_rN):
    if inv_val is not None and inv_val != 0:
        return (f"inv != 0: CFR-5-Zertifikat ({target} trifft Restlinie) "
                "existiert kanonisch in der geeichten B_N-Lesart.")
    if in_source_span:
        return (f"psi({target})=0 fuer ALLE psi in N(S) ({target} liegt "
                "klassen-eben im Span der Source-Zeilen) -- ERNSTER "
                "Struktur-Befund gegen CFR-5 bei N=109 in der Witness-Lesart; "
                "sofort zurueckmelden.")
    if exists_psi:
        base = (f"inv_Q7 kanonisch n/a (g=0) bzw. =0, ABER es existiert psi in "
                f"N(S) mit psi({target})!=0: die B_N-erzeugte Loesungsschar "
                f"trifft {target} nicht, doch der Loesungsraum enthaelt "
                "CFR-5-taugliche Funktionale -- Konstruktions- vs. "
                "Existenzfrage TRENNEN (B_N-Route ist fuers CFR-5-Gate die "
                "falsche Auswahlvorschrift).")
        if coupled_to_rN:
            base += (f" ZUSATZ: {target}-Detektion ist MAXIMAL an r_N gekoppelt "
                     "(Detektions-Bild dim 1, festes Verhaeltnis) -- kein von "
                     "r_N unabhaengiges Zertifikat.")
        return base
    return "CFR-5: unklassifiziert (Werte pruefen)."


# ==========================================================================
# Haupt-Routine pro Konvention
# ==========================================================================
def run_convention(o, a5, a7, tag):
    Fw = o["Fw"]
    B = o["B"]
    T7w = o["T7w"]
    Idm = o["Idm"]
    col_to_m0 = o["col_to_m0"]
    sources = o["sources"]
    r_m0 = o["r_m0"]
    phi = o["phi"]
    k_w = o["k_w"]
    eis_row = o["eis_row"]
    signed = o["signed"]
    kerB = o["kerB"]
    qw = o["qw"]
    Fn = Fw ** n0
    R = {"tag": tag, "a5": a5, "a7": a7, "qw": qw}
    all_rows = [s for _, s in sources]
    e0 = col_to_m0[0]
    Smat = matrix(Fw, [list(s) for _, s in sources])

    # ---- v3-phi' (voller full_t7res-Pfad, EXAKT reproduziert) ----
    t7res_family = {}
    for c, ec in sorted(col_to_m0.items()):
        fvec = B * ((T7w - Fw(a7) * Idm) * ec)
        if not fvec.is_zero():
            t7res_family[f"A_T7res_e{c}"] = fvec
    allow_full = dict(t7res_family)
    allow_full["E_ker"] = k_w
    if eis_row is not None:
        allow_full["E_row_eis"] = eis_row
    rc = span_solve_eval(Fw, allow_full, all_rows, [phi * s for s in all_rows])
    found = phi_prime_from(phi, allow_full, rc)
    assert found is not None, "phi' nicht gefunden (Solve nicht loesbar)"
    _sol, phi_p = found
    R["phi_prime_rN"] = signed(phi_p * r_m0)
    R["phi_prime_annihilates_all26"] = bool(all(phi_p * s == 0 for s in all_rows))
    R["phi_prime_vector_signed"] = [signed(x) for x in phi_p]
    R["allowance_rank"] = int(matrix(
        Fw, [list(v) for v in t7res_family.values()]).rank())

    # ---- Schritt 1: W_A ----
    w_cols = [(T7w - Fw(a7) * Idm) * ec for _, ec in sorted(col_to_m0.items())]
    WA = Fn.subspace(w_cols)
    BWA = Fn.subspace([B * w for w in w_cols])
    R["dim_WA"] = int(WA.dimension())
    R["dim_WA_mod_kerB"] = int(BWA.dimension())

    # ---- Schritt 2: W_I ----
    # annih = {w : (Smat*B) w = 0} = {w : s^T B w = 0 forall s}
    #       = {w : B(w,s)=0 forall s}  (B alternierend)
    annih = (Smat * B).right_kernel()
    WI = WA.intersection(annih)
    WI_cap_ker = WI.intersection(kerB)
    R["dim_WI"] = int(WI.dimension())
    R["dim_WI_cap_kerB"] = int(WI_cap_ker.dimension())
    R["dim_WI_mod_kerB"] = int(WI.dimension() - WI_cap_ker.dimension())
    WIb = list(WI.basis())
    BWI = (Fn.subspace([B * b for b in WIb]) if WIb
           else Fn.subspace([Fn.zero()]))
    R["dim_BWI"] = int(BWI.dimension())

    # Match gegen v3-Schnitt
    NS = Smat.right_kernel()               # {f : s.f = 0 forall s}
    R["NS_dim"] = int(NS.dimension())
    full_span = Fn.subspace(list(allow_full.values()))
    v3_inter = full_span.intersection(NS)
    pure_inter = BWA.intersection(NS)
    R["dim_v3_inter"] = int(v3_inter.dimension())
    R["dim_pure_BWA_cap_NS"] = int(pure_inter.dimension())
    R["match_BWI_eq_pure_BWAcapNS"] = bool(BWI == pure_inter)
    R["match_BWI_subset_v3"] = bool(BWI.is_subspace(v3_inter))
    R["match_v3_subset_BWI"] = bool(v3_inter.is_subspace(BWI))
    R["match_BWI_eq_v3"] = bool(BWI == v3_inter)

    # v3-Schnitt-Zeugnis (psi_rN-Gate)
    R["v3_ns_witness"] = v3_ns_witness(Fw, allow_full, NS, r_m0, T7w, e0, signed)

    # ---- Schritt 3: Gram ----
    d = len(WIb)
    Gram = matrix(Fw, [[WIb[i] * (B * WIb[j]) for j in range(d)]
                       for i in range(d)])
    R["WI_gram_signed"] = [[signed(Gram[i, j]) for j in range(d)]
                           for i in range(d)]
    R["WI_gram_rank"] = int(Gram.rank())
    # symplektisches Paar (u1,u2): erstes B(u1,u2)!=0
    u1 = u2 = None
    gval = Fw(0)
    for i in range(d):
        for j in range(d):
            if Gram[i, j] != 0:
                u1, u2, gval = WIb[i], WIb[j], Gram[i, j]
                break
        if u1 is not None:
            break
    R["WI_symplectic_nondegenerate"] = bool(u1 is not None and gval != 0)
    R["g"] = signed(gval) if u1 is not None else 0

    # ---- Eich-Ambiguitaets-Diagnostik (immer, unabhaengig von g) ----
    # Wirkt die (reine T7-Restlinien-)Eichfreiheit B(w,-), w in W_I,
    # nichttrivial auf phi'(r_N)? -> zeigt, dass phi'(r_N)=1772 eich-abhaengig
    # ist. B(w,r_N) = w . (B r_N). ker-B-Richtungen paaren zwangslaeufig 0.
    R["WI_basis_diag"] = [
        {"in_kerB": bool(wb in kerB), "B_w_rN": signed(wb * (B * r_m0))}
        for wb in WIb
    ]
    gauge_shift_vals = [signed((phi_p + B * wb) * r_m0) for wb in WIb]
    R["gauge_shifted_phiprime_rN"] = gauge_shift_vals
    R["gauge_freedom_nontrivial_on_rN"] = bool(
        any(v != R["phi_prime_rN"] for v in gauge_shift_vals))

    # ---- CFR-5-Erweiterung: h7(e0) + N(S)-Landkarte (immer berechnet) ----
    # h7e0 = 2 e0 + e1 + ... + e6 (Fan-Kombi der Witness-Spalten 0-6, M0-Koord.,
    # via derselben Bridge wie r_N). ACHTUNG: NICHT identisch mit T7*e0 (dem
    # v3-"Q7"-Traeger) -- beide Lesarten werden parallel gerechnet.
    assert all(c in col_to_m0 for c in range(7)), "Fan-Spalten 0-6 fehlen"
    h7e0 = (2 * col_to_m0[0] + col_to_m0[1] + col_to_m0[2] + col_to_m0[3]
            + col_to_m0[4] + col_to_m0[5] + col_to_m0[6])
    T7e0 = T7w * e0
    R["q7_ungauged"] = signed(phi_p * h7e0)       # phi'(h7e0), Fan-Lesart
    R["q7_ungauged_T7e0"] = signed(phi_p * T7e0)  # phi'(T7 e0) = v3-"Q7"
    R["h7e0_eq_T7e0"] = bool(h7e0 == T7e0)         # Fan-Kombi == T7 e0 ?

    # Rang-Leiter: liegt h7e0 (bzw. T7e0) im Span(Sources) bzw. Span(Sources,r_N)?
    # rank(S,rN,X)=rank(S,rN) <=> X in Span(S,rN) <=> X klassen-aequiv. zu
    # Skalar*r_N mod Sources (=> KEINE unabhaengige CFR-5-Information).
    src_vecs = [s for _, s in sources]
    src_space = Fn.subspace(src_vecs)
    S_rN = Fn.subspace(src_vecs + [r_m0])
    R["source_span_dim"] = int(src_space.dimension())            # rank_S
    R["rank_S_plus_rN"] = int(S_rN.dimension())
    R["rank_S_plus_rN_plus_h7e0"] = int(
        Fn.subspace(src_vecs + [r_m0, h7e0]).dimension())
    R["rank_S_plus_rN_plus_T7e0"] = int(
        Fn.subspace(src_vecs + [r_m0, T7e0]).dimension())
    R["h7e0_in_source_span"] = bool(h7e0 in src_space)
    R["T7e0_in_source_span"] = bool(T7e0 in src_space)
    R["rN_in_source_span"] = bool(r_m0 in src_space)
    R["h7e0_in_S_plus_rN"] = bool(h7e0 in S_rN)   # True => an r_N gekoppelt
    R["T7e0_in_S_plus_rN"] = bool(T7e0 in S_rN)

    # N(S)-Landkarte: (psi(r_N), psi(h7e0), psi(T7e0)) pro Basisvektor (dim 9)
    ns_basis = list(NS.basis())
    R["ns_landkarte"] = [
        {"psi_rN": signed(psi * r_m0), "psi_h7e0": signed(psi * h7e0),
         "psi_T7e0": signed(psi * T7e0)}
        for psi in ns_basis
    ]
    R["exists_psi_detecting_h7e0"] = bool(any(psi * h7e0 != 0 for psi in ns_basis))
    R["exists_psi_detecting_T7e0"] = bool(any(psi * T7e0 != 0 for psi in ns_basis))
    R["exists_psi_detecting_rN"] = bool(any(psi * r_m0 != 0 for psi in ns_basis))
    # Entkopplung: Dimension des Bildes psi -> (psi(r_N), psi(h7e0)) in F^2.
    # dim 1 => r_N- und h7e0-Sichtbarkeit maximal gekoppelt (festes Verhaeltnis).
    img_pairs = matrix(Fw, [[psi * r_m0, psi * h7e0] for psi in ns_basis])
    R["ns_detection_image_dim_rN_h7e0"] = int(img_pairs.rank())

    # I-Basis-Auswertung: bewegt die Allowance-Eichung phi'(h7e0)? (war Q7
    # eich-abhaengig?) -- reine I = B(W_I) (dim 1) und v3-Schnitt (dim 2).
    R["psi_q7_pure_I"] = [
        {"iota_rN": signed(iota * r_m0), "iota_h7e0": signed(iota * h7e0),
         "iota_T7e0": signed(iota * T7e0)}
        for iota in BWI.basis()
    ]
    R["psi_q7_v3_I"] = [
        {"iota_rN": signed(iota * r_m0), "iota_h7e0": signed(iota * h7e0),
         "iota_T7e0": signed(iota * T7e0)}
        for iota in v3_inter.basis()
    ]
    R["allowance_gauge_moves_q7"] = bool(
        any(iota * h7e0 != 0 for iota in BWI.basis()))
    R["allowance_gauge_moves_q7_T7e0"] = bool(
        any(iota * T7e0 != 0 for iota in BWI.basis()))

    # ---- Schritte 4-6 (nur falls g!=0) ----
    if u1 is not None and gval != 0:
        g12 = u1 * (B * u2)     # B(u1,u2)
        g21 = u2 * (B * u1)     # B(u2,u1) = -g12

        def proj(v, a1, a2):
            gg12 = a1 * (B * a2)
            gg21 = a2 * (B * a1)
            return (v - ((a2 * (B * v)) / gg21) * a1
                      - ((a1 * (B * v)) / gg12) * a2)

        prN = proj(r_m0, u1, u2)

        # Basisfreiheit: 5 zufaellige GL2-Transformationen von (u1,u2)
        set_random_seed(20260710)
        basis_free = True
        for _ in range(5):
            while True:
                al, be, ga, de = (Fw.random_element() for _ in range(4))
                if al * de - be * ga != 0:
                    break
            u1p = al * u1 + be * u2
            u2p = ga * u1 + de * u2
            if proj(r_m0, u1p, u2p) != prN:
                basis_free = False
        R["pi_basis_free"] = bool(basis_free)

        # pi(r_N) in W_I^perpB ?  (B(u, pi(r_N)) = u . (B pi(r_N)) = 0)
        R["piRN_in_WIperp"] = bool(all((wb * (B * prN)) == 0 for wb in WIb))

        # inv := phi'(pi(r_N))
        inv = signed(phi_p * prN)
        R["inv"] = inv
        R["piRN_signed"] = [signed(x) for x in prN]

        # inv_Q7: dieselbe symplektische Eichung auf h7e0 angewandt
        prQ7 = proj(h7e0, u1, u2)
        inv_q7 = signed(phi_p * prQ7)
        R["inv_q7"] = inv_q7
        R["piQ7_in_WIperp"] = bool(all((wb * (B * prQ7)) == 0 for wb in WIb))
        R["piQ7_signed"] = [signed(x) for x in prQ7]

        # Eich-Ambiguitaet der ALTEN Auswertung: B(w, r_N) fuer Basis w in W_I
        R["gauge_ambiguity_on_rN"] = [signed(wb * (B * r_m0)) for wb in WIb]

        # ---- Schritt 6: Invarianz-Selbsttest ----
        set_random_seed(424242)
        inv_holds = True
        inv_q7_holds = True
        neg_control = False
        neg_control_q7 = False
        annih_ok = True
        samples = []
        for _ in range(6):
            coeffs = [Fw.random_element() for _ in range(d)]
            w = sum((c * b for c, b in zip(coeffs, WIb)), Fn.zero())
            gw = B * w                      # Funktional-Vektor: (gw . x) = B(x,w)
            phi_pp = phi_p + gw
            iv = signed(phi_pp * prN)
            iv_q7 = signed(phi_pp * prQ7)
            at_rN = signed(phi_pp * r_m0)
            at_q7 = signed(phi_pp * h7e0)
            ann = bool(all(phi_pp * s == 0 for s in all_rows))
            if iv != inv:
                inv_holds = False
            if iv_q7 != inv_q7:
                inv_q7_holds = False
            if at_rN != R["phi_prime_rN"]:
                neg_control = True
            if at_q7 != R["q7_ungauged"]:
                neg_control_q7 = True
            if not ann:
                annih_ok = False
            samples.append({"inv_eval": iv, "inv_q7_eval": iv_q7,
                            "at_rN": at_rN, "at_h7e0": at_q7,
                            "annihilates": ann})
        R["selftest_invariance_holds"] = bool(inv_holds)
        R["selftest_invariance_q7_holds"] = bool(inv_q7_holds)
        R["selftest_negcontrol_changes_rN"] = bool(neg_control)
        R["selftest_negcontrol_changes_h7e0"] = bool(neg_control_q7)
        R["selftest_phipp_annihilates_sources"] = bool(annih_ok)
        R["selftest_samples"] = samples
    else:
        R["inv"] = None
        R["inv_q7"] = None

    R["verdict_line"] = interpret(R.get("g"), R.get("inv"))
    R["verdict_cfr5"] = cfr5_case(
        "h7e0", R.get("inv_q7"), R["exists_psi_detecting_h7e0"],
        R["h7e0_in_source_span"],
        R.get("ns_detection_image_dim_rN_h7e0") == 1)
    R["verdict_cfr5_T7e0"] = cfr5_case(
        "T7e0", None, R["exists_psi_detecting_T7e0"],
        R["T7e0_in_source_span"], False)
    return R


# ==========================================================================
# Optional (Schritt 8): l-Restlinien-Familien-Raenge (Standard-a_l)
# ==========================================================================
def l_family_ranks(o, ells):
    Fw = o["Fw"]
    B = o["B"]
    Idm = o["Idm"]
    col_to_m0 = o["col_to_m0"]
    ranks = {}
    for ell in ells:
        Tlw = redw_field(Fw, M0.hecke_matrix(ell))
        a_ell = Fw(ap_curve[ell])
        fam = []
        for _, ec in sorted(col_to_m0.items()):
            fv = B * ((Tlw - a_ell * Idm) * ec)
            if not fv.is_zero():
                fam.append(fv)
        rank = int(matrix(Fw, [list(v) for v in fam]).rank()) if fam else 0
        ranks[f"l={ell}"] = {"a_l": ap_curve[ell], "family_size": len(fam),
                             "rank": rank}
    return ranks


# ==========================================================================
# Lauf
# ==========================================================================
o = build_mod_q(3863)
out["primary_field_q"] = o["qw"]
out["bridged_cols"] = o["bridged_cols"]
out["B_kernel_dim_mod_q"] = int(o["kerB"].dimension())

conv_std = run_convention(o, a5=3, a7=2, tag="standard")
conv_frey = run_convention(o, a5=2, a7=0, tag="frey")
out["conventions"] = {"standard": conv_std, "frey": conv_frey}

# Optionaler l-Familien-Rang-Datenpunkt (Standard-a_l)
out["l_family_ranks_standard_ap"] = l_family_ranks(o, (7, 11, 13))

# ---- Selbstvalidierung gegen Referenz-Sollwerte ----
val = {
    "standard_phi_prime_rN": conv_std["phi_prime_rN"],
    "standard_phi_prime_rN_ref": REF_STD_PHI_RN,
    "standard_psi_rN": conv_std["v3_ns_witness"].get("psi_rN"),
    "standard_psi_rN_ref": REF_STD_PSI_RN,
    "standard_dim_v3_inter": conv_std["dim_v3_inter"],
    "standard_dim_v3_inter_ref": REF_STD_INTER,
    "standard_allowance_rank": conv_std["allowance_rank"],
    "standard_allowance_rank_ref": REF_STD_ALLOW_RANK,
    "standard_phi_vec_matches_ref":
        conv_std["phi_prime_vector_signed"] == REF_STD_PHI_VEC,
    "frey_phi_prime_rN": conv_frey["phi_prime_rN"],
    "frey_phi_prime_rN_ref": REF_FREY_PHI_RN,
}
val["PASS"] = bool(
    val["standard_phi_prime_rN"] == REF_STD_PHI_RN
    and val["standard_psi_rN"] == REF_STD_PSI_RN
    and val["standard_dim_v3_inter"] == REF_STD_INTER
    and val["standard_allowance_rank"] == REF_STD_ALLOW_RANK
    and val["standard_phi_vec_matches_ref"]
    and val["frey_phi_prime_rN"] == REF_FREY_PHI_RN
)
out["self_validation"] = val

out["seconds"] = round(time.time() - t0, 1)

out_json = Path(f"_results/merel_invariant_gauge_n109_{OUTDATE}.json")
out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2),
                    encoding="utf-8")

# Kompakte Konsolen-Zusammenfassung
print(json.dumps({
    "self_validation_PASS": val["PASS"],
    "self_validation": val,
    "standard": {k: conv_std.get(k) for k in
                 ("dim_WA", "dim_WA_mod_kerB", "dim_WI", "dim_WI_mod_kerB",
                  "dim_WI_cap_kerB", "dim_BWI", "dim_v3_inter",
                  "dim_pure_BWA_cap_NS", "match_BWI_eq_pure_BWAcapNS",
                  "match_BWI_eq_v3", "WI_gram_rank", "g",
                  "WI_symplectic_nondegenerate",
                  "gauge_shifted_phiprime_rN", "gauge_freedom_nontrivial_on_rN",
                  "inv", "inv_q7", "q7_ungauged", "q7_ungauged_T7e0",
                  "h7e0_eq_T7e0", "source_span_dim", "rank_S_plus_rN",
                  "rank_S_plus_rN_plus_h7e0", "rank_S_plus_rN_plus_T7e0",
                  "h7e0_in_source_span", "h7e0_in_S_plus_rN",
                  "T7e0_in_source_span", "exists_psi_detecting_h7e0",
                  "exists_psi_detecting_T7e0", "exists_psi_detecting_rN",
                  "ns_detection_image_dim_rN_h7e0",
                  "allowance_gauge_moves_q7", "psi_q7_pure_I", "ns_landkarte",
                  "selftest_invariance_holds", "verdict_line",
                  "verdict_cfr5", "verdict_cfr5_T7e0")},
    "frey": {k: conv_frey.get(k) for k in
             ("dim_WA", "dim_WA_mod_kerB", "dim_WI", "dim_WI_mod_kerB",
              "dim_BWI", "dim_v3_inter", "dim_pure_BWA_cap_NS",
              "match_BWI_eq_pure_BWAcapNS", "match_BWI_eq_v3", "WI_gram_rank",
              "g", "WI_symplectic_nondegenerate",
              "gauge_freedom_nontrivial_on_rN", "inv", "inv_q7",
              "q7_ungauged", "q7_ungauged_T7e0", "h7e0_eq_T7e0",
              "rank_S_plus_rN_plus_h7e0", "rank_S_plus_rN_plus_T7e0",
              "h7e0_in_source_span", "h7e0_in_S_plus_rN",
              "exists_psi_detecting_h7e0", "exists_psi_detecting_T7e0",
              "ns_detection_image_dim_rN_h7e0", "allowance_gauge_moves_q7",
              "psi_q7_pure_I", "ns_landkarte", "verdict_line",
              "verdict_cfr5", "verdict_cfr5_T7e0")},
    "l_family_ranks": out["l_family_ranks_standard_ap"],
    "seconds": out["seconds"],
}, ensure_ascii=False, indent=2))
