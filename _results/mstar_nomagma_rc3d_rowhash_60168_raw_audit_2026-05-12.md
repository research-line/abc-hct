# RC3c Source-Row Witness Audit

Date: 2026-05-12

| Level | Mode | Sign | ncols | Source rows | Recomputed rank | Method | Bound rows | Checks | Manifest |
|---:|---|---:|---:|---:|---:|---|---:|---|---|
| 60168 | raw | 1 | 31680 | 31680 | 31680 | sage-matrix | 31680 | ok | `manifest.json` |

## Scope

This audit recomputes the rank of exported original source rows over GF(3863). It proves full rank for those rows and keeps row IDs for binding to the transcript layer. When `--transcript-root` is supplied, it also checks the per-row transcript hash index.
