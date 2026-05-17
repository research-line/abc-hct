# No-Magma Mac Environment

Date: 2026-05-12

Local script SHA256: `F0AEE89DBA2F0EB8126BBF2523C40EAA9D53C2ED952556FFFD5BDA3AA2137EFB`

```text
REMOTE_DATE=2026-05-12 03:02:26 CEST
HOST=mac-studio
PWD=/Users/lukas/compute/abc_nomagma
SCRIPT_SHA256=f0aee89dba2f0eb8126bbf2523c40eaa9d53c2ed952556fffd5bda3aa2137efb
AUDIT_TARGET=240672_anc_live
PROCESS_BEGIN
19310 01-05:19:37   0.0  0.0   1888 ./micromamba-bin/bin/micromamba run -p ./sage-env python _scripts/mstar_nomagma_sparse_hecke_quotient.py --backend sage --levels 240672 --modes anc --primes 5 7 11 13 --q 3863 --hecke-family standard --rank-engine quotient-numpy-dense --pivot-strategy max --hecke-batch-size 1000 --max-hecke-batches-per-prime 48 --progress --out-json _results/mstar_nomagma_sparse_hecke_quotient_240672_anc_T5cap48_fullprimes_numpy_mac_2026-05-10.json
19313 01-05:19:37 100.0 22.1 7399232 python _scripts/mstar_nomagma_sparse_hecke_quotient.py --backend sage --levels 240672 --modes anc --primes 5 7 11 13 --q 3863 --hecke-family standard --rank-engine quotient-numpy-dense --pivot-strategy max --hecke-batch-size 1000 --max-hecke-batches-per-prime 48 --progress --out-json _results/mstar_nomagma_sparse_hecke_quotient_240672_anc_T5cap48_fullprimes_numpy_mac_2026-05-10.json
PROCESS_END
PY_ENV_BEGIN
python=3.14.4 | packaged by conda-forge | (main, Apr  8 2026, 02:33:53) [Clang 20.1.8 ]
platform=macOS-26.4.1-arm64-arm-64bit-Mach-O
numpy=2.4.3
sage=10.8
PY_ENV_END
```
