#!/usr/bin/env python3
"""
M-DET Stufe 1b: Elementarteiler-Exponenten des 60168-Witness-Systems (Sage, Mac).

M-DET 1a ergab: rank_Q = 31680 (Vollrang), Drop-Primes {2: Defekt 2,
3: 1, 5: 1, 31: 1}. Dieses Script bestimmt v_p(det) EXAKT ueber die
KERN-FILTRATION (nicht ueber naive Leitern pro Basisvektor!):

  L_k := { x in ker(M mod p) : es existiert Z-Lift x^ mit M x^ == 0 mod p^k }.
  Standard-Fakt (Smith-Normalform ueber Z_p):
    dim_Fp L_k = #( Elementarteiler e_i mit p^k | e_i )
    =>  v_p(det) = Summe_{k>=1} dim L_k.

  Lift-Test Stufe k -> k+1 fuer Klasse x mit Stufe-k-Lift x_k:
    x liftet  <=>  (M x_k)/p^k mod p  in  Bild(M mod p) + span(Korrekturen),
    Korrekturen = Obstruktionsvektoren o_j = (M u_j)/p^j mod p aller
    frueheren Stufen j < k (u_j = Stufe-j-Lifts der L_j-Basen).
    Begruendung: zwei Stufe-k-Lifts von x differieren um p*u mit
    u in V_{k-1} = ker(M mod p^{k-1}); V_{k-1} wird erzeugt von den
    Stufe-(k-1)-Lifts der L_{k-1}-Basis, 2*V_{k-2}, ..., p^{k-1}*Z^n.
    Ohne Korrekturspalten haengt der Test vom Lift-Pfad ab und
    UNTERZAEHLT (Gegenbeispiel: M = diag(2,4), Basis {e1, e1+e2}:
    naiv 1+1 = 2, wahr v_2(8) = 3).
  Konstruktion des neuen Lifts aus Loesung (z; gamma) von
    [M | corr] * (z; gamma) == -o(x_k) mod p:
    x_{k+1} = x_k + p^k * z + Summe_j gamma_j * p^(k - j) * u_j.
  Jede Stufe wird HART verifiziert: M x_{k+1} == 0 mod p^{k+1} (exakt in Z).

  Fuer Defekt-1-Primes (3, 5, 31) ist die Korrektur-Logik aequivalent zur
  naiven Leiter (Korrekturspalten dort nachweislich redundant); fuer p = 2
  (Defekt 2) werden alle 3 nichttrivialen Kernklassen getrennt verfolgt.

  Elementarteiler-Exponenten = konjugierte Partition der dim-Folge
  (d_1, d_2, ...): exps = [ #(k : d_k >= j) fuer j = 1..d_1 ].

Output: _results/mdet_1b_snf_exponents_60168_<date>.{json,md}
"""
import json, sys, time
from datetime import date
from pathlib import Path

WITNESS = Path("_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl")
WQ = 3863
N = 31680
KMAX = 10  # Sicherheits-Obergrenze der Filtrations-Leiter
OUT_JSON = "_results/mdet_1b_snf_exponents_60168_{}.json".format(date.today())
OUT_MD = "_results/mdet_1b_snf_exponents_60168_{}.md".format(date.today())


