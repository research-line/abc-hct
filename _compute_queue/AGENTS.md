# Agentenregeln für die abc Compute Queue

Diese Datei gilt für Agenten, die in `_compute_queue/` arbeiten.

## Harte Regel

Starte keine langen Rechenjobs auf dem Laptop oder der lokalen
Codex-Workstation. Lokal erlaubt sind nur Kurzläufe, Smokes und Checks, die
realistisch unter ca. einer Stunde bleiben.

Längere Jobs laufen auf:

- Mac Studio (`lukas@100.119.69.90`),
- Hetzner/Server,
- Desktop-PC, wenn verfügbar.

## Workflow

1. Job als JSON unter `jobs/` anlegen oder aktualisieren.
2. Mit `abc_compute_queue_runner.py --once --dry-run` prüfen.
3. Auf dem Zielhost ausführen, nicht lokal:

   ```bash
   python3 _compute_queue/scripts/abc_compute_queue_runner.py --root . --once
   ```

4. Für dauerhaften Betrieb:

   ```bash
   nohup python3 _compute_queue/scripts/abc_compute_queue_runner.py \
     --root . --loop --interval 300 \
     > _compute_queue/logs/runner.nohup.log 2>&1 &
   ```

## Ergebnisbehandlung

- Fertige JSON/MD-Resultate aus `_results/` lokal sichern.
- Beweisstand in `BEWEISNOTIZ_2.md`, `TODO.md`, `GAPS.md`, `MEMORY.md`
  nachziehen.
- Kuratierte Scripts/Results können ins private GitHub-Repo.
- Interne Notizen, Handoffs und Agentenlogs bleiben aus GitHub draußen.

## Sage

Vor einem Sage-Job:

```bash
bash _compute_queue/scripts/install_sage_backend.sh --check
```

Wenn kein Sage verfügbar ist:

```bash
bash _compute_queue/scripts/install_sage_backend.sh --pull
```

Auf Mac Studio ist wegen ARM64 bevorzugt:

```bash
bash _compute_queue/scripts/install_sage_backend.sh --micromamba
```

Der Docker-Backend-Weg ist ohne sudo nutzbar, benötigt aber ausreichend
Docker-/Colima-Ressourcen und ein passendes Image für die Architektur.
