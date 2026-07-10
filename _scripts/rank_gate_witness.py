#!/usr/bin/env python3
"""rank_gate_witness.py -- Kanonisches Rang-Gate im rohen Witness-Spaltenraum.

Ersetzt den obsoleten mspetersson-Tensor-Wrapper (OOM auf 80224) durch die
Kopplungskonstante c aus drei Sparse-Rang-Aussagen. Reine Sparse-Lineare-
Algebra mod q -- KEIN Sage, KEIN PARI/msinit, KEINE M0-Bridge. Nur stdlib.

Kanonische Definition (Addendum Nr.5, 2026-07-10,
  _proof-notes/MG_h3a_manin_pairing_identification_2026-05-16.md):

  Roher Witness-Spaltenraum F_q^ncols. Source-Zeilen S (origin=="source")
  und Repair-Zeile r_N (origin=="repair_only") direkt aus mixed_rows.jsonl;
  die row-Werte sind bereits mod-q-Residuen (q aus manifest, NICHT raten).

  phi := rechter Nullvektor der Source-Zeilen-Matrix (S . phi = 0);
  kernel_dim = ncols - rank(S); das Gate ist nur bei kernel_dim == 1 sauber
  (phi bis auf Skalar eindeutig).
  (Z1')  eval_rN  := r_N . phi           (!= 0; N=109-Referenz: 705 mod 3863)
  (Z2')  h7e0_Fan := 2 e0 + e1 + ... + e6  (SPALTEN-Indikator auf den rohen
         Witness-Spalten 0..6; satz-treue, "Witness-seitige" Fan-Formel der
         CFR-5-Eigenschaft, Addendum Nr.5 (3)).  eval_h7e0 := h7e0_Fan . phi
  c := eval_h7e0 . eval_rN^{-1} mod q.  (== h7e0 == c . r_N mod Source-Span;
       bei kernel_dim==1 ist Source-Span = phi^perp -> c kanonisch, Skalar
       kuerzt sich.)  N=109 (gebridgte Referenz): c = 400, konventionsrobust
       (standard + frey) -- Bridge-Invarianz der Kopplung.

Zwei aequivalente Rechenwege (--method):
  * raw       Single-Stage: alle Source-Zeilen in einem Basis-Objekt ueber
              F_q^ncols. Reproduziert die phi-Normierung des 109-Smokes exakt
              (eval_rN == 705). Fuer grosse Level teuer (Fill-in), daher nur
              fuer kleine Faelle / Selbstvalidierung.
  * quotient  Zwei-Stufen (wie mstar_h3a_restline_kernel_quotient.py):
              (1) manin_T-Basis bauen (source_kind=="manin_T"; billig, sparse),
              (2) Hecke-Zeilen + r_N + h7e0 gegen manin_T reduzieren und in den
              kompakten Quotienten projizieren, (3) Kern der projizierten
              Hecke-Matrix. Skaliert auf 80224. Der Kern darf via --kernel-json
              aus einem kernel_quotient-Artefakt geladen werden (dann keine
              teure Hecke-Elimination); die Index-Ausrichtung wird ueber die
              Reproduktion von repair_pairing gegengeprueft.
  eval_rN, eval_h7e0 sind unter beiden Wegen gleich (bis auf die phi-Normierung),
  c ist identisch. Grund: fuer phi in ker(S) gilt v . phi_raw = pi(v) . phi_quot,
  weil phi_raw die manin_T-Zeilen annihiliert (pi = Reduktion mod manin_T).

Kein abc-Claim; Instanz-Zertifikat im rohen Witness-Raum; Klassen-/odd-Hebung
offen. Autor: LG.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FAN_DIRECT = {0: 2, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}      # h7e0 = 2 e0 + e1 + ... + e6
FAN_SHIFT1 = {1: 2, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}      # Kontroll-Layout e_c=Spalte c+1


def signed_lift(value: int, q: int) -> int:
    v = value % q
    if v > q // 2:
        v -= q
    return int(v)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SparseRowBasis:
    """Streaming max-pivot echelon basis over F_q (rows = dict col->val)."""

    def __init__(self, q: int):
        self.q = int(q)
        self.basis: dict[int, dict[int, int]] = {}
        self.rank = 0
        self.max_basis_row_len = 0

    def add_dict(self, raw_row: dict[int, int]) -> bool:
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            pivot = max(row)
            value = row[pivot] % q
            if pivot in self.basis:
                factor = value
                for c, v in self.basis[pivot].items():
                    new = (row.get(c, 0) - factor * v) % q
                    if new:
                        row[c] = new
                    elif c in row:
                        del row[c]
            else:
                inv = pow(value, -1, q)
                normalized = {c: (v * inv) % q for c, v in row.items() if (v * inv) % q}
                self.basis[pivot] = normalized
                self.rank += 1
                self.max_basis_row_len = max(self.max_basis_row_len, len(normalized))
                return True
        return False

    def add_pairs(self, row_pairs: list[list[int]]) -> bool:
        return self.add_dict({int(c): int(v) for c, v in row_pairs})

    def reduce(self, raw_row: dict[int, int]) -> dict[int, int]:
        q = self.q
        row = {int(c): int(v) % q for c, v in raw_row.items() if int(v) % q}
        while row:
            candidates = [c for c in row if c in self.basis]
            if not candidates:
                break
            pivot = max(candidates)
            factor = row[pivot] % q
            for c, v in self.basis[pivot].items():
                new = (row.get(c, 0) - factor * v) % q
                if new:
                    row[c] = new
                elif c in row:
                    del row[c]
        return row

    def free_columns(self, ncols: int) -> list[int]:
        pivots = set(self.basis)
        return [c for c in range(ncols) if c not in pivots]

    def solve_null_vector(self, ncols: int, free_col: int | None = None) -> dict[int, int]:
        free_cols = self.free_columns(ncols)
        if not free_cols:
            raise ValueError("matrix has full rank; no free column available")
        if free_col is None:
            free_col = free_cols[0]
        if free_col not in free_cols:
            raise ValueError(f"requested free column {free_col} is not free")
        q = self.q
        x: dict[int, int] = {free_col: 1}
        for pivot in sorted(self.basis):
            row = self.basis[pivot]
            total = 0
            for col, value in row.items():
                if col == pivot:
                    continue
                total = (total + value * x.get(col, 0)) % q
            value = (-total) % q
            if value:
                x[pivot] = value
        return x


def record_kind(record: dict[str, Any]) -> str:
    meta = record.get("row_metadata") or {}
    if meta.get("source_kind"):
        return str(meta["source_kind"])
    if str(record.get("stage", "")) == "manin_T_relations_after_SI":
        return "manin_T"
    return "hecke"


def read_manifest(case_dir: Path) -> dict[str, Any]:
    return json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))


def iter_rows(case_dir: Path, manifest: dict[str, Any]):
    rows_path = case_dir / str(manifest.get("rows_file", "mixed_rows.jsonl"))
    with rows_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def dot_sparse(row: dict[int, int], vec: dict[int, int], q: int) -> int:
    return sum((int(v) % q) * vec.get(int(c), 0) for c, v in row.items()) % q


def write_status(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    payload = dict(payload)
    payload["updated"] = now_iso()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def base_output(manifest: dict[str, Any], case_dir: Path, q: int, ncols: int,
                method: str) -> dict[str, Any]:
    return {
        "tool": "rank_gate_witness",
        "version": 2,
        "date": now_iso(),
        "author": "LG",
        "method": method,
        "case_dir": str(case_dir),
        "level": manifest.get("level"),
        "mode": manifest.get("mode"),
        "q": q,
        "q_from_manifest": int(manifest["q"]),
        "ncols": ncols,
        "rows_file_sha256": manifest.get("rows_file_sha256"),
        "repair_only_row_id_manifest": manifest.get("repair_only_row_id"),
    }


def finalize(out: dict[str, Any], eval_rN: int, eval_h7e0: int, eval_h7e0_shift1: int,
             kernel_dim: int, q: int, ref_eval_rn: int | None, ref_c: int | None,
             mapping_note: dict[str, Any]) -> None:
    out["eval_rN"] = int(eval_rN)
    out["eval_rN_signed"] = signed_lift(eval_rN, q)
    out["eval_rN_nonzero"] = eval_rN % q != 0
    out["eval_h7e0"] = int(eval_h7e0 % q)
    out["eval_h7e0_signed"] = signed_lift(eval_h7e0, q)
    out["column_mapping_used"] = mapping_note
    out["kernel_dim_gt_1"] = kernel_dim != 1
    out["c_ambiguous"] = kernel_dim != 1

    if eval_rN % q != 0:
        inv = pow(eval_rN % q, -1, q)
        c = (eval_h7e0 * inv) % q
        out["c"] = int(c)
        out["c_signed"] = signed_lift(c, q)
        out["alt_layout_shift1"] = {
            "h7e0_fan": {str(k): v for k, v in FAN_SHIFT1.items()},
            "eval_h7e0_signed": signed_lift(eval_h7e0_shift1, q),
            "c_signed": signed_lift((eval_h7e0_shift1 * inv) % q, q),
            "note": "e_c = Spalte c+1; NUR Kontrolle. Bei N=109 ergibt dies NICHT c=400.",
        }
    else:
        out["c"] = None
        out["c_signed"] = None
        out["c_note"] = "eval_rN == 0 -> Restlinie verschwindet, c undefiniert (Gate NEGATIV)"

    ref: dict[str, Any] = {}
    if ref_eval_rn is not None:
        ref["ref_eval_rN"] = int(ref_eval_rn)
        ref["eval_rN_matches_ref"] = (eval_rN % q) == (int(ref_eval_rn) % q)
        if ref_eval_rn % q != 0 and eval_rN % q != 0:
            ref["eval_rN_over_ref"] = int((eval_rN * pow(int(ref_eval_rn), -1, q)) % q)
    if ref_c is not None and out.get("c") is not None:
        ref["ref_c"] = int(ref_c)
        ref["c_matches_ref"] = (out["c"] % q) == (int(ref_c) % q)
        ref["bridge_invariance"] = ref["c_matches_ref"]
    out["reference_comparisons"] = ref

    gate_clean = (kernel_dim == 1) and (eval_rN % q != 0)
    out["verdict"] = {
        "kernel_dim": kernel_dim,
        "kernel_dim_is_1": kernel_dim == 1,
        "eval_rN_nonzero": eval_rN % q != 0,
        "c": out.get("c"),
        "c_signed": out.get("c_signed"),
        "gate_clean": bool(gate_clean),
        "bridge_invariance_vs_c400": ref.get("bridge_invariance"),
    }


# --------------------------------------------------------------------------- raw

def run_raw(case_dir: Path, q_override: int | None, status_path: Path | None,
            progress_every: int, ref_eval_rn: int | None, ref_c: int | None) -> dict[str, Any]:
    t0 = time.time()
    manifest = read_manifest(case_dir)
    q = int(q_override) if q_override is not None else int(manifest["q"])
    ncols = int(manifest.get("ncols", manifest.get("columns_after_2term")))
    out = base_output(manifest, case_dir, q, ncols, "raw")

    write_status(status_path, {"phase": "elimination", "method": "raw",
                               "case_dir": str(case_dir), "q": q, "ncols": ncols,
                               "rows_processed": 0, "source_rank": 0, "seconds": 0.0})
    basis = SparseRowBasis(q)
    repair_row = None
    source_count = 0
    for row in iter_rows(case_dir, manifest):
        origin = row.get("origin")
        if origin == "repair_only":
            if repair_row is None:
                repair_row = row
            continue
        if origin != "source":
            continue
        source_count += 1
        basis.add_pairs(row["row"])
        if progress_every and source_count % progress_every == 0:
            write_status(status_path, {"phase": "elimination", "method": "raw",
                                       "case_dir": str(case_dir), "q": q, "ncols": ncols,
                                       "rows_processed": source_count,
                                       "source_rank": basis.rank,
                                       "max_basis_row_len": basis.max_basis_row_len,
                                       "seconds": round(time.time() - t0, 1)})
    if repair_row is None:
        raise ValueError(f"repair row not found in {case_dir}")

    source_rank = basis.rank
    kernel_dim = ncols - source_rank
    free_cols = basis.free_columns(ncols)
    out.update({
        "n_source_rows": source_count, "source_rank": source_rank,
        "kernel_dim": kernel_dim, "max_basis_row_len": basis.max_basis_row_len,
        "repair_only_row_id_seen": repair_row.get("row_id"),
        "repair_id_matches_manifest": repair_row.get("row_id") == manifest.get("repair_only_row_id"),
        "free_columns": free_cols if len(free_cols) <= 64 else {
            "count": len(free_cols), "min": free_cols[0], "max": free_cols[-1]},
    })
    if kernel_dim <= 0:
        out["error"] = "no free column: source matrix has full column rank"
        out["seconds"] = round(time.time() - t0, 1)
        return out

    write_status(status_path, {"phase": "nullvector", "method": "raw", "q": q,
                               "source_rank": source_rank, "kernel_dim": kernel_dim,
                               "seconds": round(time.time() - t0, 1)})
    phi = basis.solve_null_vector(ncols, free_col=free_cols[0])
    out["free_col_used"] = free_cols[0]
    out["phi_normalization"] = f"phi[{free_cols[0]}]=1"
    support = sorted(phi)
    out["phi_support_size"] = len(support)
    out["phi_support_min"] = support[0] if support else None
    out["phi_support_max"] = support[-1] if support else None
    out["phi_at_cols_0_6_signed"] = {str(c): signed_lift(phi.get(c, 0), q) for c in range(7)}
    if len(support) <= 64:
        out["phi_entries_signed"] = [[c, signed_lift(phi[c], q)] for c in support]

    eval_rN = dot_sparse({int(c): int(v) for c, v in repair_row["row"]}, phi, q)
    eval_h7e0 = sum(coeff * phi.get(col, 0) for col, coeff in FAN_DIRECT.items()) % q
    eval_h7e0_shift1 = sum(coeff * phi.get(col, 0) for col, coeff in FAN_SHIFT1.items()) % q
    mapping = {"layout": "direct_witness_columns", "e_c": "raw witness column c (0-indexed)",
               "h7e0_fan": {str(k): v for k, v in FAN_DIRECT.items()},
               "note": "Witness-seitige Fan-Formel h7e0 = 2 e0 + e1 + ... + e6, Addendum Nr.5 (3)."}
    finalize(out, eval_rN, eval_h7e0, eval_h7e0_shift1, kernel_dim, q,
             ref_eval_rn, ref_c, mapping)
    out["seconds"] = round(time.time() - t0, 1)
    write_status(status_path, {"phase": "done", "method": "raw", "q": q,
                               "kernel_dim": kernel_dim, "eval_rN": out["eval_rN"],
                               "c": out.get("c"), "gate_clean": out["verdict"]["gate_clean"],
                               "seconds": out["seconds"]})
    return out


# ---------------------------------------------------------------------- quotient

def load_kernel_json(path: Path) -> dict[str, Any]:
    pj = json.loads(path.read_text(encoding="utf-8"))
    kernel_vec = {int(c): int(v) % int(pj["q"]) for c, v in pj["kernel_entries_mod_q"]}
    return {
        "kernel_vector": kernel_vec,
        "free_columns": [int(c) for c in pj["free_columns"]],
        "quotient_ncols": int(pj["quotient_ncols"]),
        "quotient_rank": int(pj["quotient_rank"]),
        "quotient_kernel_dim": int(pj["quotient_kernel_dim"]),
        "repair_pairing_mod_q": int(pj["repair_pairing_mod_q"]),
        "q": int(pj["q"]),
        "source": str(path),
    }


def project(base: SparseRowBasis, raw_row: dict[int, int],
            col_map: dict[int, int], q: int) -> dict[int, int]:
    rem = base.reduce(raw_row)
    return {col_map[c]: v for c, v in rem.items() if c in col_map and int(v) % q}


def run_quotient(case_dir: Path, q_override: int | None, status_path: Path | None,
                 progress_every: int, ref_eval_rn: int | None, ref_c: int | None,
                 kernel_json: Path | None, annihilation_sample: int = 0) -> dict[str, Any]:
    t0 = time.time()
    manifest = read_manifest(case_dir)
    q = int(q_override) if q_override is not None else int(manifest["q"])
    ncols = int(manifest.get("ncols", manifest.get("columns_after_2term")))
    out = base_output(manifest, case_dir, q, ncols, "quotient")

    loaded = load_kernel_json(kernel_json) if kernel_json else None
    if loaded is not None:
        out["kernel_source"] = {"loaded_from": loaded["source"],
                                "quotient_kernel_dim": loaded["quotient_kernel_dim"],
                                "quotient_ncols": loaded["quotient_ncols"],
                                "quotient_rank": loaded["quotient_rank"]}
        if loaded["q"] != q:
            raise ValueError(f"kernel-json q {loaded['q']} != case q {q}")

    write_status(status_path, {"phase": "manin_T_basis", "method": "quotient",
                               "case_dir": str(case_dir), "q": q, "ncols": ncols,
                               "manin_t_rows": 0, "seconds": 0.0})

    # Pass 1: manin_T basis; buffer hecke rows + repair + row_id checks
    base = SparseRowBasis(q)
    hecke_rows: list[dict[int, int]] = []
    repair_raw: dict[int, int] | None = None
    repair_row_id = None
    manin_rows = 0
    for row in iter_rows(case_dir, manifest):
        origin = str(row.get("origin", ""))
        rd = {int(c): int(v) for c, v in row["row"]}
        if origin == "repair_only":
            repair_raw = rd
            repair_row_id = row.get("row_id")
            continue
        if origin != "source":
            continue
        if record_kind(row) == "manin_T":
            manin_rows += 1
            base.add_dict(rd)
            if progress_every and manin_rows % progress_every == 0:
                write_status(status_path, {"phase": "manin_T_basis", "method": "quotient",
                                           "manin_t_rows": manin_rows, "manin_t_rank": base.rank,
                                           "max_basis_row_len": base.max_basis_row_len,
                                           "seconds": round(time.time() - t0, 1)})
        else:
            hecke_rows.append(rd)
    if repair_raw is None:
        raise ValueError(f"repair row not found in {case_dir}")

    free_cols = base.free_columns(ncols)
    col_map = {c: i for i, c in enumerate(free_cols)}
    quotient_ncols = len(free_cols)
    out.update({
        "manin_t_rows": manin_rows, "manin_t_rank": base.rank,
        "manin_t_max_basis_row_len": base.max_basis_row_len,
        "hecke_rows": len(hecke_rows), "quotient_ncols": quotient_ncols,
        "n_source_rows": manin_rows + len(hecke_rows),
        "repair_only_row_id_seen": repair_row_id,
        "repair_id_matches_manifest": repair_row_id == manifest.get("repair_only_row_id"),
        "manin_t_basis_seconds": round(time.time() - t0, 1),
    })

    # Kernel of the projected Hecke matrix (loaded or computed)
    if loaded is not None:
        # cross-check that our free-column ordering matches the loaded artifact
        aligned = (free_cols == loaded["free_columns"])
        out["free_columns_match_kernel_json"] = bool(aligned)
        if not aligned:
            mism = next((i for i in range(min(len(free_cols), len(loaded["free_columns"])))
                         if free_cols[i] != loaded["free_columns"][i]), None)
            out["free_columns_first_mismatch_index"] = mism
            raise ValueError("free-column ordering differs from kernel-json "
                             f"(first mismatch at quotient index {mism}) -- kernel not aligned")
        kernel_vector = loaded["kernel_vector"]
        quotient_rank = loaded["quotient_rank"]
        kernel_dim = loaded["quotient_kernel_dim"]
    else:
        write_status(status_path, {"phase": "hecke_projection", "method": "quotient",
                                   "hecke_rows": len(hecke_rows), "quotient_ncols": quotient_ncols,
                                   "seconds": round(time.time() - t0, 1)})
        qbasis = SparseRowBasis(q)
        for i, hr in enumerate(hecke_rows):
            qbasis.add_dict(project(base, hr, col_map, q))
            if progress_every and (i + 1) % progress_every == 0:
                write_status(status_path, {"phase": "hecke_elimination", "method": "quotient",
                                           "hecke_processed": i + 1, "hecke_total": len(hecke_rows),
                                           "quotient_rank": qbasis.rank,
                                           "max_basis_row_len": qbasis.max_basis_row_len,
                                           "seconds": round(time.time() - t0, 1)})
        quotient_rank = qbasis.rank
        kernel_dim = quotient_ncols - quotient_rank
        write_status(status_path, {"phase": "nullvector", "method": "quotient",
                                   "quotient_rank": quotient_rank, "kernel_dim": kernel_dim,
                                   "seconds": round(time.time() - t0, 1)})
        kernel_vector = qbasis.solve_null_vector(quotient_ncols) if kernel_dim else {}

    out["quotient_rank"] = quotient_rank
    out["kernel_dim"] = kernel_dim
    out["kernel_support_size"] = len(kernel_vector)

    if kernel_dim <= 0 or not kernel_vector:
        out["error"] = "empty kernel (quotient full rank)"
        out["seconds"] = round(time.time() - t0, 1)
        return out

    # Project repair row and h7e0 fan into the quotient, pair with the kernel
    repair_proj = project(base, repair_raw, col_map, q)
    eval_rN = dot_sparse(repair_proj, kernel_vector, q)
    h7e0_proj = project(base, dict(FAN_DIRECT), col_map, q)
    h7e0_shift1_proj = project(base, dict(FAN_SHIFT1), col_map, q)
    eval_h7e0 = dot_sparse(h7e0_proj, kernel_vector, q)
    eval_h7e0_shift1 = dot_sparse(h7e0_shift1_proj, kernel_vector, q)

    out["repair_projected_support_size"] = len(repair_proj)
    out["h7e0_projected_support_size"] = len(h7e0_proj)

    # Self-check vs. loaded artifact (index alignment): repair pairing must match
    if loaded is not None:
        out["repair_pairing_selfcheck"] = {
            "computed_mod_q": int(eval_rN % q),
            "kernel_json_mod_q": int(loaded["repair_pairing_mod_q"] % q),
            "match": int(eval_rN % q) == int(loaded["repair_pairing_mod_q"] % q),
        }

    # Preliminary c already known -- surface it in the status before the
    # (potentially long) full source-annihilation re-check.
    prelim_c = (eval_h7e0 * pow(eval_rN % q, -1, q)) % q if eval_rN % q else None
    write_status(status_path, {"phase": "eval_done", "method": "quotient", "q": q,
                               "kernel_dim": kernel_dim, "eval_rN": int(eval_rN % q),
                               "eval_rN_signed": signed_lift(eval_rN, q),
                               "eval_h7e0_signed": signed_lift(eval_h7e0, q),
                               "c": prelim_c, "c_signed": signed_lift(prelim_c, q) if prelim_c is not None else None,
                               "repair_pairing_selfcheck": out.get("repair_pairing_selfcheck", {}).get("match"),
                               "note": "c bekannt; source-annihilation-Vollcheck laeuft noch",
                               "seconds": round(time.time() - t0, 1)})

    # Source annihilation confirmation (hecke rows vanish on the kernel).
    # Full check by default; --annihilation-sample N re-checks a spread sample
    # of N hecke rows (fast independent confirmation on very large levels; the
    # loaded kernel artifact already carries its own FULL source_annihilated).
    if annihilation_sample and 0 < annihilation_sample < len(hecke_rows):
        step = len(hecke_rows) / annihilation_sample
        idxs = sorted({int(j * step) for j in range(annihilation_sample)})
        check_items = [(k, hecke_rows[k]) for k in idxs]
        out["annihilation_check_mode"] = f"sampled_{len(idxs)}_of_{len(hecke_rows)}_spread"
    else:
        check_items = list(enumerate(hecke_rows))
        out["annihilation_check_mode"] = "full"
    src_nonzero = 0
    for done, (i, hr) in enumerate(check_items):
        if dot_sparse(project(base, hr, col_map, q), kernel_vector, q):
            src_nonzero += 1
        if progress_every and (done + 1) % progress_every == 0:
            write_status(status_path, {"phase": "source_annihilation_check", "method": "quotient",
                                       "hecke_checked": done + 1, "hecke_total": len(check_items),
                                       "check_mode": out["annihilation_check_mode"],
                                       "source_pairing_nonzero_so_far": src_nonzero,
                                       "c_signed": signed_lift(prelim_c, q) if prelim_c is not None else None,
                                       "seconds": round(time.time() - t0, 1)})
    out["source_rows_checked"] = len(check_items)
    out["source_pairing_nonzero"] = src_nonzero
    out["source_annihilated"] = src_nonzero == 0

    mapping = {"layout": "direct_witness_columns", "e_c": "raw witness column c (0-indexed)",
               "h7e0_fan": {str(k): v for k, v in FAN_DIRECT.items()},
               "projected_to_quotient": True,
               "note": "Witness-seitige Fan-Formel h7e0 = 2 e0 + e1 + ... + e6, Addendum Nr.5 (3); "
                       "gegen manin_T reduziert und in den Quotienten projiziert."}
    finalize(out, eval_rN, eval_h7e0, eval_h7e0_shift1, kernel_dim, q,
             ref_eval_rn, ref_c, mapping)
    out["seconds"] = round(time.time() - t0, 1)
    write_status(status_path, {"phase": "done", "method": "quotient", "q": q,
                               "kernel_dim": kernel_dim, "eval_rN": out["eval_rN"],
                               "c": out.get("c"), "gate_clean": out["verdict"]["gate_clean"],
                               "seconds": out["seconds"]})
    return out


def write_md(out: dict[str, Any], out_md: Path) -> None:
    v = out.get("verdict", {})
    ref = out.get("reference_comparisons", {})
    sc = out.get("repair_pairing_selfcheck")
    lines = [
        f"# Rang-Gate (roher Witness-Raum) -- N={out.get('level')}",
        "",
        "Kein abc-Claim; Instanz-Zertifikat im rohen Witness-Raum; "
        "Klassen-/odd-Hebung offen.",
        "",
        f"Methode: **{out.get('method')}**. Reine Sparse-Lineare-Algebra mod q -- "
        "keine M0-Bridge, kein Sage/PARI. phi = rechter Nullvektor der Source-Zeilen; "
        "c := (h7e0_Fan . phi) / (r_N . phi) mod q.",
        "",
        "```text",
        f"case:                  {out.get('case_dir')}",
        f"q:                     {out.get('q')}",
        f"ncols (V_SI):          {out.get('ncols')}",
        f"source rows:           {out.get('n_source_rows')}",
    ]
    if out.get("method") == "quotient":
        lines += [
            f"manin_T rows/rank:     {out.get('manin_t_rows')} / {out.get('manin_t_rank')}",
            f"hecke rows:            {out.get('hecke_rows')}",
            f"quotient ncols/rank:   {out.get('quotient_ncols')} / {out.get('quotient_rank')}",
        ]
    else:
        lines.append(f"source rank:           {out.get('source_rank')}")
    lines += [
        f"kernel_dim:            {out.get('kernel_dim')}   "
        f"(sauber nur bei ==1; c_ambiguous={out.get('c_ambiguous')})",
        f"eval_rN (Z1'):         {out.get('eval_rN_signed')}  (nonzero={out.get('eval_rN_nonzero')})",
        f"eval_h7e0 (Z2'):       {out.get('eval_h7e0_signed')}",
        f"c:                     {out.get('c_signed')}   (mod q: {out.get('c')})",
        "```",
        "",
        "## Spalten-Mapping",
        "",
        f"- Verwendet: **{out.get('column_mapping_used', {}).get('layout')}** "
        f"({out.get('column_mapping_used', {}).get('note')})",
        f"- h7e0_Fan = {out.get('column_mapping_used', {}).get('h7e0_fan')}",
    ]
    alt = out.get("alt_layout_shift1")
    if alt:
        lines.append(f"- Kontroll-Layout (Spalte c+1): eval_h7e0={alt.get('eval_h7e0_signed')}, "
                     f"c={alt.get('c_signed')} (erwartet NICHT 400 bei N=109).")
    lines.append("")
    if out.get("kernel_source"):
        ks = out["kernel_source"]
        lines += ["## Kernel-Quelle", "",
                  f"- geladen aus: `{ks.get('loaded_from')}` "
                  f"(quotient_kernel_dim={ks.get('quotient_kernel_dim')}, "
                  f"quotient_ncols={ks.get('quotient_ncols')})",
                  f"- free-column-Ausrichtung stimmt: {out.get('free_columns_match_kernel_json')}"]
        if sc:
            lines.append(f"- repair_pairing-Selbstcheck: computed={sc.get('computed_mod_q')} "
                         f"vs. artefakt={sc.get('kernel_json_mod_q')} -> match={sc.get('match')}")
        lines.append("")
    if "source_annihilated" in out:
        _mode = out.get("annihilation_check_mode", "full")
        _checked = out.get("source_rows_checked")
        _checked_txt = f", geprueft={_checked}" if _checked is not None else ""
        lines += [f"- source_annihilated (Hecke-Zeilen verschwinden auf phi): "
                  f"{out.get('source_annihilated')} "
                  f"(nonzero={out.get('source_pairing_nonzero')}; Modus={_mode}{_checked_txt})", ""]
    if ref:
        lines += ["## Referenz-Vergleiche", ""]
        if "ref_eval_rN" in ref:
            lines.append(f"- eval_rN vs. 705-Analogon ({ref['ref_eval_rN']}): "
                         f"match={ref.get('eval_rN_matches_ref')} "
                         f"(Verhaeltnis eval_rN/ref = {ref.get('eval_rN_over_ref')})")
        if "ref_c" in ref:
            lines.append(f"- c vs. gebridgter Wert ({ref['ref_c']}): "
                         f"match={ref.get('c_matches_ref')} "
                         f"-> Bridge-Invarianz der Kopplung = {ref.get('bridge_invariance')}")
        lines.append("")
    lines += [
        "## Verdikt", "",
        f"- gate_clean (kernel_dim==1 & eval_rN!=0): **{v.get('gate_clean')}**",
        f"- c = {v.get('c_signed')} (mod q {v.get('c')})",
    ]
    if v.get("bridge_invariance_vs_c400") is not None:
        lines.append(f"- Bridge-Invarianz gegen gebridgtes c=400: **{v.get('bridge_invariance_vs_c400')}**")
    lines += ["", "Grenzen: Klassen-Ebene, einzelnes q, Instanz-Level; odd-lokale Hebung "
              "und formale CFR-3.4-Bruecke der Fan-Lesart offen.", ""]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="rank_gate_witness")
    p.add_argument("--case-dir", required=True, type=Path)
    p.add_argument("--method", choices=["raw", "quotient", "auto"], default="auto")
    p.add_argument("--kernel-json", type=Path, default=None,
                   help="kernel_quotient-Artefakt mit vorab berechnetem Quotienten-Kern (fast path)")
    p.add_argument("--q", type=int, default=None, help="override q (sonst aus manifest)")
    p.add_argument("--out-json", type=Path, default=None)
    p.add_argument("--out-md", type=Path, default=None)
    p.add_argument("--status-json", type=Path, default=None)
    p.add_argument("--progress-every", type=int, default=2000)
    p.add_argument("--annihilation-sample", type=int, default=0,
                   help="0=Vollcheck; N>0 prueft eine gespreizte Stichprobe von N Hecke-Zeilen")
    p.add_argument("--ref-eval-rN", type=int, default=None, help="Referenz eval_rN (N=109: 705)")
    p.add_argument("--ref-c", type=int, default=None, help="Referenz c (gebridgt N=109: 400)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    manifest = read_manifest(args.case_dir)
    ncols = int(manifest.get("ncols", manifest.get("columns_after_2term")))
    method = args.method
    if method == "auto":
        method = "quotient" if (args.kernel_json is not None or ncols > 4096) else "raw"
    if method == "raw":
        out = run_raw(args.case_dir, args.q, args.status_json, args.progress_every,
                      getattr(args, "ref_eval_rN"), args.ref_c)
    else:
        out = run_quotient(args.case_dir, args.q, args.status_json, args.progress_every,
                           getattr(args, "ref_eval_rN"), args.ref_c, args.kernel_json,
                           args.annihilation_sample)
    if args.out_json:
        args.out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    if args.out_md:
        write_md(out, args.out_md)
    if not args.out_json and not args.out_md:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(out.get("verdict", {}), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
