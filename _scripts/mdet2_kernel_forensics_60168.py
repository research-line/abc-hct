#!/usr/bin/env python3
"""
M-DET 2: Kernvektor-Forensik am 60168-Witness-System (Sage, Mac).

ZIEL (Satz-B-Mechanismus): Nicht nur MESSEN, dass die Drop-Primes
{2, 3, 5, 31} sind (1a) und welche Exponenten sie tragen (1b), sondern
WARUM — aus der Struktur der Kernvektoren den Erklaerungs-Mechanismus
ableiten. Vorergebnisse: Eisenstein-Kongruenz-Primes der drei
60168-Klassen sind LEER (mdet2_eisenstein_prime_test: alle Torsion 1,
kein q besteht) => arithmetische Erklaerung via Eisenstein faellt aus;
konstruktive Erklaerung (Relationen-Kombinatorik) fuehrend. Speziell
p=3: Dreiecks-Relation 1 + T + T^2 == (1 - T)^2 mod 3 (T^3 = 1) —
nilpotentes QUADRAT, konsistent mit v_3(D(W)) = 2 (1b, log-belegt).

WAS DAS SCRIPT TUT (pro p in {3, 5, 31, 2}):
  1. GF(p)-Kernvektor(en) des 31680^2-Witness-Systems berechnen
     (right_kernel; ~85 min/Prime nach 1b-Erfahrung) und PERSISTIEREN
     (npz, symmetrischer Lift) — die 1b-Laeufe speicherten sie nicht.
  2. Struktur-Statistik:
     a) Traegergroesse + Wertehistogramm (symmetrischer Lift).
     b) DREIECKS-MUSTER: manin-Stage-Zeilen mit genau 3 nnz =
        Manin-Dreiecke. Pro Dreieck (c1,c2,c3) das Wertemuster des
        Kernvektors klassifizieren: m = #Traeger-Ecken (0..3) und bei
        m = 3 Muster konstant (a,a,a) / zweigleich (a,a,b) / verschieden
        (a,b,c) BIS AUF SKALAR. p=3-Hypothese ((1-T)^2): signifikanter
        Ueberschuss konstanter Dreiecke.
     c) LOKALISIERUNG: Traegerdichte ueber 64 Spaltenfenster
        (Mikro-Cluster-These: Traeger konzentriert statt uniform).
     d) UEBERLAPP zwischen den p-Traegern (Jaccard) — sitzen 3/5/31
        am selben Ort (S5-Zertifikats-Orte!) oder disjunkt?
  3. Zeilen-Profil: welche STAGES (manin/hecke/...) sind auf dem
     Traeger inzident (Histogramm) — verortet den Mechanismus in der
     Konstruktionsschicht.

Output: _results/mdet2_kernel_forensics_60168_<date>.{json,md}
        _results/mdet2_kernel_vectors_60168_<date>.npz
"""
import json, sys, time
from collections import Counter
from datetime import date
from pathlib import Path

WITNESS = Path("_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl")
WQ = 3863
N = 31680
PRIMES = [3, 5, 31, 2]
NWIN = 64
OUT_JSON = "_results/mdet2_kernel_forensics_60168_{}.json".format(date.today())
OUT_MD = "_results/mdet2_kernel_forensics_60168_{}.md".format(date.today())
OUT_NPZ = "_results/mdet2_kernel_vectors_60168_{}.npz".format(date.today())


