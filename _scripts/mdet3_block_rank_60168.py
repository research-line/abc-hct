#!/usr/bin/env python3
"""
M-DET 3: Block-Rang-Test — welche Konstruktionsschicht traegt jeden Drop-Prime?
(Sage, Mac). Satz-B-Baustein-Diagnostik nach dem Torsions-Lemma.

Das 60168-Witness besteht aus zwei Stage-Bloecken:
  (M) Manin-T-Relationen nach S/I-Quotient  (~21.104 Zeilen)
  (H) T_5-minus-2-Hecke-Saturierung          (~10.576 Zeilen)
Das volle System (M+H, 31.680 Zeilen quadratisch) hat Drop-Primes
{2,3,5,31} (M-DET 1a). FRAGE: Bei welchem p sitzt der Rangdefekt schon
im Manin-Block (M) — geometrisch, level-uniform (Torsions-Lemma) — und
bei welchem entsteht er erst durch die Hecke-Schicht (H) — arithmetisch
(Eichler-Shimura mod 5 / nicht-rationale Bahn fuer 31)?

METHODE (wohldefiniert trotz nicht-quadratischer Bloecke): pro Block B
und Prim p den GF(p)-Rang vergleichen mit dem ℚ-Rang (= GF(P0)-Rang an
einem grossen Kontrollprim P0, der KEIN Drop ist). Block-Defekt_p(B) :=
rank_ℚ(B) − rank_{GF(p)}(B).
  Defekt_p(M) > 0  ⟹  p ist GEOMETRISCH (Manin-Relationsstruktur).
  Defekt_p(M) = 0 aber Defekt_p(M+H) > 0  ⟹  p kommt von der HECKE-Schicht.
Erwartung aus Forensik/Lemma: 2,3 geometrisch (Defekt schon in M);
5 teils/Hecke; 31 erst in M+H (arithmetisch).

Output: _results/mdet3_block_rank_60168_<date>.{json,md}
"""
import json, sys, time
from datetime import date
from pathlib import Path

WITNESS = Path("_results/rc3c_source_witness_60168_raw_2026-05-12/N60168_raw_sign1/source_rows.jsonl")
WQ = 3863
PRIMES = [101, 2, 3, 5, 31, 7]   # 101 = Kontroll-Prim (ℚ-Rang-Proxy), kein Drop
OUT_JSON = "_results/mdet3_block_rank_60168_{}.json".format(date.today())
OUT_MD = "_results/mdet3_block_rank_60168_{}.md".format(date.today())


def main():
    t0 = time.time()
    ts = lambda: time.strftime("%H:%M:%S")
    half = WQ // 2
    print("=== M-DET 3: Block-Rang-Test (Manin vs Hecke) ===")
    from sage.all import GF, matrix

    # Zeilen mit Stage-Label lesen; in Manin (M) und Hecke (H) trennen.
    manin_entries = {}    # (row, col) -> val   (Block M, eigene Zeilennummerierung)
    full_entries = {}     # (row, col) -> val   (Block M+H)
    m_row = 0
    f_row = 0
    ncols = 0
    with open(WITNESS) as f:
        for line in f:
            rec = json.loads(line)
            stage = str(rec.get("stage", "?"))
            is_manin = "manin" in stage
            cells = []
            for c, v in rec["row"]:
                v = int(v)
                if v > half:
                    v -= WQ
                if v:
                    c = int(c)
                    cells.append((c, v))
                    if c + 1 > ncols:
                        ncols = c + 1
            for c, v in cells:
                full_entries[(f_row, c)] = v
                if is_manin:
                    manin_entries[(m_row, c)] = v
            f_row += 1
            if is_manin:
                m_row += 1
    print(f"[{ts()}] geladen: Manin {m_row} Zeilen, voll {f_row} Zeilen, ncols={ncols} "
          f"({time.time()-t0:.0f}s)")
    sys.stdout.flush()

    blocks = {
        "manin": (m_row, manin_entries),
        "full": (f_row, full_entries),
    }
    ranks = {b: {} for b in blocks}
    report = {"date": str(date.today()), "level": 60168, "ncols": ncols,
              "manin_rows": m_row, "full_rows": f_row,
              "control_prime": 101, "ranks": ranks, "status": "running"}

    for bname, (nrows, ent) in blocks.items():
        for p in PRIMES:
            t1 = time.time()
            M = matrix(GF(p), nrows, ncols, ent, sparse=True)
            r = int(M.rank())
            del M
            ranks[bname][str(p)] = r
            print(f"[{ts()}] {bname} p={p}: rank={r} ({time.time()-t1:.0f}s)")
            sys.stdout.flush()
            with open(OUT_JSON, "w") as fp:
                json.dump(report, fp, indent=2)

    # Defekte relativ zum Kontroll-Prim 101
    P0 = "101"
    defects = {}
    for bname in blocks:
        rq = ranks[bname][P0]
        defects[bname] = {p: rq - ranks[bname][p] for p in ranks[bname] if p != P0}
    report["defects_vs_control"] = defects
    # Klassifikation pro Drop-Prim
    classification = {}
    for p in [str(x) for x in PRIMES if x != 101]:
        dm = defects["manin"].get(p, 0)
        dfull = defects["full"].get(p, 0)
        if dfull == 0:
            cls = "kein Drop"
        elif dm > 0:
            cls = "GEOMETRISCH (Defekt im Manin-Block)"
        else:
            cls = "HECKE (Defekt erst im vollen System)"
        classification[p] = {"defect_manin": dm, "defect_full": dfull, "class": cls}
    report["classification"] = classification
    report["status"] = "done"
    report["total_seconds"] = time.time() - t0
    with open(OUT_JSON, "w") as fp:
        json.dump(report, fp, indent=2)

    lines = ["# M-DET 3: Block-Rang-Test Manin vs Hecke, 60168 ({})".format(date.today()), ""]
    lines.append(f"Manin-Block {m_row} Zeilen, volles System {f_row} Zeilen, ncols {ncols}.")
    lines.append("Kontroll-Prim 101 (ℚ-Rang-Proxy). Defekt_p(B) = rank_101(B) − rank_p(B).")
    lines.append("")
    lines.append("| p | Defekt Manin | Defekt voll | Klassifikation |")
    lines.append("|---|---|---|---|")
    for p, c in classification.items():
        lines.append(f"| {p} | {c['defect_manin']} | {c['defect_full']} | {c['class']} |")
    lines.append("")
    lines.append("Roh-Ränge:")
    lines.append("| Block | " + " | ".join(f"p={p}" for p in PRIMES) + " |")
    lines.append("|---|" + "|".join("---" for _ in PRIMES) + "|")
    for bname in blocks:
        lines.append(f"| {bname} | " + " | ".join(str(ranks[bname][str(p)]) for p in PRIMES) + " |")
    lines.append("")
    lines.append(f"Total: {time.time()-t0:.0f}s")
    with open(OUT_MD, "w") as fp:
        fp.write("\n".join(lines) + "\n")
    print("JSON:", OUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
