# abc Mac Compute Queue

Stand: 2026-05-23

Diese Queue ist die dauerhafte Rechenpipeline für lange abc/HCT-Läufe. Sie
verhindert, dass schwere Sage-/Python-Jobs versehentlich auf dem Laptop
laufen, und startet neue Jobs auf dem Mac Studio erst, wenn definierte
Blocker-Prozesse beendet sind.

## Ziel

- Lange Berechnungen laufen auf Mac Studio, Server oder Desktop-PC.
- Lokale Kurzläufe bleiben erlaubt, solange sie realistisch unter einer
  Stunde bleiben.
- Jobs sind als JSON in `jobs/` beschrieben und dadurch für alle Agenten
  lesbar.
- Der Runner startet höchstens einen Queue-Job gleichzeitig.
- Die Heartbeat-Automation prüft Mac-Status, holt fertige Ergebnisse ab und
  darf den Runner anstoßen.

## Ordner

```text
_compute_queue/
  README.md                 diese Betriebsanleitung
  AGENTS.md                 Regeln für GPT/Codex und andere Agenten
  CLAUDE.md                 Regeln für Claude
  jobs/                     deklarative Job-Dateien
  scripts/                  Runner, Sage-Backend-Checks, Install-Helfer
  state/                    Laufzustand pro Job
  logs/                     Runner- und Job-Logs
```

## Compute-Policy

| Host | Verwendung |
|---|---|
| Laptop / lokale Codex-Workstation | Nur Smoke-/Kurzläufe unter ca. 1 h |
| Mac Studio | Primärer 24/7-Compute-Host |
| Hetzner `ellmos-services` | Leichte Fallback-/Kalibrierläufe; nur 2 vCPU / 8 GB |
| Desktop-PC | Erlaubter Zielhost für lange Jobs, wenn verfügbar |

Wichtig: lange Jobs nie lokal auf dem Laptop starten. Wenn ein Job länger als
eine Stunde dauern kann, muss er als Queue-Job auf einem Remote-Host laufen.

## Start auf dem Mac Studio

Vom Mac-Projektordner aus:

```bash
cd /Users/lukas/compute/abc_hct
python3 _compute_queue/scripts/abc_compute_queue_runner.py --root . --once
```

Als dauerhafter Poller:

```bash
cd /Users/lukas/compute/abc_hct
nohup python3 _compute_queue/scripts/abc_compute_queue_runner.py \
  --root . --loop --interval 300 \
  > _compute_queue/logs/runner.nohup.log 2>&1 &
```

Der Runner startet nur, wenn:

- der aktuelle Host in `allowed_hosts` des Jobs steht,
- keine `defer_while_process_regex`-Blocker laufen,
- ein Sage-Backend verfügbar ist,
- die erwarteten Output-Dateien noch nicht erfolgreich vorhanden sind.

## Sage-Backend

Der Runner sucht zuerst ein natives `sage`, dann bekannte Micromamba-Pfade wie
`~/mamba/envs/sage/bin/sage`. Falls keines vorhanden ist und der Job Docker
erlaubt, nutzt er:

```bash
docker run --rm -e HOME=/tmp -v "$PWD:/work" -w /work sagemath/sagemath:latest sage
```

Backend-Check:

```bash
bash _compute_queue/scripts/install_sage_backend.sh --check
```

Docker-Sage vorbereiten:

```bash
bash _compute_queue/scripts/install_sage_backend.sh --pull
```

Auf dem Mac ist Docker/Colima vorhanden, aber das Standard-Image
`sagemath/sagemath:latest` hat kein `linux/arm64`-Manifest. Mac-Sage wird
deshalb nativ über Micromamba installiert:

```bash
bash _compute_queue/scripts/install_sage_backend.sh --micromamba
```

Auf Hetzner ist Docker-Sage verfügbar (`SageMath 10.8`), aber der Server hat
nur 2 vCPU / 8 GB RAM und ist daher eher Kalibrier- oder Fallback-Host.

## Aktuelle Queue

1. `qb3_wiedemann_80224_raw_2026-05-23.json`
   - Q_B-3 Source-Gram-Rank für `80224/raw`.
   - **Pausiert seit Loop 350.**
   - Grund: die aktuelle Produktionsroute baut `ModularSymbols(..., sign=0)`
     plus `plus_submodule()`/`build_bal_factors` und landet bei `80224` in
     einer rationalen IML-Nullspace-Rechnung mit sehr großem Peak-Speicher.
   - Wieder aktivieren nur nach `sign=1`-/finite-field-Refactor oder nach
     expliziter Entscheidung für einen Host mit mindestens 64 GB RAM.
2. `qb3_wiedemann_80224_anc_2026-05-23.json`
   - gleiche Zertifizierung für `80224/anc`.
   - **Pausiert aus demselben Grund**; anc darf nicht automatisch dieselbe
     teure `sign=0`-Route wiederholen.

Der manuell gestartete Mac-Lauf
`mstar_h3a_qb3_wiedemann_production_remod_q5077_80224_raw_mac_2026-05-24`
darf weiterlaufen. Die Pausierung betrifft nur neue Queue-Starts.

## Heartbeat

Die Automation `abc-mac-job-monitor` soll nicht nur die alten H3a-Prozesse
prüfen, sondern auch:

- Sage-Backend auf Mac/Server prüfen,
- Queue-Runner-Status lesen,
- nach Abschluss der H3a-Blocker den nächsten Queue-Job anstoßen,
- fertige Resultate ins lokale Projekt holen,
- `BEWEISNOTIZ_2.md`, `TODO.md`, `GAPS.md`, `MEMORY.md` aktualisieren.

## GitHub

Ins private Repo gehören nur kuratierte Scripts und reproduzierbare Results.
Nicht ins Repo gehören diese internen Steuerdateien, sofern sie
beweisnotiznah oder agentisch sind:

- `BEWEISNOTIZ*`
- `GAPS.md`
- `TODO.md`
- `MEMORY.md`
- `_proof-notes/`
- `_handoffs/`
- Agentenlogs

Die Compute-Queue selbst darf ins private Repo, wenn sie keine Secrets und
keine internen Beweisnotizen enthält.