def main():
    t0 = time.time()
    ts = lambda: time.strftime("%H:%M:%S")
    print("=== M-DET 1b: SNF exponents via kernel filtration ===")
    from sage.all import GF, ZZ, matrix, vector

    half = WQ // 2
    entries = {}
    nrows = 0
    with open(WITNESS) as f:
        for line in f:
            rec = json.loads(line)
            for c, v in rec["row"]:
                v = int(v)
                if v > half:
                    v -= WQ
                if v:
                    entries[(nrows, int(c))] = v
            nrows += 1
    if nrows != 31680:
        print(f"FATAL: {nrows} Zeilen != 31680. ABBRUCH.")
        return 3
    MZ = matrix(ZZ, nrows, N, entries, sparse=True)
    print(f"[{ts()}] Witness geladen: nnz={len(entries)} ({time.time()-t0:.0f}s)")
    sys.stdout.flush()

    results = {}
    fatal = False
    for p, expected_defect in ((3, 1), (5, 1), (31, 1), (2, 2)):
        t1 = time.time()
        Fp = GF(p)
        Mp = MZ.change_ring(Fp)
        K = Mp.right_kernel().basis()
        d1 = len(K)
        print(f"[{ts()}] p={p}: kernel dim={d1} (erwartet {expected_defect}) ({time.time()-t1:.0f}s)")
        sys.stdout.flush()
        if d1 != expected_defect:
            print(f"  WARNUNG: Defekt weicht von 1a-Soll ab -- messe was ist.")

        # Zu verfolgende Kernklassen: bei dim 1 die eine Basis-Klasse;
        # bei dim 2 (p=2) alle 3 nichttrivialen Klassen b0, b1, b0+b1.
        basis_Z = [vector(ZZ, [int(t) for t in kb]) for kb in K]
        if d1 == 1:
            classes = [("b0", basis_Z[0])]
        elif d1 == 2:
            classes = [("b0", basis_Z[0]), ("b1", basis_Z[1]),
                       ("b0+b1", basis_Z[0] + basis_Z[1])]
        else:
            # generisch: nur Basisklassen einzeln + paarweise Summen waeren
            # noetig; bei d1 > 2 abbrechen statt falsch zu rechnen.
            print(f"  FATAL: kernel dim {d1} > 2 nicht implementiert.")
            fatal = True
            break

        corr = []   # Liste (stufe_j, u_j (Z-Vektor), o_j (Z-Vektor, = M u_j / p^j))
        dims = []   # d_k-Folge
        kmax_hit = False
        k = 1
        while classes and k <= KMAX:
            n_cls = len(classes)
            d_k = 1 if n_cls == 1 else 2  # n_cls in {1, 3}
            dims.append(d_k)
            # Augmentierte Matrix [Mp | corr-Spalten]
            if corr:
                cent = {}
                for j, (_, _, oZ) in enumerate(corr):
                    for i, t in enumerate(oZ):
                        tv = int(t) % p
                        if tv:
                            cent[(i, j)] = tv
                Cm = matrix(Fp, nrows, len(corr), cent, sparse=True)
                A = Mp.augment(Cm)
            else:
                A = Mp
            survivors = []
            new_corr = []
            for label, x in classes:
                w = MZ * x
                assert all(int(t) % p**k == 0 for t in w), f"Leiter inkonsistent p={p} k={k} {label}"
                oZ = vector(ZZ, [int(t) // p**k for t in w])
                new_corr.append((k, x, oZ))
                rhs = vector(Fp, [(-int(t)) % p for t in oZ])
                try:
                    sol = A.solve_right(rhs)
                except ValueError:
                    print(f"[{ts()}]   p={p} k={k} {label}: KEIN Lift mod p^{k+1} ({time.time()-t1:.0f}s)")
                    sys.stdout.flush()
                    continue
                z = vector(ZZ, [int(sol[i]) for i in range(N)])
                x_new = x + p**k * z
                for j, gi in enumerate(range(N, N + len(corr))):
                    g = int(sol[gi])
                    if g:
                        sj, uj, _ = corr[j]
                        x_new = x_new + g * p**(k - sj) * uj
                # Harte Verifikation der neuen Stufe (exakt in Z)
                w2 = MZ * x_new
                assert all(int(t) % p**(k + 1) == 0 for t in w2), \
                    f"Lift-Verifikation FEHLGESCHLAGEN p={p} k={k+1} {label}"
                survivors.append((label, x_new))
                print(f"[{ts()}]   p={p} k={k} {label}: liftet mod p^{k+1} (verifiziert) ({time.time()-t1:.0f}s)")
                sys.stdout.flush()
            # Unterraum-Konsistenz: bei 3 Klassen sind 0, 1 oder 3 Lifts moeglich
            if n_cls == 3 and len(survivors) == 2:
                print(f"  FATAL: 2 von 3 Klassen liften (kein Unterraum) -- Logikfehler.")
                fatal = True
                break
            corr.extend(new_corr)
            classes = survivors
            k += 1
        if fatal:
            break
        if classes and k > KMAX:
            kmax_hit = True
            print(f"  WARNUNG: KMAX={KMAX} erreicht, v_p(det) ist nur UNTERE Schranke.")
        v_p_det = sum(dims)
        exps = [sum(1 for d in dims if d >= j) for j in range(1, (dims[0] if dims else 0) + 1)]
        results[p] = {"kernel_dim": d1, "dims_filtration": dims,
                      "elementary_divisor_exponents": exps,
                      "v_p_det": v_p_det, "kmax_hit": kmax_hit}
        print(f"[{ts()}] p={p}: dims={dims} -> ET-Exponenten {exps}, v_p(det)={v_p_det} ({time.time()-t1:.0f}s)")
        sys.stdout.flush()

    if fatal:
        return 4

    D = 1
    for p, d in results.items():
        D *= p ** d["v_p_det"]
    any_kmax = any(d["kmax_hit"] for d in results.values())
    report = {"date": str(date.today()), "level": 60168,
              "per_prime": {str(p): d for p, d in results.items()},
              "D_W_abs": int(D),
              "D_W_factored": " * ".join(f"{p}^{d['v_p_det']}" for p, d in sorted(results.items())),
              "exact": not any_kmax,
              "note": ("D(W) = |det| des vollrangigen Witness-Systems; Exponenten via "
                       "Kern-Filtration mit Korrekturspalten (jede Stufe Z-exakt verifiziert; KMAX={})."
                       .format(KMAX))}
    with open(OUT_JSON, "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# M-DET 1b: Elementarteiler-Exponenten, 60168 ({})".format(date.today()), ""]
    lines.append("| p | Kern-Dim | Filtration d_k | ET-Exponenten | v_p(det) |")
    lines.append("|---|---|---|---|---|")
    for p, d in sorted(results.items()):
        lines.append("| {} | {} | {} | {} | {} |".format(
            p, d["kernel_dim"], d["dims_filtration"],
            d["elementary_divisor_exponents"], d["v_p_det"]))
    lines.append("")
    lines.append("**|D(W)| = {} = {}**{}".format(
        report["D_W_factored"], D, "" if report["exact"] else " (UNTERE SCHRANKE, KMAX erreicht)"))
    lines.append("")
    lines.append("Methode: Kern-Filtration L_k mit Korrekturspalten frueherer Obstruktionen;")
    lines.append("jeder Lift exakt in Z verifiziert (M x == 0 mod p^k). Naive Leitern pro")
    lines.append("Basisvektor waeren bei p=2 (Defekt 2) nicht korrekt.")
    lines.append("")
    lines.append("Total: {:.0f}s".format(time.time() - t0))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " MD:", OUT_MD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
