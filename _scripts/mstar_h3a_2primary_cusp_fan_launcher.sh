#!/usr/bin/env bash
# H3a-B 2-primary Cusp-Fan Test Launcher (Schubladenversion).
#
# Status:    READY (stub). Nicht starten, solange 240672/raw laeuft.
# Datum:     2026-05-16
# Protokoll: _proof-notes/MG_h3a_2primary_large_level_protocol_2026-05-16.md
# Lemma:     _proof-notes/MG_h3a_2primary_boundary_budget_lemma_candidate_2026-05-16.md
#
# Zweck:
#   Pro M*-Restlevel (80224, 120336, 240672) einen nativen GF(2)-Cusp-Fan-Test
#   ausfuehren. Wichtig: nicht die mod-3863-Witnesses modulo 2 reduzieren.
#   Stattdessen denselben Manin-Quotienten direkt ueber F_2 aufbauen.
#
# Vorbedingung:
#   - 240672/raw Standard-Witness (PID 94578) ist abgeschlossen.
#     Pruefen via:
#       test -f _results/mstar_h3a_240672_raw_rc3c_standard_2026-05-16.json
#   - Mac-Studio-RAM frei (kein gleichzeitiger 240672/anc-Lauf).
#
# Reihenfolge: klein -> gross (80224 -> 120336 -> 240672).
# Jeder Lauf prueft:
#   1. rank_F2(T5-2 auf Cusp-Fan F_d)
#   2. dim_F2(coker D_5)
#   3. T7(e_0)-Pairing gegen den Rechtskernel
#   4. ob (3) den Defekt sattigt.

set -euo pipefail

readonly REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
readonly DATE_STAMP="$(date +%Y-%m-%d)"
readonly LOG_DIR="${REPO_DIR}/_logs"
readonly RESULT_DIR="${REPO_DIR}/_results"
readonly SCRIPT="${REPO_DIR}/_scripts/mstar_nomagma_sparse_hecke_quotient.py"

mkdir -p "${LOG_DIR}" "${RESULT_DIR}"

# Levels in aufsteigender Reihenfolge (kleinster zuerst).
LEVELS=(80224 120336 240672)
MODE="raw"
PRIMES="5 7 11 13"
Q=2
BATCH_SIZE=1000
# 240672 braucht max-batches >= ceil(d / batch_size) + ein paar.
declare -A MAX_BATCHES=( [80224]=12 [120336]=24 [240672]=48 )

guard_against_running_witness() {
    # Refuse to start if a 240672 standard witness is still computing.
    if pgrep -fa "mstar_nomagma_sparse_hecke_quotient.*240672.*--q 3863" > /dev/null; then
        echo "ABORT: 240672/raw q=3863 witness is still running. Wait for it to finish."
        exit 2
    fi
    if [[ ! -f "${RESULT_DIR}/mstar_h3a_240672_raw_rc3c_standard_${DATE_STAMP}.json" \
       && ! -f "${RESULT_DIR}/mstar_h3a_240672_raw_rc3c_standard_2026-05-16.json" ]]; then
        echo "WARN: 240672/raw q=3863 result file not found. Continue only if intended."
    fi
}

run_one_level() {
    local N="$1"
    local mb="${MAX_BATCHES[$N]}"
    local tag="mstar_h3a_${N}_${MODE}_q2_cusp_fan_${DATE_STAMP}"
    local out_json="${RESULT_DIR}/${tag}.json"
    local out_md="${RESULT_DIR}/${tag}.md"
    local log="${LOG_DIR}/${tag}.log"
    local witness_dir="${RESULT_DIR}/rc3c_q2_witness_${N}_${MODE}_${DATE_STAMP}"

    echo "[$(date)] Starting q=2 native cusp-fan test on ${N}/${MODE}"
    echo "  log:        ${log}"
    echo "  out-json:   ${out_json}"
    echo "  witness:    ${witness_dir}"

    PYTHONIOENCODING=utf-8 nohup python3 "${SCRIPT}" \
        --backend sage \
        --levels "${N}" \
        --modes "${MODE}" \
        --primes ${PRIMES} \
        --q "${Q}" \
        --rank-engine quotient-numpy-dense \
        --hecke-family standard \
        --max-hecke-batches-per-prime "${mb}" \
        --hecke-batch-size "${BATCH_SIZE}" \
        --rc3-source-witness-dir "${witness_dir}" \
        --out-json "${out_json}" \
        --out-md "${out_md}" \
        > "${log}" 2>&1 &
    local pid=$!
    echo "  PID:        ${pid}"
    echo "${pid}" > "${RESULT_DIR}/${tag}.pid"
    # Wait sequentially: small level first, then medium, then large.
    wait "${pid}"
    echo "[$(date)] Finished ${N}/${MODE} (exit ${?})"
}

main() {
    guard_against_running_witness

    for N in "${LEVELS[@]}"; do
        run_one_level "${N}"
        # Decision gate: after each level, inspect the result MD before continuing.
        local md="${RESULT_DIR}/mstar_h3a_${N}_${MODE}_q2_cusp_fan_${DATE_STAMP}.md"
        if [[ -f "${md}" ]]; then
            echo "--- result summary (${N}/${MODE}) ---"
            head -40 "${md}" || true
            echo "--- end summary ---"
        fi
    done

    cat <<EOF

All three q=2 native cusp-fan tests have finished.

Manual follow-up:
  - Compare defect dimensions (target: small, level-independent C).
  - Compare T7(e_0) saturation: if defect is fully killed by the repair row,
    the 2-primary budget lemma's strong form applies.
  - Otherwise: identify which additional boundary/Atkin-Lehner row reduces
    the defect to zero, and check whether the same row works across levels.

Update the lemma file accordingly:
  _proof-notes/MG_h3a_2primary_boundary_budget_lemma_candidate_2026-05-16.md
EOF
}

# Do not auto-execute. Require explicit RUN_NOW=1 to start.
if [[ "${RUN_NOW:-0}" == "1" ]]; then
    main
else
    cat <<EOF
Stub mode. To launch:

  ssh -i ~/.ssh/id_ed25519_mcmc lukas@100.119.69.90 \\
      "cd ~/compute/abc_hct && RUN_NOW=1 bash _scripts/mstar_h3a_2primary_cusp_fan_launcher.sh"

Refusing to run automatically; ensure 240672/raw q=3863 is finished first.
EOF
fi
