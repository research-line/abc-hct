#!/bin/bash
# sync_compute_queue_to_onedrive.sh  (v2, 2026-06-13)
#
# Spiegelt Beweismaterial der Mac-Compute-Infrastruktur additiv nach
# OneDrive (unidirektional Mac -> OneDrive, KEIN --delete):
#   1. compute_queue/  -> abc/_compute_queue/   (jetzt INKL. logs/ + state/)
#   2. _results/       -> abc/_results/         (json/md/npz/log, max 40M;
#      Ergebnisse sind write-once, Namen datumseindeutig)
#
# Betrieb: CRON (alle 30 min) statt LaunchAgent — LaunchAgents duerfen
# auf macOS nicht in ~/Library/CloudStorage schreiben (TCC); der alte
# Agent com.lukas.computequeue-onedrive-sync lief deshalb still leer
# (letzte Aenderung 2026-05-30). BACH nutzt aus demselben Grund cron.
set -u
OD="$HOME/Library/CloudStorage/OneDrive-Persönlich/.TOPICS/.RESEARCH/.LAB/.HCT/abc"
LOG="$HOME/Library/Logs/compute_queue_sync.log"
ts() { date "+%Y-%m-%d %H:%M:%S"; }

run_rsync() {
    local label="$1"; shift
    local out
    out=$(rsync -a --itemize-changes "$@" 2>&1)
    local rc=$?
    if [ -n "$out" ]; then
        echo "[$(ts)] $label rc=$rc:" >> "$LOG"
        echo "$out" >> "$LOG"
    fi
    return $rc
}

[ -d "$HOME/compute/abc_hct" ] || { echo "[$(ts)] FEHLER: Quelle fehlt" >> "$LOG"; exit 1; }
mkdir -p "$OD/_compute_queue" "$OD/_results"

run_rsync "queue" --exclude "__pycache__/" \
    "$HOME/compute/abc_hct/compute_queue/" "$OD/_compute_queue/"
run_rsync "results" --max-size=40M \
    --include "*/" --include "*.json" --include "*.md" --include "*.npz" \
    --include "*.log" --include "*.txt" --include "*.jsonl" --exclude "*" \
    "$HOME/compute/abc_hct/_results/" "$OD/_results/"
exit 0
