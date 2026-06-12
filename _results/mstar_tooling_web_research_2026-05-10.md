# M*: Tooling-Web-Recherche und lokale Backend-Proben

Datum: 2026-05-10

## Web/GitHub

Recherchierte Toolfamilien:

- SageMath ModularSymbols / Hecke module API / GitHub-Quelle;
- Magma ModularSymbols / ModularForms;
- PARI/GP Modular Forms;
- Sage NumericalEigenforms als heuristischer Separationshelfer.

## Lokale API-Probe

`_scripts/mstar_sage_optimization_probe.py`:

- 5 Probes, 5 OK, 0 Timeout.
- `ModularSymbols(..., base_ring=GF(3863))` funktioniert auf Level 11 und
  109 schnell.
- Atkin-Lehner-Methoden sind API-seitig vorhanden.

## Backend-Tests

### Sage `modsym_gf`

Smoke:

- Level 109, raw, \(T_5,T_7\): ok.
- \(\det(T_5-a_5I)=841\pmod{3863}\) auf dem sign-0 ModularSymbols-Newspace;
  voller Rang, Kernel 0.

Restlevel:

- Level 60168, raw/ANC, nur \(T_5\), Backend `modsym_gf`, Timeout 120s.
- Beide Worker timeout.

### PARI/GP

Verfügbar in der Sage-Micromamba-Umgebung:

```text
/root/micromamba/envs/sage/bin/gp
```

Smoke:

```gp
mf = mfinit([109,2],0);
M = mfheckemat(mf,5);
matsize(M) = [8,8]
```

Restlevel:

```gp
mf = mfinit([60168,2],0);
```

scheitert mit PARI stack overflow bereits bei 8 MB und auch bei 1 GB Stack.

### Magma

`magma` ist lokal nicht im PATH. Web-Dokumentation spricht stark dafür, dass
Magma ein guter Alternativpfad wäre, aber lokal ist es derzeit nicht
ausführbar.

## Schluss

Sage-ModularSymbols über \(\mathbb F_{3863}\) ist API-seitig real, aber
`60168` bleibt ohne weitere Zerlegung zu schwer. PARI/GP ist vorhanden, aber
für `60168` nicht out-of-the-box brauchbar. Magma wäre wahrscheinlich der
beste externe Vergleich, ist lokal aber nicht installiert.
