# Q^r-Layer-Sizing Readiness Ledger (2026-06-06)

## Kurzbefund

- Kein abc-, PCAT-, FAQS- oder canonical-level-Upgrade.
- Kein Langlauf gestartet; dieser Check liest nur vorhandene Artefakte.
- Gesamtstatus: `preflight_ready_but_compute_blocked`.
- Nächster sinnvoller Schritt: 240672/Cremona-Fortschritt holen oder abschließen, danach PSC-Zertifikate q=2,3,5,31 mit echten Row-/Kernel-Bindungen instanziieren.

## Externer Paperstand

| Quelle | Einordnung |
|---|---|
| [Cuevas Barrientos--Pasten, arXiv:2504.15971v3](https://arxiv.org/abs/2504.15971) | Subexponentieller Szpiro-in-Familien-Kontext; kein Frey-uniformes Polynomial-Closing. |
| [Chan, arXiv:2407.13850](https://arxiv.org/abs/2407.13850) | Fast-alle-Szpiro-Ratio; bestätigt Statistik-gegen-Worst-Case-Barriere. |
| [Sawin--Sutherland, arXiv:2504.12295v2](https://arxiv.org/abs/2504.12295) | Murmurations-Dichte als Mittelwert-/Evidenzkontext, nicht als individueller Frey-Hebel. |
| [Dumas--Kaltofen--Thomé, arXiv:1507.01083](https://arxiv.org/abs/1507.01083) | Passender Zertifikatsrahmen für Wiedemann/Krylov; härtet Verifikation, nicht HCT-Transfer. |
| [Pasten, arXiv:1705.09251v4](https://arxiv.org/abs/1705.09251) | Shimura-/abc-Kontext; keine neue Perioden-/Modulgrad-Schließung für diese Route. |
| [Iyengar--Khare--Manning, arXiv:2510.05418v2](https://arxiv.org/abs/2510.05418) | Kongruenzideal-Sprache aktuell; für HCT bleibt uniforme Frey-Schranke das offene Gate. |
| [Khan--Maithani, arXiv:2604.06446](https://arxiv.org/abs/2604.06446) | Determinantaler Wiles-Defekt ist Reformulierungskontext, kein unabhängiger abc-Beweis. |

## Artefakt-Readiness

| Fall | Gate | Status | Nächste Aktion |
|---|---|---|---|
| `80224/raw` | QB3 Wiedemann identity-pairing fingerprint | `available_certificate_fingerprint` | Nur als Zertifikatshärtungs-Kalibrator nutzen; das ist nicht der q-Layer-Sizing-Lauf. |
| `240672/raw` | Cremona Hecke separator for current Frey class | `local_output_missing_or_remote_running` | 240672/Cremona-Ausgabe holen oder fertigstellen, bevor sie als qdim=1-Input genutzt wird. |
| `60168/raw q=2` | PSC-2 two-dimensional source-cokernel repair | `pairing_available_template_not_certificate` | Row-Hashes, Kernelbasis und Source-Block-Hash binden, um das PSC-2-Zertifikat zu instanziieren. |
| `60168/raw q=3` | PSC-1 one-row source-cokernel repair | `pairing_available_template_not_certificate` | q=3-Kernelvektor und Repair-Rowhash binden, bevor certificate-level behauptet wird. |
| `60168/raw q=5` | PSC-1 one-row repair candidate | `template_only_missing_real_export` | Echten q=5-Kernel-/Pairing-Witness exportieren; nicht aus q=2/q=3 folgern. |
| `60168/raw q=31` | PSC-1 one-row repair candidate | `template_only_missing_real_export` | Echten q=31-Kernel-/Pairing-Witness exportieren; getrennt von q=5 führen. |
| `LM-60168` | Local drainage manifest for q in {2,3,5,31} | `manifest_template_not_certificate` | Keine Labels hochstufen, bevor alle vier PSC-Einträge real und verifiziert sind. |
| `60168/raw transfer` | Canonical local drainage transfer | `blocked_by_false_transfer_inputs` | Embedding und Spaltenbasis-Kompatibilität klären, bevor canonical- oder PCAT-Sprache verwendet wird. |
| `60168/raw witness base` | Source witness availability | `available_source_witness` | Als Bindungsziel für PSC-Row-/Kernel-Provenienz verwenden. |
| `240672/raw legacy witness` | Old standard-family witness | `legacy_standard_witness_not_current_cremona_gate` | Nicht ohne explizites Replay/Übersetzung als 2026-06-05-Cremona-Gate wiederverwenden. |

## Blocker

- 240672/raw Cremona-Hecke output is not locally available as a completed gate.
- PSC certificates for q in {2,3,5,31} remain templates until row/kernel/source bindings are real.
- Canonical local drainage transfer labels remain false, so PCAT/FAQS/abc language is not licensed.

## Maschinenlesbare Details

- JSON: `_results/Q_LAYER_SIZING_READINESS_LEDGER_2026-06-06.json`
- CSV: `_results/Q_LAYER_SIZING_READINESS_LEDGER_2026-06-06.csv`
- Dieser Markdownbericht: `_results/Q_LAYER_SIZING_READINESS_LEDGER_2026-06-06.md`
