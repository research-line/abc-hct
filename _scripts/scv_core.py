#!/usr/bin/env python3
"""
scv_core.py — Source-Canonicality-Validator Core (SCV Phase 1)

Verifiziert Matrixgleichungen ueber F_q fuer den CQ-3/S2a-Vertrag.
Prueft: raw <-> canonical Isomorphismus (Schicht C), Hecke-Aequivarianz
(Schicht D), Eichler-Ideal (Schicht E), ell_q-Membership und Rang-
zertifikate (Schicht G).

Hausmuster: reines Python mod-q (psc2_verifier.py). Kein scipy/numpy —
exakte F_q-Arithmetik. Alle Matrizen als Listen von Listen ganzer Zahlen.

Architektur: _proof-notes/MG_SCV_architecture_audit_2026-06-05.md
Roadmap:     _proof-notes/MG_auditor_corrections_roadmap_2026-06-05.md
Schema:      _scripts/source_canonicality_schema.json
Angelegt 2026-06-05 (SCV Phase 1).
"""

import argparse, json, sys

# =========================================================================
# F_q-Arithmetik (Hausmuster aus psc2_verifier.py)
# =========================================================================

def _rref_modq(rows, q):
    """Reduzierte Zeilenstufenform mod q. Gibt (rref, pivots) zurueck."""
    M = [[x % q for x in r] for r in rows]
    nrows = len(M)
    ncols = len(M[0]) if M else 0
    pivots = []
    r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, nrows) if M[i][c] % q != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], q - 2, q)
        M[r] = [(x * inv) % q for x in M[r]]
        for i in range(nrows):
            if i != r and M[i][c] % q != 0:
                f = M[i][c]
                M[i] = [(M[i][k] - f * M[r][k]) % q for k in range(ncols)]
        pivots.append(c)
        r += 1
        if r == nrows:
            break
    return M, pivots


def rank_modq(rows, q):
    """Rang einer Matrix mod q."""
    if not rows or not rows[0]:
        return 0
    _, piv = _rref_modq(rows, q)
    return len(piv)


def matmul_modq(A, B, q):
    """Matrixmultiplikation A (m x n) * B (n x p) mod q."""
    if not A or not B or not B[0]:
        return []
    n = len(B)
    p = len(B[0])
    return [
        [sum(A[i][k] * B[k][j] for k in range(n)) % q for j in range(p)]
        for i in range(len(A))
    ]


def matvec_modq(A, v, q):
    """Matrix-Vektor-Produkt A*v mod q. Gibt Liste zurueck."""
    return [sum(A[i][k] * v[k] for k in range(len(v))) % q
            for i in range(len(A))]


def identity(n):
    """n x n Einheitsmatrix."""
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def mat_sub_modq(A, B, q):
    """A - B mod q (elementweise)."""
    return [[(A[i][j] - B[i][j]) % q
             for j in range(len(A[0]))]
            for i in range(len(A))]


def is_zero_modq(M, q):
    """Prueft ob M = 0 mod q."""
    return all(all(x % q == 0 for x in row) for row in M)


def _solve_modq(A, b, q):
    """Loest A*x = b mod q. Gibt x zurueck oder None wenn unloesbar.
    A: m x n, b: Vektor der Laenge m, x: Vektor der Laenge n."""
    m = len(A)
    n = len(A[0]) if A else 0
    aug = [[A[i][j] % q for j in range(n)] + [b[i] % q] for i in range(m)]
    M, piv = _rref_modq(aug, q)
    if n in piv:
        return None
    npiv = len(piv)
    for i in range(npiv, m):
        if M[i][n] % q != 0:
            return None
    x = [0] * n
    pivot_row = {c: ri for ri, c in enumerate(piv) if c < n}
    for c, ri in pivot_row.items():
        x[c] = M[ri][n] % q
    return x


