# M*: Magma-Alternativen-Probe

Datum: 2026-05-10

## Kurzfazit

Sage-Brandt ist lokal real und läuft auf den Smoke-Levels 109 und 218. Für das erste harte Restlevel 60168 timeoutet die prime-ramified Brandt-Konstruktion im Kurzlauf; die mathematisch passendere multi-ramified Präsentation wird von Sage derzeit nicht implementiert.

## Ergebnisse

| Fall | Level | Status | Dimension | Hecke-Befund |
|---|---:|---|---:|---|
| `smoke_109` | 109 | ok | 9 | T5,T7,T11,T13 |
| `smoke_218` | 218 | ok | 27 | T5,T7,T11,T13 |
| `rest_60168_prime_ramified_109` | 60168 | timeout |  | Timeout nach 60s |
| `rest_60168_multiramified_ideal` | 60168 | error |  | NotImplementedError: Brandt modules currently only implemented when N is a prime |

## Konsequenz

Die beste Magma-Alternative ist nicht PARI/GP oder OSCAR, sondern Sage-Brandt plus zusätzliche Splitting-/Quotientenarbeit. Als direkter Ersatz für Wiese/Kilford-local-Hecke-Algebras reicht sie lokal noch nicht: Sage kann multi-ramified Brandt-Module nicht, und die prime-ramified Darstellung ist für 60168 zu schwer im Kurzlauf.

Nächster sinnvoller Nicht-Magma-Schritt: Sage-Brandt nicht verwerfen, sondern einen kleineren Quotientenpfad bauen: zuerst nur Konstruktion und Dimension/Ideal-Klassen cachen, dann Heckeoperatoren faktorweise und mit längeren Läufen auf Mac Studio oder einer größeren Linux-VM.
