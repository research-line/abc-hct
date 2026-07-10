#!/usr/bin/env python
# C_E-Luecken-Fueller fuer den Sweep: N=48, 240 (dort warf E.congruence_number()
# den Sage-internen "BUG in modular degree or congruence number"-ValueError).
# Alternativpfad: congruence_number ueber den Newform-Modularsymbol-Faktor
# (ModularSymbols(N,2,sign=1).cuspidal_subspace().new_subspace()-Zerlegung ->
# Faktor mit a_p == a_p(E) -> .congruence_number()). Ziel: odd-Teil von C_E
# bestimmen und pruefen, ob es odd-Kongruenzprimzahlen JENSEITS von deg phi gibt.
from sage.all import *
import json, time
from pathlib import Path

try:
    from cysignals.alarm import alarm, cancel_alarm, AlarmInterrupt
    HAVE_ALARM = True
except Exception:
    HAVE_ALARM = False

CASES = [
    (48,  (0, 1, 0, -24, 36)),
    (240, (0, -1, 0, -5336, 151536)),
]

out = {}
for N, ainvs in CASES:
    t = time.time()
    E = EllipticCurve(list(ainvs))
    assert int(E.conductor()) == N
    dphi = int(E.modular_degree())
    rec = {"N": N, "ainvs": str(E.ainvs()), "modular_degree": dphi,
           "modular_degree_factor": str(factor(dphi))}
    # Methode: Newform-Faktor der neuen kuspidalen Modularsymbole
    try:
        if HAVE_ALARM:
            alarm(300)
        S = ModularSymbols(N, 2, sign=1).cuspidal_subspace()
        Bs = int(floor(2 * Gamma0(N).index() / 12))
        good = [int(p) for p in primes(Bs) if gcd(int(p), N) == 1][:12]
        decomp = list(S.decomposition())
        target = None
        for A in decomp:
            if A.dimension() != 1:
                continue
            ok = True
            for p in good:
                try:
                    ap_factor = A.hecke_operator(p).matrix()[0, 0]
                except Exception:
                    ok = False
                    break
                if int(ap_factor) != int(E.ap(p)):
                    ok = False
                    break
            if ok:
                target = A
                break
        if target is None:
            rec["cn_method"] = "no_dim1_factor_matched"
        else:
            others = [X for X in decomp if X is not target]
            Bc = others[0]
            for X in others[1:]:
                Bc = Bc + X
            C = int(target.congruence_number(Bc))
            rec["congruence_number"] = C
            rec["congruence_number_factor"] = str(factor(C)) if C > 1 else "1"
            rec["odd_primes_CE"] = [int(p) for p, _e in factor(C) if p != 2]
            rec["odd_primes_deg_phi"] = [int(p) for p, _e in factor(dphi) if p != 2]
            rec["extra_odd_primes_beyond_deg_phi"] = sorted(
                set(rec["odd_primes_CE"]) - set(rec["odd_primes_deg_phi"]))
        if HAVE_ALARM:
            cancel_alarm()
    except (AlarmInterrupt, KeyboardInterrupt):
        if HAVE_ALARM:
            cancel_alarm()
        rec["cn_method"] = "timeout"
    except Exception as exc:
        if HAVE_ALARM:
            try:
                cancel_alarm()
            except Exception:
                pass
        rec["cn_method"] = "error:%r" % exc
    rec["seconds"] = float(round(time.time() - t, 2))
    out[str(N)] = rec

Path("_results/cn_gapfill_2026-07-10.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, default=str))
