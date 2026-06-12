#!/usr/bin/env python3
"""
psc2_verifier.py — PSC (Plücker-Sink Certificate) Verifier-Skeleton.
Deckt PSC-2 (zweidimensionaler Defekt d_q=2, q=2: Pairing [[1,1],[1,0]]) UND
PSC-1 (eindimensionaler Defekt d_q=1, q=3,5,31: One-Row Schubert Gate AP-6) ab —
verify_psc2() ist in d_q allgemein. Schema PSC-2: _scripts/psc2_certificate_schema.json;
Schema PSC-1: _scripts/psc1_certificate_schema.json.

Teil der Trace-Plücker-Content-No-Escape-Kampagne (HCT/abc), s.
_proof-notes/trace_pluecker_content_noescape_2026-05-31.md  (AP-3/AP-4/AP-5, Satz PCAT).
Angelegt 2026-06-01 (Kampagne 2026-05-31).

ZWECK (bewiesener mathematischer Kern, NICHT abc):
  Gegeben ganzzahlige Source-Relationen A (n x n, det != 0 ueber Q), Repair-/Trace-Zeilen
  R (s x n), und eine Primzahl q. Sei d = n - rank(A mod q) und K eine rechte Kernelbasis
  von A mod q (n x d). Dann gilt:

      A K = 0 (mod q),  rank(A mod q) = n-d,  rank(K mod q) = d,
      und EIN d x d Minor von (R K) ist Einheit mod q
          ==>  rank([A;R] mod q) = n  ==>  ell_q(coker[A;R]) = 0.

  D.h. q ist VOLL drainiert (nicht nur erste Schicht): kein tieferer q^r-Sedimentdrache.
  (Korrektur 2026-05-31: voll reparierter mod-q-Rang => ell_q=0; keine q^2/q^3-Tiefe noetig.)

  Dies ist die AP-5-Schubert-Gate-Form von delta([A;R]) = gcd(det(A)*Plücker(R A^{-1}))
  (Lemma AP, verifiziert). Das Zertifikat ist klein, portabel und ohne grosse SNF pruefbar.

ABGRENZUNG (Faktentreue):
  - certificate-level: beweist q∤δ([A;R]) fuer DIESEN konkreten Block (A,R).
  - canonical-level:  beweist NICHT, dass (A,R) der kanonische HCT-Trace-Quotient ist
                      (Drache D1 / S2a-S2b offen). Das Zertifikat traegt beide Labels.
  - Globaler Content-No-Escape (Satz PCAT, alle q uniform) bleibt OFFEN.
"""

import argparse, json, sys

# --------------------------------------------------------------------------
# Lineare Algebra ueber F_q (q prim)
# --------------------------------------------------------------------------

def _rref_modq(rows, q):
    """Reduzierte Zeilenstufenform mod q. rows: Liste von Listen ganzer Zahlen.
    Gibt (rref, pivots) zurueck."""
    M = [[x % q for x in r] for r in rows]
    nrows = len(M); ncols = len(M[0]) if M else 0
    pivots = []
    r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, nrows) if M[i][c] % q != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], q - 2, q)            # Fermat-Inverse (q prim)
        M[r] = [(x * inv) % q for x in M[r]]
        for i in range(nrows):
            if i != r and M[i][c] % q != 0:
                f = M[i][c]
                M[i] = [(M[i][k] - f * M[r][k]) % q for k in range(ncols)]
        pivots.append(c); r += 1
        if r == nrows:
            break
    return M, pivots

def rank_modq(rows, q):
    if not rows:
        return 0
    _, piv = _rref_modq(rows, q)
    return len(piv)

def right_kernel_modq(A, q):
    """Basis des rechten Kerns {x : A x = 0 mod q} als Liste von Spaltenvektoren (Listen)."""
    M, piv = _rref_modq(A, q)
    ncols = len(A[0])
    pivset = set(piv)
    free = [c for c in range(ncols) if c not in pivset]
    basis = []
    for f in free:
        vec = [0] * ncols
        vec[f] = 1
        for ri, c in enumerate(piv):
            vec[c] = (-M[ri][f]) % q
        basis.append(vec)
    return basis   # len = d = ncols - rank

def matmul_modq(A, B, q):
    """A (m x n) * B (n x p) mod q."""
    n = len(B); p = len(B[0]) if B else 0
    return [[sum(A[i][k] * B[k][j] for k in range(n)) % q for j in range(p)] for i in range(len(A))]

def det_modq(M, q):
    """det einer quadratischen Matrix mod q via Gauss."""
    M = [[x % q for x in r] for r in M]; n = len(M); det = 1
    for c in range(n):
        piv = next((i for i in range(c, n) if M[i][c] % q != 0), None)
        if piv is None:
            return 0
        if piv != c:
            M[c], M[piv] = M[piv], M[c]; det = (-det) % q
        det = (det * M[c][c]) % q
        inv = pow(M[c][c], q - 2, q)
        for i in range(c + 1, n):
            f = (M[i][c] * inv) % q
            if f:
                M[i] = [(M[i][k] - f * M[c][k]) % q for k in range(n)]
    return det % q

# --------------------------------------------------------------------------
# PSC-2 Kern-Verifikation
# --------------------------------------------------------------------------

