# Compute-Queue Runner & Memory-Watchdog -- Mechanik

Stand: 2026-05-30

Diese Datei dokumentiert die *Innenmechanik* von
`scripts/compute_queue_runner.py` und seiner Kopplung an den
`memory_pressure_watchdog.sh`. Betrieb/Policy stehen in `README.md`,
Prioritäten und Status-Konventionen in `PRIORITIES.md`.

## 1. Was der Runner tut

- Lädt alle Job-JSONs aus `jobs/*.json`, sortiert nach `priority`
  (kleinere Zahl = höhere Priorität).
- Prüft pro Lauf jeden Job mit `job_eligible(...)` und **startet höchstens
  einen** eligible Job (`launch_job`), danach endet die Runde.
- Modi: `--once` (eine Runde), `--loop --interval N` (Dauerbetrieb, Default
  300 s), `--dry-run` (entscheidet + schreibt State, startet aber keinen
  Prozess).
- Schreibt pro Lauf `state/runner_status.json` (`action` + `decisions`).

## 2. Eligibility -- Reihenfolge der Prüfungen (`job_eligible`)

Ein Job ist nur startbar, wenn er ALLE Prüfungen in dieser Reihenfolge
passiert:

1. **Status-Gate** -- `status in {paused, blocked, disabled, completed, done,
   failed}` -> Job wird übersprungen (terminal bzw. Hold). Siehe Abschnitt 4.
2. **Host** -- aktueller Host muss in `allowed_hosts` sein und darf nicht in
   `disallowed_hosts` stehen (Aliase: mac-studio, ellmos-services, ASUS-GEI).
3. **Output-Erfolg** (`output_success`) -- wenn `expected_outputs` existieren
   UND `success_json` erfüllt ist -> Job gilt als fertig: State -> `success`,
   **Auto-Completion** des Job-JSON -> `completed` (seit 2026-05-30), Job
   übersprungen ("already successful").
4. **Eigener Lauf-State** -- State `running` und PID lebt -> "already running".
5. **Ein-Job-Regel** -- läuft bereits ein Queue-Job, ist ein *zusätzlicher* nur
   erlaubt, wenn der Watchdog einen Slot signalisiert (`pull_ok`, Abschnitt 5).
6. **Abhängigkeiten** -- `depends_on_success`: jede genannte Job-ID muss State
   `success` haben.
7. **Defer-Blocker** -- `defer_while_process_regex`: läuft ein passender
   Prozess (z. B. ein manueller Wiedemann-Lauf), wird der Job zurückgestellt.
8. **Ressourcen** -- `resource_policy.min_free_mem_gb` / `max_load_1min`.
9. **Sage-Backend** -- natives `sage` / micromamba-Env / Docker-Image vorhanden.

## 3. Erfolgskriterium (`output_success`)

```text
expected_outputs : Liste relativer Pfade -- alle müssen existieren
success_json     : { "path": ..., "field": "<dotted.key>", "equals": <wert> }
```

Beide werden geprüft. Fehlt eine Output-Datei oder weicht das Feld ab, gilt der
Job als *nicht* erfolgreich -- und könnte ohne Status-Gate neu starten. Deshalb:
abgebrochene/erledigte Jobs immer über `status` terminieren (Abschnitt 4), nicht
allein auf Output-Reste verlassen.

## 4. Status-Lebenszyklus

| Status | Bedeutung | Runner-Verhalten |
|---|---|---|
| `queued` | startbereit | wird geprüft/gestartet |
| `running` | wird ausgeführt | "already running", solange PID lebt |
| `completed` / `done` | fertig | **übersprungen (terminal)** |
| `failed` | mit Fehler abgebrochen | **übersprungen (terminal)** |
| `blocked` | Hold (Bug/Refactor/extern oder erledigt-via-Parallellauf) | übersprungen, reaktivierbar |
| `paused` | vom Memory-Watchdog pausiert | übersprungen, Resume durch Watchdog |
| `disabled` | dauerhaft aus | übersprungen |

- **Auto-Completion (2026-05-30):** Sobald `output_success` erfüllt ist, setzt
  der Runner das Job-JSON selbst auf `completed` (+ `completed_unix`,
  `completed_reason`). *Davor* kannte der Runner nur `paused/blocked/disabled`
  als Skip; ein manuell gesetztes `completed` wurde ignoriert und der Job über
  `success_json` neu bewertet -> Neustart-Gefahr, wenn die Output-Dateien
  fehlten. Dieser Fix (Skip-Menge um `completed/done/failed` erweitert +
  Auto-Completion) schließt die Lücke.
- **Reaktivieren:** `status` zurück auf `queued`.

## 5. Kopplung an den Memory-Watchdog (Slot-Modell)