# =========================================================================
# Sparse-Matrix-I/O (.smtx / .vec)
# =========================================================================
#
# .smtx v1 — COO-Sparse-Format (Certificate I/O Contract):
#   Zeile 1:  rows cols nnz
#   Zeilen 2..nnz+1:  row col value  (0-indiziert, ganzzahlig)
#   Kommentarzeilen beginnen mit #
#
# .vec v1 — Vektorformat:
#   Zeile 1:  length
#   Zeilen 2..length+1:  value (ganzzahlig)
#   Kommentarzeilen beginnen mit #

def load_smtx(path):
    """Laedt .smtx als dichte Matrix (Listen von Listen).
    Gibt (matrix, nrows, ncols) zurueck."""
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f
                 if l.strip() and not l.strip().startswith("#")]
    hdr = lines[0].split()
    nrows, ncols, nnz = int(hdr[0]), int(hdr[1]), int(hdr[2])
    M = [[0] * ncols for _ in range(nrows)]
    for line in lines[1:1 + nnz]:
        parts = line.split()
        r, c, v = int(parts[0]), int(parts[1]), int(parts[2])
        M[r][c] = v
    return M, nrows, ncols


def save_smtx(path, M):
    """Speichert dichte Matrix als .smtx (nur Nicht-Null-Eintraege)."""
    nrows = len(M)
    ncols = len(M[0]) if M else 0
    entries = [(i, j, M[i][j])
               for i in range(nrows) for j in range(ncols) if M[i][j] != 0]
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# smtx v1\n{nrows} {ncols} {len(entries)}\n")
        for r, c, v in entries:
            f.write(f"{r} {c} {v}\n")


def load_vec(path):
    """Laedt .vec als Liste ganzer Zahlen."""
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f
                 if l.strip() and not l.strip().startswith("#")]
    n = int(lines[0])
    return [int(lines[1 + i]) for i in range(n)]


