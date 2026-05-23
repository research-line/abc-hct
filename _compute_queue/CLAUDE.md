# Claude-Regeln für die abc Compute Queue

Diese Compute-Queue ist die dauerhafte Mac-/Server-Rechenpipeline für
abc/HCT.

## Grundregel

Keine langen Jobs auf dem Laptop. Lokale Kurzläufe sind erlaubt, wenn sie
realistisch unter ca. einer Stunde bleiben. Alles darüber gehört auf Mac
Studio, Server oder Desktop-PC.

## Vor jedem Start

1. `README.md` und `AGENTS.md` lesen.
2. Job-JSON in `jobs/` prüfen.
3. Aktuelle Remote-Prozesse prüfen:

   ```bash
   ps -axo pid,pcpu,rss,etime,command | egrep 'mstar_h3a|qb3|sage|python'
   ```

4. Sage-Backend prüfen:

   ```bash
   bash _compute_queue/scripts/install_sage_backend.sh --check
   ```

   Auf Mac Studio bei fehlendem Sage:

   ```bash
   bash _compute_queue/scripts/install_sage_backend.sh --micromamba
   ```

## Startregel

Den Runner auf dem Zielhost starten:

```bash
python3 _compute_queue/scripts/abc_compute_queue_runner.py --root . --once
```

Nicht den Produktions-Sage-Befehl direkt von der lokalen Workstation starten.

## Dokumentation

Nach jedem neuen Ergebnis:

- Resultate lokal holen.
- `BEWEISNOTIZ_2.md`, `TODO.md`, `GAPS.md`, `MEMORY.md` aktualisieren.
- Kuratierte Scripts/Results ins private Repo spiegeln, aber keine internen
  Beweisnotizen oder Handoffs.
