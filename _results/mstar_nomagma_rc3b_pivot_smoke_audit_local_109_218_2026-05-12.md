# RC3b Pivot Audit

Date: 2026-05-12

| Level | Mode | Sign | ncols | Pivots | Checks | Manifest |
|---:|---|---:|---:|---:|---|---|
| 109 | raw | 1 | 27 | 27 | ok | `manifest.json` |
| 109 | anc | 1 | 27 | 27 | ok | `manifest.json` |
| 218 | raw | 1 | 83 | 83 | ok | `manifest.json` |
| 218 | anc | 1 | 83 | 83 | ok | `manifest.json` |

## Scope

This audit verifies a full sparse pivot basis exported by the Python ranker. It proves full rank for the exported basis, but does not yet independently derive that basis from the Manin/Hecke row transcript.