def verify_psc2(A, R, q, K=None):
    """Prueft den PSC-2-Kern. A: n x n, R: s x n, q prim. K optional (n x d) als
    Liste von Spaltenvektoren; sonst aus A mod q berechnet.
    Rueckgabe: dict mit checks + Verdikt ell_q == 0."""
    n = len(A); assert all(len(r) == n for r in A), "A nicht n x n"
    s = len(R)
    rkA = rank_modq(A, q)
    d = n - rkA
    if K is None:
        K = right_kernel_modq(A, q)
    # K als n x d Matrix (Spalten = Kernelvektoren)
    Kmat = [[K[j][i] for j in range(len(K))] for i in range(n)]   # n x d
    # Checks
    AK = matmul_modq(A, Kmat, q) if d > 0 else [[0]]
    AK_zero = all(all(x % q == 0 for x in row) for row in AK)
    rankK = rank_modq([[Kmat[i][j] for j in range(d)] for i in range(n)], q) if d > 0 else 0
    # Pairing R*K  (s x d)
    RK = matmul_modq(R, Kmat, q) if d > 0 else [[0] * 0 for _ in range(s)]
    # Suche d x d Minor von RK, der Einheit mod q ist
    from itertools import combinations
    unit_minor = None
    if d > 0 and s >= d:
        for rowsel in combinations(range(s), d):
            sub = [[RK[i][j] for j in range(d)] for i in rowsel]
            if det_modq(sub, q) % q != 0:
                unit_minor = {"repair_rows": list(rowsel), "det_mod_q": det_modq(sub, q)}
                break
    rankBR = rank_modq(A + R, q)
    ell_q_zero = (rankBR == n)
    return {
        "q": q, "n": n, "rank_A_mod_q": rkA, "d_q": d, "s_repair_rows": s,
        "check_AK_eq_0_mod_q": AK_zero,
        "check_rank_K_eq_d": (rankK == d),
        "pairing_RK_mod_q": RK,
        "unit_dxd_minor": unit_minor,
        "rank_[A;R]_mod_q": rankBR,
        "VERDICT_ell_q_eq_0": ell_q_zero,
        "consistent": (ell_q_zero == (unit_minor is not None) == (rankBR == n)),
    }

# --------------------------------------------------------------------------
# Selbsttest: 60168/raw, q=2 Toy-Modell (Defekt d_2 = 2, Pairing [[1,1],[1,0]])
# --------------------------------------------------------------------------

def selftest():
    # A mod 2 hat Rang 2 (Zeilen 3,4 == Zeilen 1,2 mod 2), det(A) != 0 ueber Q:
    A = [[1, 0, 2, 0],
         [0, 1, 0, 2],
         [1, 0, 4, 0],
         [0, 1, 0, 4]]
    R = [[1, 1, 1, 1],    # t5-Surrogat
         [1, 0, 1, 0]]    # t7-Surrogat
    res = verify_psc2(A, R, q=2)
    print("== PSC-2 Selbsttest (60168/raw q=2 Toy-Modell) ==")
    print(json.dumps(res, indent=2))
    ok = (res["VERDICT_ell_q_eq_0"] and res["check_AK_eq_0_mod_q"]
          and res["check_rank_K_eq_d"] and res["unit_dxd_minor"] is not None
          and res["consistent"] and res["d_q"] == 2)
    print("SELBSTTEST:", "PASS" if ok else "FAIL")
    return ok

def selftest_psc1():
    # PSC-1 / AP-6: One-Row Schubert Gate. A mod 3 Rang n-1 (d=1), eine Repair-Zeile r
    # mit r·k != 0 mod 3 ==> ell_3 = 0. Plus Negativtest (r·k = 0 ==> ell_3 > 0).
    A = [[1, 0, 0, 3], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 3]]   # mod 3: Rang 3, d=1
    r_good = [[1, 1, 1, 1]]
    r_bad  = [[0, 1, 1, 0]]
    g = verify_psc2(A, r_good, q=3)
    b = verify_psc2(A, r_bad,  q=3)
    print("== PSC-1 Selbsttest (One-Row Schubert Gate, q=3, d=1) ==")
    print("  positiv:", json.dumps({k: g[k] for k in ("d_q", "pairing_RK_mod_q", "unit_dxd_minor", "VERDICT_ell_q_eq_0")}))
    print("  negativ:", json.dumps({k: b[k] for k in ("pairing_RK_mod_q", "VERDICT_ell_q_eq_0")}))
    ok = (g["d_q"] == 1 and g["VERDICT_ell_q_eq_0"] and g["consistent"]
          and (b["VERDICT_ell_q_eq_0"] is False))
    print("SELBSTTEST PSC-1:", "PASS" if ok else "FAIL")
    return ok

# --------------------------------------------------------------------------
# Stub: echte 60168/raw-Artefakte laden (sobald _results-Matrizen vorliegen)
# --------------------------------------------------------------------------

def load_real_and_verify(path_A, path_R, q, path_K=None):
    """ERWARTET echte Projektartefakte (Source-Block A, Repair-Zeilen t5,t7,
    optional rechte Kernelbasis K) als JSON-Listen oder .npz. Bindet im echten
    Lauf an Rowhash-Transcripts (s. PSC-2-Schema). Noch NICHT implementiert,
    weil die _results-Matrizen (31680 x 31680) hier nicht vorliegen."""
    raise NotImplementedError(
        "Echte Artefakte fehlen: Source-Block A, t5/t7, Kernelbasis K, Rowhash-Transcripts. "
        "Format/Bindung s. _scripts/psc2_certificate_schema.json + "
        "_results/psc2_60168_raw_q2_template.json")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="PSC-2 Verifier (HCT/abc Trace-Plücker)")
    ap.add_argument("--selftest", action="store_true", help="PSC-2: 60168/raw q=2 Toy-Modell (d=2)")
    ap.add_argument("--selftest-psc1", action="store_true", help="PSC-1: One-Row Schubert Gate q=3 (d=1)")
    args = ap.parse_args()
    if args.selftest_psc1:
        sys.exit(0 if selftest_psc1() else 1)
    if args.selftest or len(sys.argv) == 1:
        ok2 = selftest(); ok1 = selftest_psc1()
        sys.exit(0 if (ok1 and ok2) else 1)