`memory_pressure_watchdog.sh` (Detail-Doku im Skript-Header) schützt
Compute-Jobs vor macOS-Jetsam-OOM: bei Speicherdruck eskaliert er (Ollama
entladen -> Compute-Jobs `SIGSTOP`/pausieren -> zuletzt Hintergrund-Services
killen) und resumed beim Entlasten in umgekehrter Reihenfolge.

Runner und Watchdog teilen sich `~/.memwatchdog/`:

```text
compute_slot_status.json   Watchdog -> Runner: {ts, pull_ok, overflow_locked}
runner_jobs/<job>.pid      Runner   -> Watchdog: gestartete Jobs, damit der
                           Watchdog sie in count_active_compute mitzählt
```

- Der Runner liest `compute_slot_status.json` (`read_slot_status`); ist er
  älter als 90 s, gilt "kein Slot" (Race-Schutz bei totem/hängendem Watchdog).
- Läuft schon ein Queue-Job, startet der Runner einen **zusätzlichen** nur bei
  `pull_ok=true` (höchstens 1 Extra "in flight" -- User-Slot-Modell).
- Es gibt **keinen** oberen RAM-Guard im Runner. Drückt ein Job das System in
  Level 4, fängt der Watchdog das ab (pausiert + `overflow_locked`).
  `resource_policy` ist nur die Per-Job-*Untergrenze* beim Start.

Ergänzende Referenzen: `memory_pressure_watchdog.sh`-Header (Config,
Escalation), LaunchAgents `com.lukas.memwatchdog` / `com.lukas.computequeue`,
sowie (laptopseitig) `.SYNC/laptop/COMPUTE_SLOT_MANAGEMENT_2026-05-28.md`.

## 6. Job-JSON -- Kernfelder

```jsonc
{
  "id": "...",                          // eindeutig
  "status": "queued",                   // s. Abschnitt 4
  "priority": 15,                       // s. PRIORITIES.md
  "allowed_hosts": ["mac-studio"],
  "disallowed_hosts": ["ASUS-GEI"],
  "depends_on_success": ["..."],        // optional
  "defer_while_process_regex": ["..."], // beide Wiedemann-Skriptvarianten matchen
  "resource_policy": {"min_free_mem_gb": 12.0, "max_load_1min": 8.0},
  "backend": {"type": "sage", "allow_docker": true, "docker_image": "..."},
  "command": "{sage} _scripts/....sage ...",   // {sage} wird ersetzt
  "expected_outputs": ["_results/....json", "_results/....md"],
  "success_json": {"path": "_results/....json", "field": "accepted_certificate_found", "equals": true}
}
```

## 7. Betrieb: nach Code-Änderung den Daemon neustarten

