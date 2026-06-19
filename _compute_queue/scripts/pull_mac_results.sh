#!/bin/bash
# pull_mac_results.sh — Laptop-seitiger Pull der Mac-Beweisartefakte.
#
# ARCHITEKTUR-ENTSCHEID 2026-06-13: Der Mac-OneDrive-Client ist
# unzuverlaessig (Prozess beendet sich selbst; CloudStorage-Schreibungen
# seit 30.05. nie hochgeladen). Die nachweislich stabile Strecke ist
# SSH (Tailscale). Darum zieht der LAPTOP periodisch (Task Scheduler,
# stuendlich) die Artefakte und legt sie in den LAPTOP-OneDrive
# (dessen Upload zuverlaessig laeuft):
#   Mac ~/compute/abc_hct/_results/      -> abc/_results/
#   Mac ~/compute/abc_hct/compute_queue/ -> abc/_compute_queue/
# Nur json/md/npz/log/txt/jsonl/py/sh, < 40 MB. Additiv (kein Loeschen).
# Der Mac-seitige cron-Sync (sync_compute_queue_to_onedrive.sh) bleibt
# als Redundanz bestehen, falls der Mac-OneDrive wieder arbeitet.
set -u
KEY="$HOME/.ssh/id_ed25519_mcmc"
MAC="lukas@100.119.69.90"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ABC="${ABC_OVERRIDE:-$REPO_ROOT}"
LOG="$ABC/_compute_queue_pull.log"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
ts() { date '+%Y-%m-%d %H:%M:%S'; }

ssh -i "$KEY" -o ConnectTimeout=20 -o BatchMode=yes "$MAC" '
  cd ~/compute/abc_hct 2>/dev/null || exit 1
  find _results compute_queue -type f \
    \( -name "*.json" -o -name "*.md" -o -name "*.npz" -o -name "*.log" \
       -o -name "*.txt" -o -name "*.jsonl" -o -name "*.py" -o -name "*.sh" \) \
    -size -40M -not -path "*__pycache__*" -not -path "*_backups*" \
    -exec stat -f "%z %N" {} \;
' > "$TMP/remote.lst" 2>/dev/null
if [ ! -s "$TMP/remote.lst" ]; then
    echo "[$(ts)] SSH/Liste fehlgeschlagen (Mac offline?)" >> "$LOG"
    exit 1
fi

: > "$TMP/want.lst"
while IFS=" " read -r sz path; do
    loc="$ABC/${path/#compute_queue/_compute_queue}"
    if [ ! -f "$loc" ] || [ "$(stat -c %s "$loc" 2>/dev/null)" != "$sz" ]; then
        echo "$path" >> "$TMP/want.lst"
    fi
done < "$TMP/remote.lst"

n=$(wc -l < "$TMP/want.lst" | tr -d " ")
[ "$n" -eq 0 ] && exit 0

if ! ssh -i "$KEY" -o BatchMode=yes "$MAC" "cd ~/compute/abc_hct && tar czf - -T -" \
        < "$TMP/want.lst" > "$TMP/bundle.tgz" 2>/dev/null; then
    echo "[$(ts)] tar-Transfer fehlgeschlagen" >> "$LOG"
    exit 1
fi
mkdir -p "$TMP/x" "$ABC/_results" "$ABC/_compute_queue"
tar xzf "$TMP/bundle.tgz" -C "$TMP/x" 2>/dev/null
[ -d "$TMP/x/_results" ] && cp -r "$TMP/x/_results/." "$ABC/_results/"
[ -d "$TMP/x/compute_queue" ] && cp -r "$TMP/x/compute_queue/." "$ABC/_compute_queue/"
echo "[$(ts)] $n Datei(en) vom Mac geholt" >> "$LOG"
exit 0