def main():
    t0 = time.time()
    ts = lambda: time.strftime("%H:%M:%S")
    half = WQ // 2
    print("=== M-DET 2: kernel forensics 60168 ===")
    from sage.all import GF, ZZ, matrix, vector
    import numpy as np

    entries = {}
    triangles = []          # (c1, c2, c3) der manin-3nnz-Zeilen
    row_stage = []          # Stage-Label pro Zeile
    rows_by_col = {}        # col -> Zeilenindizes (fuer Stage-Profil)
    stage_hist = Counter()
    nrows = 0
    with open(WITNESS) as f:
        for line in f:
            rec = json.loads(line)
            stage = str(rec.get("stage", "?"))
            stage_hist[stage] += 1
            cols_here = []
            for c, v in rec["row"]:
                v = int(v)
                if v > half:
                    v -= WQ
                if v:
                    c = int(c)
                    entries[(nrows, c)] = v
                    cols_here.append(c)
                    rows_by_col.setdefault(c, []).append(nrows)
            if "manin" in stage and len(cols_here) == 3:
                triangles.append(tuple(cols_here))
            row_stage.append(stage)
            nrows += 1
    if nrows != 31680:
        print(f"FATAL: {nrows} Zeilen != 31680. ABBRUCH.")
        return 3
    print(f"[{ts()}] Witness: nnz={len(entries)}, Dreiecke={len(triangles)}, "
          f"Stages={dict(stage_hist)} ({time.time()-t0:.0f}s)")
    sys.stdout.flush()
    MZ = matrix(ZZ, nrows, N, entries, sparse=True)

    report = {"date": str(date.today()), "level": 60168, "n_triangles": len(triangles),
              "stage_histogram": dict(stage_hist), "per_prime": {}, "status": "running"}
    vecs_np = {}
    supports = {}

    for p in PRIMES:
        t1 = time.time()
        Fp = GF(p)
        Mp = MZ.change_ring(Fp)
        K = Mp.right_kernel().basis()
        print(f"[{ts()}] p={p}: kernel dim={len(K)} ({time.time()-t1:.0f}s)")
        sys.stdout.flush()
        pr = {"kernel_dim": len(K), "vectors": []}
        for bi, kb in enumerate(K):
            # symmetrischer Lift
            x = np.zeros(N, dtype=np.int64)
            for i, t in enumerate(kb):
                v = int(t)
                if v > p // 2:
                    v -= p
                x[i] = v
            vecs_np[f"p{p}_b{bi}"] = x.astype(np.int8)
            supp = np.nonzero(x)[0]
            supports[(p, bi)] = set(int(s) for s in supp)
            val_hist = Counter(int(v) for v in x[supp])

            # (b) Dreiecks-Muster
            m_hist = Counter()
            pat_hist = Counter()
            for (c1, c2, c3) in triangles:
                vals = (int(x[c1]), int(x[c2]), int(x[c3]))
                m = sum(1 for v in vals if v != 0)
                m_hist[m] += 1
                if m == 3:
                    a, b, c = sorted(((vals[0]) % p, (vals[1]) % p, (vals[2]) % p))
                    if a == b == c:
                        pat_hist["konstant"] += 1
                    elif a == b or b == c:
                        pat_hist["zweigleich"] += 1
                    else:
                        pat_hist["verschieden"] += 1

            # (c) Lokalisierung: Traegerdichte in NWIN Fenstern
            win = N // NWIN
            dens = [0] * NWIN
            for s in supp:
                dens[min(int(s) // win, NWIN - 1)] += 1
            dmax = max(dens) if len(supp) else 0
            d_nonzero = sum(1 for d in dens if d > 0)

            # (3) Stage-Profil der inzidenten Zeilen
            inc_stages = Counter()
            for s in supp:
                for r in rows_by_col.get(int(s), []):
                    inc_stages[row_stage[r]] += 1

            pr["vectors"].append({
                "basis_index": bi,
                "support_size": int(len(supp)),
                "support_frac": float(len(supp)) / N,
                "value_hist_lift": {str(k): v for k, v in sorted(val_hist.items())},
                "triangle_m_hist": {str(k): v for k, v in sorted(m_hist.items())},
                "triangle_pattern_m3": dict(pat_hist),
                "window_density_max": dmax,
                "windows_nonzero": d_nonzero,
                "window_size": win,
                "incident_stage_hist": dict(inc_stages),
            })
            print(f"[{ts()}]   p={p} b{bi}: |supp|={len(supp)} ({len(supp)/N:.3f}), "
                  f"m3-Muster={dict(pat_hist)}, Fenster>0: {d_nonzero}/{NWIN} ({time.time()-t1:.0f}s)")
            sys.stdout.flush()
        report["per_prime"][str(p)] = pr
        with open(OUT_JSON, "w") as f:
            json.dump(report, f, indent=2)
        np.savez_compressed(OUT_NPZ, **vecs_np)

    # (d) Traeger-Ueberlapp zwischen Primes (erste Basisvektoren)
    keys = sorted(supports.keys())
    overlaps = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = supports[keys[i]], supports[keys[j]]
            inter = len(a & b)
            uni = len(a | b)
            overlaps[f"p{keys[i][0]}b{keys[i][1]}_vs_p{keys[j][0]}b{keys[j][1]}"] = {
                "intersection": inter, "union": uni,
                "jaccard": (inter / uni) if uni else 0.0}
    report["support_overlaps"] = overlaps
    report["status"] = "done"
    report["total_seconds"] = time.time() - t0
    with open(OUT_JSON, "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# M-DET 2: Kernvektor-Forensik 60168 ({})".format(date.today()), ""]
    lines.append("Dreiecke (manin, 3 nnz): {} | Stages: {}".format(len(triangles), dict(stage_hist)))
    lines.append("")
    lines.append("| p | dim | |supp| | m3-Muster (konst/zweigl/versch) | Fenster>0/64 |")
    lines.append("|---|---|---|---|---|")
    for p in PRIMES:
        for v in report["per_prime"][str(p)]["vectors"]:
            pat = v["triangle_pattern_m3"]
            lines.append("| {} | {} | {} ({:.3f}) | {}/{}/{} | {} |".format(
                p, report["per_prime"][str(p)]["kernel_dim"],
                v["support_size"], v["support_frac"],
                pat.get("konstant", 0), pat.get("zweigleich", 0), pat.get("verschieden", 0),
                v["windows_nonzero"]))
    lines.append("")
    lines.append("Traeger-Ueberlapp (Jaccard): " + json.dumps(
        {k: round(o["jaccard"], 4) for k, o in overlaps.items()}))
    lines.append("")
    lines.append("Total: {:.0f}s".format(report["total_seconds"]))
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON, " NPZ:", OUT_NPZ)
    return 0


if __name__ == "__main__":
    sys.exit(main())