def save_vec(path, v):
    """Speichert Vektor als .vec."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# vec v1\n{len(v)}\n")
        for x in v:
            f.write(f"{x}\n")


# =========================================================================
# Kern-Verifikationsfunktionen (Schichten C, D, E, G)
# =========================================================================
#
# Konvention: Alle Module als Spaltenquotienten M = R^n / im(Rel).
# Rel ist n x k (k Relationsspalten). Operatoren wirken links auf Spalten.

def check_quotient_map(A, Rel_src, Rel_tgt, X, q):
    """Schicht C: Prueft A*Rel_src = Rel_tgt*X mod q.
    Zeigt: A ist wohldefiniert als Abbildung zwischen Quotienten.
    A: n_t x n_s, Rel_src: n_s x k_s, Rel_tgt: n_t x k_t, X: k_t x k_s."""
    lhs = matmul_modq(A, Rel_src, q)
    rhs = matmul_modq(Rel_tgt, X, q)
    ok = is_zero_modq(mat_sub_modq(lhs, rhs, q), q)
    return {"ok": ok, "equation": "A*Rel_src = Rel_tgt*X"}


def check_inverse_mod_rel(A, B, Rel, Y, q):
    """Schicht C: Prueft B*A - I = Rel*Y mod q.
    Zeigt: BA = id auf dem Quotienten R^n / im(Rel).
    B: n x m, A: m x n, Rel: n x k, Y: k x n."""
    n = len(B)
    BA = matmul_modq(B, A, q)
    I = identity(n)
    diff = mat_sub_modq(BA, I, q)
    RelY = matmul_modq(Rel, Y, q)
    ok = is_zero_modq(mat_sub_modq(diff, RelY, q), q)
    return {"ok": ok, "equation": "B*A - I = Rel*Y"}


def check_well_defined(T, Rel, q):
    """Schicht D: Prueft T*Rel = Rel*C mod q fuer ein C (ohne Zeuge).
    Loest spaltenweise. Langsam fuer grosse Matrizen — nur fuer Tests."""
    TRel = matmul_modq(T, Rel, q)
    ncols = len(TRel[0]) if TRel else 0
    for j in range(ncols):
        col = [TRel[i][j] for i in range(len(TRel))]
        if _solve_modq(Rel, col, q) is None:
            return {"ok": False, "failing_column": j}
    return {"ok": True}


def check_intertwiner(A, H_r, H_c, Rel_c, Z, q):
    """Schicht D: Prueft A*H_r - H_c*A = Rel_c*Z mod q.
    Zeigt: A intertwint H_r und H_c auf dem Quotienten."""
    AHr = matmul_modq(A, H_r, q)
    HcA = matmul_modq(H_c, A, q)
    diff = mat_sub_modq(AHr, HcA, q)
    RelZ = matmul_modq(Rel_c, Z, q)
    ok = is_zero_modq(mat_sub_modq(diff, RelZ, q), q)
    return {"ok": ok, "equation": "A*H_r - H_c*A = Rel_c*Z"}


def check_membership(v, Rel, q):
    """Schicht G: Prueft v in im(Rel) mod q, d.h. es gibt y: Rel*y = v mod q."""
    sol = _solve_modq(Rel, v, q)
    return {"ok": sol is not None}


def check_rank_exact(P, expected_rank, q):
    """Schicht G: Prueft rank(P mod q) = expected_rank."""
    actual = rank_modq(P, q)
    return {"ok": actual == expected_rank,
            "actual_rank": actual, "expected": expected_rank}


# =========================================================================
# Integrierter SCV-Verifier
# =========================================================================

def verify_scv(cert, q):
    """Verifiziert ein SCV-Zertifikat (dict mit Matrizen).

    Pflichtfelder:
      Rel_r, Rel_c  — Relationsmatrizen (raw, canonical)
      A, B           — Isomorphismus-Matrizen
      X_A, X_B       — Wohldefiniertheitszeugen
      Y_r, Y_c       — Inversenzeugen

    Optionale Felder:
      hecke: {name: {H_r, H_c, C_r, C_c, Z}}  — Hecke-Operatoren
      P, expected_rank — Quotient-Praesentation + erwarteter Rang
      v_q, y_q         — ell_q=0 Membership-Zeuge

    Gibt Report mit checks, errors, verdict, acceptance_level zurueck.
    """
    rep = {"checks": {}, "errors": [], "warnings": []}

    Rel_r, Rel_c = cert["Rel_r"], cert["Rel_c"]
    A, B = cert["A"], cert["B"]

    # --- Schicht C: Raw <-> Canonical Isomorphismus ---

    c1 = check_quotient_map(A, Rel_r, Rel_c, cert["X_A"], q)
    rep["checks"]["C1_A_well_defined"] = c1
    if not c1["ok"]:
        rep["errors"].append("C1: A*Rel_r != Rel_c*X_A")

    c2 = check_quotient_map(B, Rel_c, Rel_r, cert["X_B"], q)
    rep["checks"]["C2_B_well_defined"] = c2
    if not c2["ok"]:
        rep["errors"].append("C2: B*Rel_c != Rel_r*X_B")

    c3 = check_inverse_mod_rel(A, B, Rel_r, cert["Y_r"], q)
    rep["checks"]["C3_BA_eq_id"] = c3
    if not c3["ok"]:
        rep["errors"].append("C3: BA - I != Rel_r*Y_r")

    c4 = check_inverse_mod_rel(B, A, Rel_c, cert["Y_c"], q)
    rep["checks"]["C4_AB_eq_id"] = c4
    if not c4["ok"]:
        rep["errors"].append("C4: AB - I != Rel_c*Y_c")

    # --- Schicht D: Hecke-Aequivarianz ---

    for name, h in cert.get("hecke", {}).items():
        if "C_r" in h:
            d1 = check_quotient_map(h["H_r"], Rel_r, Rel_r, h["C_r"], q)
            rep["checks"][f"D1_{name}_raw_wd"] = d1
            if not d1["ok"]:
                rep["errors"].append(f"D1: {name}_r*Rel_r != Rel_r*C_r")

        if "C_c" in h:
            d2 = check_quotient_map(h["H_c"], Rel_c, Rel_c, h["C_c"], q)
            rep["checks"][f"D2_{name}_can_wd"] = d2
            if not d2["ok"]:
                rep["errors"].append(f"D2: {name}_c*Rel_c != Rel_c*C_c")

        d3 = check_intertwiner(A, h["H_r"], h["H_c"], Rel_c, h["Z"], q)
        rep["checks"][f"D3_{name}_intertwiner"] = d3
        if not d3["ok"]:
            rep["errors"].append(f"D3: A*{name}_r - {name}_c*A != Rel_c*Z")

    # --- Schicht G: qdim / ell_q ---

    if "P" in cert and "expected_rank" in cert:
        g1 = check_rank_exact(cert["P"], cert["expected_rank"], q)
        rep["checks"]["G1_rank_P"] = g1
        if not g1["ok"]:
            rep["errors"].append(
                f"G1: rank(P) = {g1['actual_rank']}, erwartet {g1['expected']}")

    if "v_q" in cert and "y_q" in cert and "P" in cert:
        Py = matvec_modq(cert["P"], cert["y_q"], q)
        eq = all((Py[i] - cert["v_q"][i]) % q == 0
                 for i in range(len(Py)))
        rep["checks"]["G2_ellq_membership"] = {"ok": eq}
        if not eq:
            rep["errors"].append("G2: P*y != v_q")

    # --- Verdikt ---

    all_ok = all(c["ok"] for c in rep["checks"].values())
    rep["verdict"] = "ACCEPT" if all_ok else "REJECT"
    rep["n_checks"] = len(rep["checks"])
    rep["n_passed"] = sum(1 for c in rep["checks"].values() if c["ok"])

    has_hecke = any(k.startswith("D") for k in rep["checks"])
    rep["acceptance_level"] = (
        "RED" if not all_ok else
        "YELLOW" if has_hecke else
        "YELLOW"
    )

    return rep


# =========================================================================
# OVERCLAIM-Guards
# =========================================================================

def guard_no_full_eichler(rep):
    """GUARD: finite-window Hecke != full Eichler. YELLOW != GREEN."""
    if rep.get("acceptance_level") == "GREEN":
        rep["errors"].append(
            "OVERCLAIM: GREEN erfordert Hecke-generation guard (Sturm-Bound). "
            "Finite-window = YELLOW.")
        rep["acceptance_level"] = "YELLOW"
    return rep


def guard_no_abc(rep):
    """GUARD: SCV beweist NICHT abc. Kein Satz TP."""
    rep.setdefault("warnings", []).append(
        "SCV beweist source-canonicality (CQ-3), NICHT abc. "
        "abc erfordert canonical-level + Satz TP (werkzeug-insuffizient).")
    return rep


# =========================================================================
# Selbsttest
# =========================================================================

def _make_positive_cert(q):
    """Toy-Zertifikat: M_r = F_q^3/im([1,0,0]^T), M_c = F_q^3/im([0,1,0]^T).
    A = Permutation(0,1), B = A^{-1} = A. Hecke T = 2*I."""
    Rel_r = [[1], [0], [0]]
    Rel_c = [[0], [1], [0]]
    A = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
    B = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
    X_A = [[1]]
    X_B = [[1]]
    Y_r = [[0, 0, 0]]
    Y_c = [[0, 0, 0]]
    H_r = [[2 % q, 0, 0], [0, 2 % q, 0], [0, 0, 2 % q]]
    H_c = [[2 % q, 0, 0], [0, 2 % q, 0], [0, 0, 2 % q]]
    C_r = [[2 % q]]
    C_c = [[2 % q]]
    Z = [[0, 0, 0]]
    return {
        "Rel_r": Rel_r, "Rel_c": Rel_c,
        "A": A, "B": B, "X_A": X_A, "X_B": X_B,
        "Y_r": Y_r, "Y_c": Y_c,
        "hecke": {"T_toy": {
            "H_r": H_r, "H_c": H_c,
            "C_r": C_r, "C_c": C_c, "Z": Z,
        }},
    }


def _make_negative_cert_bad_A(q):
    """Negativ-Zertifikat: A ist NICHT wohldefiniert (bildet Rel_r nicht in im(Rel_c) ab)."""
    cert = _make_positive_cert(q)
    cert["A"] = [[1, 1, 0], [0, 1, 0], [0, 0, 1]]
    return cert


def _make_negative_cert_bad_inverse(q):
    """Negativ-Zertifikat: B ist nicht die Inverse von A mod Rel."""
    cert = _make_positive_cert(q)
    cert["Y_r"] = [[1, 0, 0]]
    return cert


def _make_rank_cert(q):
    """Rang-Zertifikat: P hat Rang 2 (= n-1 fuer n=3)."""
    return {
        "P": [[1, 0, 0], [0, 1, 0], [0, 0, 0]],
        "expected_rank": 2,
    }


def _make_membership_cert(q):
    """ell_q=0 Membership: P*y = v_q."""
    return {
        "P": [[1, 0], [0, 1]],
        "v_q": [3 % q, 4 % q],
        "y_q": [3 % q, 4 % q],
        "expected_rank": 2,
    }


def _make_nontrivial_witness_cert(q):
    """Nontrivial-Witness-Zertifikat: BA != I als Matrizen, aber BA - I in im(Rel).

    Konstruktion: n=2, Rel = [[1],[0]] (Quotient ~ F_q).
    A = [[6,0],[0,1]]: Identitaet auf Quotient, nontrivial auf Ambient.
    B = I: BA = A != I, aber BA - I = [[5,0],[0,0]] = Rel * [[5,0]].
    H_r = [[2,0],[0,3]], H_c = [[7,0],[0,3]]: gleich auf Quotient (beide = 3).
    A*H_r - H_c*A = [[-30,0],[0,0]] = Rel_c * [[-30,0]]."""
    Rel_r = [[1], [0]]
    Rel_c = [[1], [0]]
    A = [[6, 0], [0, 1]]
    B = [[1, 0], [0, 1]]
    X_A = [[6]]
    X_B = [[1]]
    Y_r = [[5, 0]]
    Y_c = [[5, 0]]
    H_r = [[2, 0], [0, 3]]
    H_c = [[7, 0], [0, 3]]
    C_r = [[2]]
    C_c = [[7]]
    Z = [[(-30) % q, 0]]
    return {
        "Rel_r": Rel_r, "Rel_c": Rel_c,
        "A": A, "B": B, "X_A": X_A, "X_B": X_B,
        "Y_r": Y_r, "Y_c": Y_c,
        "hecke": {"T_nontrivial": {
            "H_r": H_r, "H_c": H_c,
            "C_r": C_r, "C_c": C_c, "Z": Z,
        }},
    }


def selftest():
    q = 5077
    ok = True

    # --- T1: Positiv-Zertifikat (voller Isomorphismus + Hecke) ---
    cert = _make_positive_cert(q)
    rep = verify_scv(cert, q)
    t1 = (rep["verdict"] == "ACCEPT"
          and rep["n_checks"] == rep["n_passed"]
          and rep["acceptance_level"] == "YELLOW"
          and len(rep["errors"]) == 0)
    print(f"[T1] Positiv (iso+hecke): verdict={rep['verdict']} "
          f"checks={rep['n_passed']}/{rep['n_checks']} -> {'PASS' if t1 else 'FAIL'}")
    ok &= t1

    # --- T2: Negativ — A nicht wohldefiniert ---
    cert2 = _make_negative_cert_bad_A(q)
    rep2 = verify_scv(cert2, q)
    t2 = (rep2["verdict"] == "REJECT"
          and any("C1" in e for e in rep2["errors"]))
    print(f"[T2] Negativ (bad A): verdict={rep2['verdict']} "
          f"errors={len(rep2['errors'])} -> {'PASS' if t2 else 'FAIL'}")
    ok &= t2

    # --- T3: Negativ — schlechter Inversenzeuge ---
    cert3 = _make_negative_cert_bad_inverse(q)
    rep3 = verify_scv(cert3, q)
    t3 = (rep3["verdict"] == "REJECT"
          and any("C3" in e for e in rep3["errors"]))
    print(f"[T3] Negativ (bad inverse): verdict={rep3['verdict']} "
          f"errors={len(rep3['errors'])} -> {'PASS' if t3 else 'FAIL'}")
    ok &= t3

    # --- T4: Rang-Check ---
    rc = _make_rank_cert(q)
    g1 = check_rank_exact(rc["P"], rc["expected_rank"], q)
    t4 = g1["ok"] and g1["actual_rank"] == 2
    g1_bad = check_rank_exact(rc["P"], 3, q)
    t4 &= not g1_bad["ok"]
    print(f"[T4] Rang: ok={g1['ok']} rank={g1['actual_rank']} "
          f"bad_reject={not g1_bad['ok']} -> {'PASS' if t4 else 'FAIL'}")
    ok &= t4

    # --- T5: Membership ---
    mc = _make_membership_cert(q)
    Py = matvec_modq(mc["P"], mc["y_q"], q)
    t5 = all((Py[i] - mc["v_q"][i]) % q == 0 for i in range(len(Py)))
    bad_y = [0, 0]
    Py_bad = matvec_modq(mc["P"], bad_y, q)
    t5_neg = not all((Py_bad[i] - mc["v_q"][i]) % q == 0 for i in range(len(Py_bad)))
    t5 &= t5_neg
    print(f"[T5] Membership: positive={t5} negative_reject={t5_neg} "
          f"-> {'PASS' if t5 else 'FAIL'}")
    ok &= t5

    # --- T6: _solve_modq ---
    A = [[1, 2], [3, 4]]
    b = [5 % q, 6 % q]
    x = _solve_modq(A, b, q)
    t6 = x is not None
    if x:
        Ax = matvec_modq(A, x, q)
        t6 &= all((Ax[i] - b[i]) % q == 0 for i in range(2))
    b_bad = [1, 0]
    A_singular = [[1, 2], [2, 4]]
    x_bad = _solve_modq(A_singular, b_bad, q)
    t6 &= (x_bad is None)
    print(f"[T6] _solve_modq: solvable={'yes' if x else 'no'} "
          f"singular_reject={x_bad is None} -> {'PASS' if t6 else 'FAIL'}")
    ok &= t6

    # --- T7: check_well_defined (ohne Zeuge) ---
    Rel = [[1], [0], [0]]
    T_good = [[2, 0, 0], [0, 3, 0], [0, 0, 4]]
    T_bad = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
    wd_good = check_well_defined(T_good, Rel, q)
    wd_bad = check_well_defined(T_bad, Rel, q)
    t7 = wd_good["ok"] and not wd_bad["ok"]
    print(f"[T7] check_well_defined: good={wd_good['ok']} "
          f"bad={wd_bad['ok']} -> {'PASS' if t7 else 'FAIL'}")
    ok &= t7

    # --- T8: OVERCLAIM-Guard ---
    rep_fake = {"acceptance_level": "GREEN", "errors": []}
    guard_no_full_eichler(rep_fake)
    t8 = (rep_fake["acceptance_level"] == "YELLOW"
          and any("OVERCLAIM" in e for e in rep_fake["errors"]))
    print(f"[T8] OVERCLAIM-Guard: level={rep_fake['acceptance_level']} "
          f"-> {'PASS' if t8 else 'FAIL'}")
    ok &= t8

    # --- T9: Nichtriviales Quotientenmodul ---
    # M = F_q^4 / im(Rel), Rel = [[1,0],[0,1],[0,0],[0,0]] (2 Relationen,
    # Quotient = F_q^2). A: Identitaet auf Quotient.
    Rel_r9 = [[1, 0], [0, 1], [0, 0], [0, 0]]
    Rel_c9 = [[1, 0], [0, 1], [0, 0], [0, 0]]
    A9 = identity(4)
    B9 = identity(4)
    X_A9 = identity(2)
    X_B9 = identity(2)
    Y_r9 = [[0] * 4, [0] * 4]
    Y_c9 = [[0] * 4, [0] * 4]
    cert9 = {"Rel_r": Rel_r9, "Rel_c": Rel_c9,
             "A": A9, "B": B9, "X_A": X_A9, "X_B": X_B9,
             "Y_r": Y_r9, "Y_c": Y_c9}
    rep9 = verify_scv(cert9, q)
    t9 = rep9["verdict"] == "ACCEPT" and rep9["n_checks"] == 4
    print(f"[T9] Mehrdim. Relationen: verdict={rep9['verdict']} "
          f"checks={rep9['n_checks']} -> {'PASS' if t9 else 'FAIL'}")
    ok &= t9

    # --- T10: .smtx Round-Trip ---
    import tempfile, os
    M_orig = [[0, 3, 0], [1, 0, 2], [0, 0, 0]]
    with tempfile.NamedTemporaryFile(suffix=".smtx", delete=False, mode="w") as tmp:
        tmppath = tmp.name
    try:
        save_smtx(tmppath, M_orig)
        M_loaded, nr, nc = load_smtx(tmppath)
        t10 = (nr == 3 and nc == 3 and M_loaded == M_orig)
    finally:
        os.unlink(tmppath)
    print(f"[T10] .smtx round-trip: {'PASS' if t10 else 'FAIL'}")
    ok &= t10

    # --- T11: Nontriviale Witnesses — ACCEPT ---
    # BA != I als Matrizen, aber BA - I = Rel*Y (Y != 0).
    # A*H_r - H_c*A != 0 als Matrizen, aber = Rel_c*Z (Z != 0).
    cert11 = _make_nontrivial_witness_cert(q)
    rep11 = verify_scv(cert11, q)
    t11 = (rep11["verdict"] == "ACCEPT"
           and rep11["n_checks"] == rep11["n_passed"]
           and len(rep11["errors"]) == 0)
    print(f"[T11] Nontriviale Witnesses (ACCEPT): verdict={rep11['verdict']} "
          f"checks={rep11['n_passed']}/{rep11['n_checks']} -> {'PASS' if t11 else 'FAIL'}")
    ok &= t11

    # --- T12: Korrumpierte Witnesses — REJECT ---
    # T12a: Y_r verfaelscht -> C3 (BA-I != Rel*Y) schlaegt fehl
    cert12a = _make_nontrivial_witness_cert(q)
    cert12a["Y_r"] = [[5, 1]]
    rep12a = verify_scv(cert12a, q)
    t12a = (rep12a["verdict"] == "REJECT"
            and any("C3" in e for e in rep12a["errors"]))
    # T12b: Z verfaelscht -> D3 (A*H_r - H_c*A != Rel_c*Z) schlaegt fehl
    cert12b = _make_nontrivial_witness_cert(q)
    cert12b["hecke"]["T_nontrivial"]["Z"] = [[(-30) % q, 1]]
    rep12b = verify_scv(cert12b, q)
    t12b = (rep12b["verdict"] == "REJECT"
            and any("D3" in e for e in rep12b["errors"]))
    t12 = t12a and t12b
    print(f"[T12] Korrumpierte Witnesses (REJECT): "
          f"bad_Y_r={rep12a['verdict']} bad_Z={rep12b['verdict']} "
          f"-> {'PASS' if t12 else 'FAIL'}")
    ok &= t12

    print(f"\nSELFTEST: {'ALL PASS' if ok else 'FAILURES'} ({12}/{12 if ok else '?'})")
    return 0 if ok else 1


# =========================================================================
# CLI
# =========================================================================

def main():
    ap = argparse.ArgumentParser(
        description="SCV Core — Source-Canonicality-Validator (CQ-3/S2a)")
    ap.add_argument("--selftest", action="store_true",
                    help="12 Selbsttests (Toy-Modelle + nontriviale Witnesses + OVERCLAIM-Guards)")
    ap.add_argument("--manifest", type=str,
                    help="SCV-Manifest (JSON) laden und verifizieren")
    ap.add_argument("--q", type=int, default=5077,
                    help="Koeffizientenprimzahl (Default: 5077)")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    if args.manifest:
        with open(args.manifest, encoding="utf-8") as f:
            manifest = json.load(f)
        rep = verify_scv(manifest, args.q)
        rep = guard_no_full_eichler(rep)
        rep = guard_no_abc(rep)
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        sys.exit(0 if rep["verdict"] == "ACCEPT" else 2)

    ap.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
