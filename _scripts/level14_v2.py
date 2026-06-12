import os
os.environ["PATH"] = "/Users/lukas/mamba/envs/sage/bin:" + os.environ.get("PATH", "")

from sage.all import GF
from sage.modular.modsym.manin_symbol_list import ManinSymbolList_gamma0
from sage.modular.modsym.relation_matrix import modI_relations, modS_relations, sparse_2term_quotient
from sage.modular.modsym.heilbronn import HeilbronnCremona, HeilbronnMerel
from sage.modular.modsym.modsym import ModularSymbols as MS
import numpy as np

import sys
N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
q = 3863
F = GF(q)

# === SAGE CANONICAL ===
M_sage = MS(N, 2, sign=1)
S_sage = M_sage.cuspidal_submodule()
dim_sage = M_sage.dimension()
print(f"=== SAGE CANONICAL (Level {N}) ===")
print(f"dim M = {dim_sage}, dim S = {S_sage.dimension()}")
print(f"basis = {M_sage.basis()}")

test_primes = [p for p in [2, 3, 5, 7, 11, 13] if p <= N + 6]
for p in test_primes:
    Tp = M_sage.hecke_matrix(p)
    tag = "p|N" if N % p == 0 else "gcd=1"
    print(f"\nSage T_{p} ({tag}):")
    for i in range(Tp.nrows()):
        print(f"  {[int(Tp[i,j]) for j in range(Tp.ncols())]}")

if S_sage.dimension() > 0:
    D = S_sage.decomposition()
    for fi, f in enumerate(D):
        test_primes = [p for p in [2, 3, 5, 7, 11, 13] if p <= N + 6]
for p in test_primes:
            print(f"  a_{p} = {f.eigenvalue(p)}")

# === CUSTOM SOLVER ===
syms = ManinSymbolList_gamma0(N, 2)
nsyms = len(syms)

rels_set = set(modS_relations(syms))
rels_set.update(modI_relations(syms, 1))
mod = sparse_2term_quotient(rels_set, nsyms, F)

rep_to_col = {}
mod_map_list = []
for entry in mod:
    rep, scalar = entry
    if scalar == 0:
        mod_map_list.append(None)
        continue
    rep_i = int(rep)
    if rep_i not in rep_to_col:
        rep_to_col[rep_i] = len(rep_to_col)
    mod_map_list.append((rep_to_col[rep_i], F(scalar)))

ncols = len(rep_to_col)
col_to_rep = {v: k for k, v in rep_to_col.items()}
print(f"\n=== CUSTOM SOLVER (Level {N}) ===")
print(f"nsyms={nsyms}, ncols(S+I)={ncols}")

# Sage coordinate map for each symbol
sage_coords_map = {}
for i in range(nsyms):
    c, d = syms[i].u, syms[i].v
    elt = M_sage.manin_symbol((0, c, d))
    sage_coords_map[i] = [int(x) for x in elt.element()]

# Find which symbols are sage basis elements (coords = unit vector)
sage_basis_sym_idx = {}
for k in range(dim_sage):
    e_k = [0] * dim_sage
    e_k[k] = 1
    for i in range(nsyms):
        if sage_coords_map[i] == e_k:
            sage_basis_sym_idx[k] = i
            c, d = syms[i].u, syms[i].v
            print(f"  Sage basis[{k}] = sym[{i}]=({c},{d})")
            break
    if k not in sage_basis_sym_idx:
        print(f"  WARNING: Sage basis[{k}] is NOT a single Manin symbol!")

if len(sage_basis_sym_idx) != dim_sage:
    print("ABORT: Cannot identify all sage basis elements as single symbols")
    import sys; sys.exit(1)

# === HECKE COMPARISON ===
print(f"\n=== HECKE: standard vs cremona vs Sage ===")
test_primes = [p for p in [2, 3, 5, 7, 11, 13] if p <= N + 6]
for p in test_primes:
    tag = "p|N" if N % p == 0 else "gcd=1"
    Tp_sage = M_sage.hecke_matrix(p)
    sage_hecke = np.array([[int(Tp_sage[i,j]) % q for j in range(dim_sage)]
                           for i in range(dim_sage)], dtype=np.int64)

    for family_name in ["standard", "cremona"]:
        if family_name == "standard":
            mats = [[1, a, 0, p] for a in range(p)] + [[p, 0, 0, 1]]
        else:
            mats = HeilbronnCremona(p).to_list()

        H = np.zeros((dim_sage, dim_sage), dtype=np.int64)
        for k in range(dim_sage):
            si = sage_basis_sym_idx[k]
            img = [0] * dim_sage
            for A in mats:
                for idx, coeff in syms.apply(si, A):
                    sc = sage_coords_map[idx]
                    for j in range(dim_sage):
                        img[j] = (img[j] + int(F(coeff)) * sc[j]) % q
            H[k] = img

        match = bool(np.all((H - sage_hecke) % q == 0))
        print(f"  T_{p} ({tag}), {family_name}: match={match}")
        if not match:
            print(f"    custom:  {H.tolist()}")
            print(f"    sage:    {sage_hecke.tolist()}")
            diff = (H - sage_hecke) % q
            print(f"    diff:    {diff.tolist()}")

print("\nDONE")
