#!/usr/bin/env python3
"""S5 full-relation rank scan in the fixed RC3d GF(3863) quotient.

The exception-prime scan of a source minor can show rank drops modulo small
primes.  This script distinguishes a bad minor from a structural rank drop:
it reconstructs the full row set in the same 31680-column GF(3863) quotient
used by RC3d, then reduces those integer row coordinates modulo selected
test primes and recomputes ranks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from typing import Any


TRACE_VALUES = {
    "raw": {5: 2, 7: 0, 11: 0, 13: -6},
    "anc": {5: 2, 7: 0, 11: 0, 13: -6},
}


def parse_primes(raw: str) -> list[int]:
    return [int(part) for part in raw.replace(",", " ").split() if part.strip()]


def parse_hecke_plan(raw: str | None, fallback_prime: int, fallback_batches: int) -> list[tuple[int, int]]:
    if not raw:
        return [(fallback_prime, fallback_batches)]
    plan: list[tuple[int, int]] = []
    for part in raw.replace(",", " ").split():
        if not part.strip():
            continue
        if ":" in part:
            prime_raw, batches_raw = part.split(":", 1)
            plan.append((int(prime_raw), int(batches_raw)))
        else:
            plan.append((int(part), fallback_batches))
    return plan


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_stage_name(stage: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in stage)


def symmetric_lift(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def canonical_row(row: dict[int, int], q: int) -> str:
    parts = []
    for col in sorted(row):
        val = int(row[col]) % q
        if val:
            parts.append(f"{int(col)}:{val}")
    return ",".join(parts)


def row_line_hash(stage: str, stage_row_index: int, row: dict[int, int], q: int) -> str:
    line = f"{stage}\t{stage_row_index}\t{canonical_row(row, q)}\n"
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def load_source_rows(case_dir: Path, q: int) -> tuple[dict[str, Any], list[dict[int, int]]]:
    manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
    rows_path = case_dir / str(manifest["rows_file"])
    if file_sha256(rows_path) != manifest.get("rows_file_sha256"):
        raise RuntimeError(f"source rows sha256 mismatch: {rows_path}")
    rows: list[dict[int, int]] = []
    for line in rows_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        row: dict[int, int] = {}
        for raw_col, raw_value in record["row"]:
            val = int(raw_value) % q
            if val:
                row[int(raw_col)] = val
        rows.append(row)
    return manifest, rows


def sage_rank(rows: list[dict[int, int]], ncols: int, q: int, prime: int) -> int:
    from sage.all import GF, matrix  # type: ignore

    field = GF(prime)
    entries: dict[tuple[int, int], Any] = {}
    for i, row in enumerate(rows):
        for col, value in row.items():
            reduced = symmetric_lift(int(value), q) % prime
            if reduced:
                entries[(i, int(col))] = field(reduced)
    mat = matrix(field, len(rows), ncols, entries, sparse=True)
    return int(mat.rank())


class SparseIncrementalRankMod:
    def __init__(self, ncols: int, q: int, prime: int, pivot_strategy: str = "max"):
        self.ncols = int(ncols)
        self.q = int(q)
        self.prime = int(prime)
        self.pivot_strategy = pivot_strategy
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0
        self.rows_seen = 0

    def row_mod_prime(self, raw_row: dict[int, int]) -> dict[int, int]:
        p = self.prime
        return {
            int(col): symmetric_lift(int(value), self.q) % p
            for col, value in raw_row.items()
            if symmetric_lift(int(value), self.q) % p
        }

    def add(self, raw_row: dict[int, int]) -> bool:
        self.rows_seen += 1
        p = self.prime
        row = self.row_mod_prime(raw_row)
        while row:
            pivot = min(row) if self.pivot_strategy == "min" else max(row)
            value = row[pivot] % p
            if pivot in self.basis:
                factor = value
                basis_row = self.basis[pivot]
                for col, basis_value in basis_row.items():
                    new = (row.get(col, 0) - factor * basis_value) % p
                    if new:
                        row[col] = new
                    elif col in row:
                        del row[col]
            else:
                inv = pow(value, -1, p)
                self.basis[pivot] = {
                    col: (val * inv) % p
                    for col, val in row.items()
                    if (val * inv) % p
                }
                self.rank += 1
                return True
        return False


def stage_expected_digests(transcript_dir: Path | None) -> dict[str, str]:
    if transcript_dir is None:
        return {}
    payload = json.loads((transcript_dir / "manifest.json").read_text(encoding="utf-8"))
    return {
        str(stage["stage"]): str(stage["row_transcript_sha256"])
        for stage in payload.get("stages", [])
        if "stage" in stage and "row_transcript_sha256" in stage
    }


def reconstruct_rows(args: argparse.Namespace) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]]]:
    from sage.all import GF  # type: ignore
    from sage.modular.modsym.heilbronn import HeilbronnCremona, HeilbronnMerel  # type: ignore
    from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0  # type: ignore
    from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient  # type: ignore

    q = int(args.q)
    field = GF(q)
    syms = ManinSymbolList_gamma0(args.level, 2)
    nsyms = len(syms)
    rels = set(modS_relations(syms))
    if args.sign in (-1, 1):
        rels.update(modI_relations(syms, args.sign))
    mod = sparse_2term_quotient(rels, nsyms, field)

    rep_to_col: dict[int, int] = {}
    mod_map: list[tuple[int, Any] | None] = []
    for entry in mod:
        rep, scalar = entry
        if scalar == 0:
            mod_map.append(None)
            continue
        rep_i = int(rep)
        if rep_i not in rep_to_col:
            rep_to_col[rep_i] = len(rep_to_col)
        mod_map.append((rep_to_col[rep_i], field(scalar)))
    ncols = len(rep_to_col)

    def reduce_terms(terms: list[tuple[int, Any]]) -> dict[int, int]:
        row: dict[int, Any] = {}
        for j, coeff in terms:
            mapped = mod_map[int(j)]
            if mapped is None:
                continue
            col, scalar = mapped
            val = field(coeff) * scalar
            if val == 0:
                continue
            row[col] = row.get(col, field(0)) + val
            if row[col] == 0:
                del row[col]
        return {int(col): int(val) % q for col, val in row.items() if int(val) % q}

    def matrices_for_p(p: int) -> list[list[int]]:
        if args.hecke_family == "cremona":
            return HeilbronnCremona(p).to_list()
        if args.hecke_family == "merel":
            return HeilbronnMerel(p).to_list()
        if args.hecke_family == "standard":
            return [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]
        raise ValueError(f"unknown Hecke family: {args.hecke_family}")

    expected = stage_expected_digests(args.transcript_dir)
    stage_records: list[dict[str, Any]] = []
    row_records: list[dict[str, Any]] = []
    if args.repair_transcript_dir is not None:
        args.repair_transcript_dir.mkdir(parents=True, exist_ok=True)

    def add_stage(stage: str, row_iter: Any, limit: int | None = None) -> None:
        stage_hash = hashlib.sha256()
        rows_added = 0
        nnz_added = 0
        started = time.perf_counter()
        row_hash_handle = None
        row_hash_path = None
        row_hash_index_file = None
        if args.repair_transcript_dir is not None:
            row_hash_index_file = f"{safe_stage_name(stage)}.rowhashes.jsonl"
            row_hash_path = args.repair_transcript_dir / row_hash_index_file
            row_hash_handle = row_hash_path.open("w", encoding="utf-8")
        try:
            for raw_row in row_iter:
                if limit is not None and rows_added >= limit:
                    break
                if not raw_row:
                    continue
                line = f"{stage}\t{rows_added}\t{canonical_row(raw_row, q)}\n"
                digest = hashlib.sha256(line.encode("utf-8")).hexdigest()
                stage_hash.update(line.encode("utf-8"))
                if row_hash_handle is not None:
                    row_hash_handle.write(json.dumps(
                        {
                            "stage_row_index": rows_added,
                            "row_line_sha256": digest,
                        },
                        sort_keys=True,
                    ) + "\n")
                row_records.append(
                    {
                        "stage": stage,
                        "stage_row_index": rows_added,
                        "row": raw_row,
                        "row_line_sha256": digest,
                    }
                )
                rows_added += 1
                nnz_added += len(raw_row)
        finally:
            if row_hash_handle is not None:
                row_hash_handle.close()
        digest = stage_hash.hexdigest()
        record = {
            "stage": stage,
            "rows_added": rows_added,
            "nnz_added": nnz_added,
            "row_transcript_sha256": digest,
            "expected_row_transcript_sha256": expected.get(stage),
            "transcript_match": None if stage not in expected else expected[stage] == digest,
            "seconds_generate": time.perf_counter() - started,
        }
        if row_hash_path is not None and row_hash_index_file is not None:
            record["row_hash_index_file"] = row_hash_index_file
            record["row_hash_index_sha256"] = file_sha256(row_hash_path)
            (args.repair_transcript_dir / f"{safe_stage_name(stage)}.sha256").write_text(digest + "\n", encoding="utf-8")
        stage_records.append(record)

    def manin_rows() -> Any:
        for i in range(nsyms):
            terms: list[tuple[int, Any]] = [(i, field(1))]
            terms.extend(syms.apply_T(i))
            terms.extend(syms.apply_TT(i))
            yield reduce_terms(terms)

    add_stage("manin_T_relations_after_SI", manin_rows())

    hecke_plan = parse_hecke_plan(args.hecke_plan, int(args.hecke_prime), int(args.max_hecke_batches))
    for hecke_prime, max_batches in hecke_plan:
        ap = TRACE_VALUES[args.mode][hecke_prime]
        mats = matrices_for_p(hecke_prime)
        batch: list[dict[int, int]] = []
        batch_index = 0
        for i in range(nsyms):
            terms = [(i, field(-ap))]
            for mat in mats:
                terms.extend(syms.apply(i, mat))
            batch.append(reduce_terms(terms))
            if len(batch) < args.hecke_batch_size:
                continue
            batch_index += 1
            stage = f"T_{hecke_prime}_minus_{ap}_batch_{batch_index}"
            add_stage(stage, batch)
            batch = []
            if batch_index >= max_batches:
                break
        if batch and batch_index < max_batches:
            batch_index += 1
            stage = f"T_{hecke_prime}_minus_{ap}_batch_{batch_index}"
            add_stage(stage, batch)

    if args.repair_transcript_dir is not None:
        transcript_manifest = {
            "certificate_version": "s5-fixedquotient-rowhash-1",
            "level": args.level,
            "mode": args.mode,
            "sign": args.sign,
            "q": args.q,
            "columns_after_2term": ncols,
            "hecke_plan": args.hecke_plan,
            "stages": stage_records,
        }
        (args.repair_transcript_dir / "manifest.json").write_text(
            json.dumps(transcript_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return ncols, stage_records, row_records


def write_repair_witness(
    args: argparse.Namespace,
    ncols: int,
    stages: list[dict[str, Any]],
    row_records: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if args.repair_witness_dir is None:
        return None
    if args.repair_prime is None:
        raise ValueError("--repair-prime is required when --repair-witness-dir is used")
    run_dir = args.repair_witness_dir / f"N{args.level}_{args.mode}_p{args.repair_prime}_sign{args.sign}"
    run_dir.mkdir(parents=True, exist_ok=True)
    rows_path = run_dir / "repair_rows.jsonl"
    ranker = SparseIncrementalRankMod(ncols, args.q, args.repair_prime, args.pivot_strategy)
    exported = 0
    exported_nnz = 0
    started = time.perf_counter()
    with rows_path.open("w", encoding="utf-8") as handle:
        for record in row_records:
            row = record["row"]
            if not ranker.add(row):
                continue
            exported_record = {
                "row_id": f"{record['stage']}/{record['stage_row_index']}",
                "stage": record["stage"],
                "stage_row_index": record["stage_row_index"],
                "row_line_sha256": record["row_line_sha256"],
                "row": [[int(col), int(row[col]) % args.q] for col in sorted(row) if int(row[col]) % args.q],
            }
            handle.write(json.dumps(exported_record, sort_keys=True) + "\n")
            exported += 1
            exported_nnz += len(exported_record["row"])
            if ranker.rank == ncols:
                break
    manifest = {
        "certificate_version": "s5-fixedquotient-repair-witness-1",
        "witness_type": "fixedquotient_repair_rows",
        "level": args.level,
        "mode": args.mode,
        "sign": args.sign,
        "q": args.q,
        "repair_prime": args.repair_prime,
        "columns_after_2term": ncols,
        "ncols": ncols,
        "rank": ranker.rank,
        "full_rank": ranker.rank == ncols,
        "pivot_strategy": args.pivot_strategy,
        "rows_file": rows_path.name,
        "rows_file_sha256": file_sha256(rows_path),
        "repair_row_count": exported,
        "repair_row_nnz": exported_nnz,
        "rows_seen": ranker.rows_seen,
        "seconds": time.perf_counter() - started,
        "hecke_plan": args.hecke_plan,
        "source": "rows reconstructed in the fixed GF(3863) quotient and reduced modulo repair_prime",
        "stages": stages,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"run_dir": str(run_dir), "manifest": manifest}


def write_markdown(payload: dict[str, Any], out_md: Path) -> None:
    lines = [
        "# S5 Fixed-Quotient Full Relation Rank",
        "",
        f"Level `{payload['level']}`, mode `{payload['mode']}`, q `{payload['q']}`.",
        f"Columns in fixed quotient: `{payload['ncols']}`.",
        "",
        "## Stage Reconstruction",
        "",
        "| stage | rows | nnz | transcript match | seconds |",
        "|---|---:|---:|---|---:|",
    ]
    for stage in payload["stages"]:
        lines.append(
            f"| {stage['stage']} | {stage['rows_added']} | {stage['nnz_added']} | "
            f"{stage['transcript_match'] if stage['transcript_match'] is not None else 'not checked'} | "
            f"{stage['seconds_generate']:.3f} |"
        )
    lines.extend(["", "## Ranks", "", "| prime | source rank | full rank | repaired? | seconds source | seconds full |", "|---:|---:|---:|---|---:|---:|"])
    for result in payload["prime_results"]:
        lines.append(
            f"| {result['prime']} | {result.get('source_rank')} | {result['full_rank']} | "
            f"{result['repaired_to_full_rank']} | {result.get('seconds_source_rank', 0):.3f} | "
            f"{result['seconds_full_rank']:.3f} |"
        )
    if payload.get("repair_witness"):
        manifest = payload["repair_witness"]["manifest"]
        lines.extend(
            [
                "",
                "## Repair Witness",
                "",
                f"Directory: `{payload['repair_witness']['run_dir']}`.",
                f"Prime: `{manifest['repair_prime']}`.",
                f"Rank: `{manifest['rank']}` / `{manifest['ncols']}`.",
                f"Rows exported: `{manifest['repair_row_count']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A repaired result means the full reconstructed row set has full rank modulo",
            "the test prime in the same GF(3863)-quotient coordinates, even if the",
            "exported source minor had dropped rank modulo that prime.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=60168)
    parser.add_argument("--mode", choices=["raw", "anc"], default="raw")
    parser.add_argument("--sign", type=int, choices=[-1, 0, 1], default=1)
    parser.add_argument("--q", type=int, default=3863)
    parser.add_argument("--hecke-prime", type=int, default=5)
    parser.add_argument("--hecke-plan", help="Comma/space list like '5:13,7:1'. Overrides --hecke-prime for row generation.")
    parser.add_argument("--hecke-family", choices=["cremona", "merel", "standard"], default="standard")
    parser.add_argument("--hecke-batch-size", type=int, default=1000)
    parser.add_argument("--max-hecke-batches", type=int, default=13)
    parser.add_argument("--test-primes", default="2 3 5 31")
    parser.add_argument("--source-witness-dir", type=Path)
    parser.add_argument("--transcript-dir", type=Path)
    parser.add_argument("--repair-witness-dir", type=Path)
    parser.add_argument("--repair-transcript-dir", type=Path)
    parser.add_argument("--repair-prime", type=int)
    parser.add_argument("--pivot-strategy", choices=["max", "min"], default="max")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    test_primes = parse_primes(args.test_primes)
    ncols, stages, full_records = reconstruct_rows(args)
    full_rows = [record["row"] for record in full_records]
    source_rows: list[dict[int, int]] | None = None
    source_manifest: dict[str, Any] | None = None
    if args.source_witness_dir is not None:
        source_manifest, source_rows = load_source_rows(args.source_witness_dir, args.q)
    repair_witness = write_repair_witness(args, ncols, stages, full_records)

    prime_results = []
    for prime in test_primes:
        source_rank = None
        source_seconds = None
        if source_rows is not None:
            t0 = time.perf_counter()
            source_rank = sage_rank(source_rows, ncols, args.q, prime)
            source_seconds = time.perf_counter() - t0
        t0 = time.perf_counter()
        full_rank = sage_rank(full_rows, ncols, args.q, prime)
        full_seconds = time.perf_counter() - t0
        prime_results.append(
            {
                "prime": prime,
                "source_rank": source_rank,
                "full_rank": full_rank,
                "ncols": ncols,
                "source_defect": None if source_rank is None else ncols - source_rank,
                "full_defect": ncols - full_rank,
                "repaired_to_full_rank": full_rank == ncols,
                "seconds_source_rank": source_seconds,
                "seconds_full_rank": full_seconds,
            }
        )

    payload = {
        "tool": "mstar_s5_fixedquotient_full_rank",
        "level": args.level,
        "mode": args.mode,
        "sign": args.sign,
        "q": args.q,
        "hecke_prime": args.hecke_prime,
        "hecke_plan": args.hecke_plan,
        "hecke_family": args.hecke_family,
        "hecke_batch_size": args.hecke_batch_size,
        "max_hecke_batches": args.max_hecke_batches,
        "ncols": ncols,
        "total_rows": len(full_rows),
        "total_nnz": sum(len(row) for row in full_rows),
        "source_manifest": source_manifest,
        "repair_witness": repair_witness,
        "stages": stages,
        "prime_results": prime_results,
        "seconds_total": time.perf_counter() - started,
    }
    args.out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(payload, args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