Der produktive Runner läuft als LaunchAgent `com.lukas.computequeue` im
Dauermodus (`--loop`). Ein `--loop`-Prozess importiert
`compute_queue_runner.py` **nur einmal beim Start** und ruft danach in einer
Schleife `run_once()` auf. Eine Bearbeitung der `.py`-Datei wirkt daher **erst
nach Neustart** des Daemons -- der laufende Prozess nutzt bis dahin den alten
Bytecode im Speicher (Tests mit `--once`/`--dry-run` re-importieren die Datei
und täuschen sonst „live" vor).

Neu laden (respektiert KeepAlive, kein `unload`/`load` nötig):

```bash
launchctl kickstart -k "gui/$(id -u)/com.lukas.computequeue"
```

Detached gestartete Compute-Jobs (`start_new_session=True`) **überleben** den
Runner-Neustart. Danach prüfen: neuer Runner-PID (kurze `etime`) und frischer
`state/runner_status.json`.

## 8. Synchronisation lokal <-> OneDrive

Die aktive Queue lebt in `~/compute/abc_hct/compute_queue/` (flüchtig). Die
dauerhafte Sicherung ist OneDrive `_compute_queue/`. Damit Änderungen nicht
manuell nachgezogen werden müssen (häufigste Fehlerquelle: vergessenes Sync),
läuft die Spiegelung scriptgesteuert **und** automatisiert:

- **Skript:** `scripts/sync_compute_queue_to_onedrive.sh` -- additives `rsync`
  lokal -> OneDrive, schliesst `state/`, `logs/`, `__pycache__/` aus, **kein**
  `--delete` (nur-in-OneDrive-Dateien bleiben erhalten). Idempotent; loggt nur
  bei Änderungen nach `~/Library/Logs/compute_queue_sync.log`.
- **Automatik:** LaunchAgent `com.lukas.computequeue-onedrive-sync`
  (`~/Library/LaunchAgents/`), `StartInterval` 1800 s + `RunAtLoad`.
- **Manuell anstossen:** `bash compute_queue/scripts/sync_compute_queue_to_onedrive.sh`
- **Deaktivieren:** `launchctl bootout gui/$(id -u)/com.lukas.computequeue-onedrive-sync`

Die Richtung ist bewusst unidirektional (lokal = Master). Wer die OneDrive-Kopie
direkt ändert, muss damit rechnen, dass die nächste Sync sie überschreibt.

## 9. Audit-Transcript (faithful-execution-Vorbereitung)

Seit 2026-05-30 schreibt `_scripts/mstar_h3a_qb3_wiedemann_production_finite_pairing.sage`
zusätzliche Audit-Daten ins Ergebnis-JSON, die eine spätere *unabhängige*
Nachprüfung (Community oder eigenes Folge-Paper) erleichtern:

- **`component_hashes`** (opt-in via `--emit-component-hashes`, default aus -- W.dict() ist auf grossen Levels speicher-unsicher): SHA-256 von `C_source`, `free_to_sage`,
  `B_AL` (W/E/P) → Reproduzierbarkeit / Anti-Drift.
- **`matvec_checkpoints`** (bei `--checkpoint-stride N` > 0): alle N Schritte
  ein SHA-256 des Iterats `x_k` plus `s_k` → erlaubt einem unabhängigen Replay,
  Divergenz früh zu erkennen, ohne 2n Matvecs am Stück nachzurechnen.
- **`transcript_scope`**: ehrliches Scope-Label im JSON.

In allen `qb3_wiedemann_*`-Job-Definitionen via `--checkpoint-stride 1000` aktiviert.

**Wichtige Grenze:** Diese Daten attestieren **Reproduzierbarkeit**, nicht die
**Korrektheit** der Operator-Konstruktion — ein Skript, das ein Transcript über
sich selbst schreibt, kann seine eigene Korrektheit nicht beweisen. Der echte
faithful-execution-Schluss braucht eine **unabhängige** B_AL-Implementierung
(Atkin-Lehner) plus Matvec-Replay; das ist bewusst auf nach dem Hauptprojekt
verschoben (eigenes Paper). Stand 2026-05-30: Tier 1 (Sequenz unabhängig
re-verifiziert) + Tier 2 (Input-Hashes verifiziert) erledigt, Tier 3 offen.

## Auto-Done, Exit-Codes & Rerun-Schutz (Patch 2026-06-13)

Anlass: Zwei Vorfälle. (1) 2026-06-12: Runner hielt fertige Jobs mit
`<defunct>`-PIDs (Zombies) für „running" und blockierte die Queue 3,5 h.
(2) 2026-06-13: Nach sauberem Ende eines 16,5-h-Jobs (Exit 0, Ergebnis
geschrieben) startete der Runner den Job NEU, weil die Job-Datei noch
auf `queued` stand und kein Erfolgskriterium deklariert war.

Drei Abschluss-Mechanismen (in dieser Reihenfolge wirksam):

1. **`expected_outputs` / `success_json`** (Job-JSON, bestand schon):
   Der Runner prüft bei jeder Eligibility, ob die deklarierten
   Output-Dateien existieren bzw. das JSON-Feld den Sollwert hat →
   State `success`, Job-Datei `completed`. **Konvention: Jeder neue Job
   SOLL `success_json` deklarieren** (z. B. `{"path": "_results/X.json",
   "field": "status", "equals": "done"}`).

2. **Exit-Code-Reaping (NEU):** `reap_children()` ruft pro Loop
   `waitpid(-1, WNOHANG)` auf und verbucht beendete Kinder:
   - Exit 0 → State `success` + Job-Datei `completed` (Auto-Done)
   - Exit > 0 → State + Job-Datei `failed` (kein Auto-Retry-Brennen)
   - Signal (kill/OOM) → State `killed`, Job-Datei bleibt `queued`
     (transient ⟹ Neustart durch Runner erlaubt)
   Beseitigt zugleich die Zombie-Entstehung. Greift nur für Kinder des
   AKTUELLEN Daemons (nach `launchctl kickstart` sind Altjobs von
   launchd adoptiert → Mechanismus 1 oder 3 greift).

3. **`finished_unverified` (NEU, ersetzt blinden Rerun):** State
   `running` + PID weg + kein Exit-Code bekannt → State wird
   `finished_unverified`, Job wird NICHT neu gestartet. Manuell:
   Ergebnisse prüfen, dann Job-Datei auf `done` setzen ODER State-Datei
   löschen + Job `queued` für echten Rerun.

Zombie-Erkennung: `pid_alive()` prüft jetzt zusätzlich den ps-State
(`Z` = tot). Backup des Vorzustands:
`_backups/compute_queue_runner_2026-06-13_pre_autodone.py`.
