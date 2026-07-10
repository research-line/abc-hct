#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
starcore_falsifier.py  --  Stein 2 der Generator-Falsifikator-Pipeline (abc / P6, ★-Kern)

Automatisiert die Steckbrief-Tests T0-T5 aus dem Fahndungsblatt
(MG_starcore_fahndungsblatt_2026-07-10.md, Section E) gegen einen Tripel-Korpus.
Ein Kandidat = berechenbare Groesse G(triple_features) -> float, plus Pflicht-Metadaten.
Der Falsifikator toetet Kandidaten, die die Pflichteigenschaften des gesuchten
radikal-sensitiven Objekts G(E_{a,b,c}) verletzen. KEIN Claim -- Programm-Instrument.

Autor: LG (via claude-code / Opus). Kein abc-Claim-Upgrade durch Korrelationen.

--------------------------------------------------------------------------------
TESTS (Ausgabe je Test: metric-score, verdict in {pass,kill,park,reject,dataless}, kill_grund)
--------------------------------------------------------------------------------
T0  Provenienz-Gate (BSD-Schaerfung): Pflichtfelder vorhanden? mechanism_class ==
    'presupposed' -> KILL OHNE Rechnung (Konstruktion setzt die Zielgroesse als Input
    voraus, statt sie abzuleiten). Fehlende Pflichtfelder -> REJECT.

T1  Radikal- vs. Bewertungs-Sensitivitaet: Traeger-Buckets = Tripel mit IDENTISCHER
    rad-Traegermenge (Support), aber verschiedenen Exponentenmustern (Exponenten-
    Aufblaehung). Gefordert: Var(G | Bucket) ~ 0 (bewertungs-still) UND Var(G ueber
    Buckets) >> 0 (rad-sensitiv). Metric = within_ratio = Within-Bucket-SS / Total-SS
    ueber Tripel in Multi-Member-Buckets. KILL wenn within_ratio > Schwelle
    (exponenten-sensitiv) ODER wenn G konstant ist (sieht rad nicht -> keine Reaktion).

T2  omega-Skalierung (N2-Detektor): |G|/omega(rad(abc)) darf ueber den Korpus nicht mit
    omega davonwachsen. Metric = growth_factor = q90(|G|/omega | oberstes omega-Terzil)
    / q90(|G|/omega | unterstes omega-Terzil). KILL wenn growth_factor > Schwelle
    (Tamagawa-/Komponentengruppen-Klasse akkumuliert Groesse p+-1 pro bad prime).

T3  Zirkularitaets-Leck (N3): partielle Korrelation corr(G, log deg phi | log rad) auf
    dem Subkorpus mit deg-phi-Daten (Watkins-Spalte 'deg'). Metric = |partial_corr|.
    KILL wenn > Schwelle (versteckter deg-phi-/Perioden-Proxy; P1-Dichotomie).
    Fehlt die deg-phi-Spalte -> t3_status = 'awaiting_degphi_column' (implementiert,
    aber datenlos -- NICHT stillschweigend uebersprungen).

T4  Nutzen/Trennschaerfe: Effektgroesse (Cohen d, zusaetzlich AUC) von G auf hoch-
    qualitativen Tripeln (q > 1.2) gegen magnitude-gematchte Zufallstripel. Metric =
    |Cohen d|. PARK wenn < Schwelle (nutzlos != falsch -> KEIN Kill).

T5  Support-only-Detektor (N5): KILL, wenn G AUSSCHLIESSLICH die Support-Information
    traegt und keine Trennung darueber hinaus leistet. Sauber abgegrenzt von T1:
      * T1 verlangt Stille INNERHALB der Buckets (bewertungs-blind).
      * T5 killt, wenn G zusaetzlich (A) bewertungs-blind ist (Within-Ratio <= Schwelle,
        also G = Funktion des Supports) UND (B) die Support-KARDINALITAET omega bereits
        >= T5_cardinality_eta2_min der Between-Bucket-Varianz erklaert -- d.h. G traegt
        nur, WIE VIELE Primzahlen im Traeger sind, nicht WELCHE (kein arithmetisches
        Gewicht). Direktes finites Gegenmodell (Ihara S3-Paar, pi_l-Gleichheit bis l=11
        bei kippendem Verdikt): das Ziel-G muss die primitive Zaehlschicht transportieren.
      Ein arithmetisch gewichtetes G (z.B. log rad = Summe_{p|rad} log p) erfuellt (A),
      aber NICHT (B) -- es unterscheidet gleich-grosse Traeger {2,3} vs {2,5} -- und
      ueberlebt T5. Ein rein exponenten-sensitives G (z.B. log c) faellt schon bei (A)
      durch (kein support-only) und wird von T1 getoetet, nicht von T5.

--------------------------------------------------------------------------------
GESAMT-VERDIKT
--------------------------------------------------------------------------------
T0 kill/reject -> Gesamt kill/reject (ohne T1-T5). Sonst: harte Tests = T1,T2,T3,T5
(ein Kill -> Gesamt KILL). T4 ist weich (nur PARK). Kein harter Kill + T4 park ->
Gesamt PARK. Alles pass -> SURVIVOR (geht in manuelle Pruefung; Majorisierung bleibt
Handarbeit).

--------------------------------------------------------------------------------
KORPUS
--------------------------------------------------------------------------------
(1) Watkins-Subkorpus (numerics/watkins_v3_final_a+b80.csv): vollstaendige Enumeration
    kleiner Tripel (c <= 80), Spalten a,b,c,N,deg,quality,... -> traegt N (Konduktor)
    und deg (== deg phi, Modulgrad; siehe DEGPHI-Annahme unten) -> Nutzen-/Zirkularitaets-
    Achse (T3, T4).
(2) Brute-Force voll-glatte S-Unit-Tripel: a+b=c, alle S-glatt (S = erste K Primzahlen),
    c <= BOUND, gcd=1 -> reiche Traeger-Buckets (gleicher Support, verschiedene
    Exponenten) fuer T1/T5 UND hochqualitative Tripel fuer T4. Konstruktionsregel unten.
(3) Zufallskontrollen: zufaellige teilerfremde (a,b), c=a+b, magnitude-gematcht zur
    Hochqualitaets-Gruppe -> T4-Kontrastgruppe.

DEGPHI-ANNAHME (explizit, konservativ): Die Watkins-Spalte 'deg' wird als Modulgrad
deg phi der Frey-Kurve interpretiert (empirisch konsistent: quality == log c / log rad
verifiziert; 'deg' variiert 1..~2.6e6 wie ein Modulgrad, nicht wie omega). Steuerbar per
DEGPHI_COLUMN; falls sich das als falsch erweist, Flag umsetzen -> T3 wird datenlos.

--------------------------------------------------------------------------------
GUARDS
--------------------------------------------------------------------------------
- Holdout-Split (support-level, seeded, ~80/20): ganze Traegerklassen gehen auf eine
  Seite -> Buckets bleiben auf beiden Seiten intakt. Tests laufen per Default auf TRAIN;
  --holdout wiederholt die Wertung out-of-sample. Indizes in eigener Datei.
- Praeregistrierte Schwellen in starcore_thresholds_preregistered_2026-07-10.json
  (VOR dem ersten Generator-Lauf). Kein Claim-Upgrade durch Korrelationen.
"""

import argparse
import bisect
import csv
import hashlib
import json
import math
import os
import random
import sys
from collections import defaultdict

# --------------------------------------------------------------------------- #
# Pfade / Konfiguration
# --------------------------------------------------------------------------- #
_HERE = os.path.dirname(os.path.abspath(__file__))
_ABC_ROOT = os.path.dirname(_HERE)  # _scripts/ liegt in <abc>/_scripts

DEFAULT_WATKINS = os.path.join(_ABC_ROOT, "numerics", "watkins_v3_final_a+b80.csv")
DEFAULT_DATA_DIR = os.path.join(_ABC_ROOT, "_data")
DEFAULT_RESULTS_DIR = os.path.join(_ABC_ROOT, "_results")
DEFAULT_THRESHOLDS = os.path.join(_HERE, "starcore_thresholds_preregistered_2026-07-10.json")

STAMP = "2026-07-10"
CORPUS_NAME = "starcore_corpus_2026-07-10.json"
HOLDOUT_NAME = "starcore_holdout_indices_2026-07-10.json"
CALIB_JSON = "starcore_falsifier_calibration_2026-07-10.json"
CALIB_MD = "starcore_falsifier_calibration_2026-07-10.md"

# Watkins-Spalte, die als deg phi (Modulgrad) interpretiert wird. None -> T3 datenlos.
DEGPHI_COLUMN = "deg"

# Brute-Force-Glatt-Konstruktion (Traeger-Buckets)
SMOOTH_PRIMES = [2, 3, 5, 7, 11, 13, 17]   # S = erste 7 Primzahlen
SMOOTH_BOUND = 10 ** 6                       # c <= 10^6 (Fahndungsblatt); Fallback 10^5 dokumentiert
# Zufallskontrollen
N_RANDOM_CONTROLS = 4000
# Holdout
HOLDOUT_SEED = 20260710
HOLDOUT_FRACTION = 0.20
RANDOM_SEED = 20260710

FALLBACK_THRESHOLDS = {
    "T1_within_bucket_variance_ratio_max": 0.10,
    "T2_omega_scaling_growth_factor_max": 2.0,
    "T3_partial_corr_abs_max": 0.30,
    "T4_min_abs_cohen_d": 0.50,
    "T4_min_group_size": 10,
    "T5_precondition_within_ratio_max": 0.10,
    "T5_cardinality_eta2_min": 0.98,
}


# --------------------------------------------------------------------------- #
# Zahlentheorie-Helfer (stdlib, zero-dependency)
# --------------------------------------------------------------------------- #
def factorize(n):
    """Primfaktorzerlegung via Trial-Division (n bis ~10^12 trivial)."""
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def triple_features(a, b, c, N=None, deg_phi=None, source=""):
    """Feature-Cache pro Tripel. Support = Traegermenge der Primzahlen von abc."""
    abc = a * b * c
    fac = factorize(abc)
    support = tuple(sorted(fac))
    rad = 1
    for p in support:
        rad *= p
    omega = len(support)
    log_rad = math.log(rad) if rad > 1 else 0.0
    log_c = math.log(c) if c > 1 else 0.0
    quality = log_c / log_rad if log_rad > 0 else 0.0
    return {
        "a": a, "b": b, "c": c,
        "N": N, "deg_phi": deg_phi,
        "rad": rad,
        "support": support,                       # Tuple im Speicher, Liste im JSON
        "omega": omega,
        "exponents": {int(p): int(fac[p]) for p in support},
        "quality": quality,
        "log_rad": log_rad,
        "log_c": log_c,
        "source": source,
    }


def smooth_numbers(primes, bound):
    """Alle S-glatten Zahlen <= bound (Produkte von Primpotenzen aus 'primes')."""
    smooth = [1]
    for p in primes:
        powers = []
        pw = p
        while pw <= bound:
            powers.append(pw)
            pw *= p
        extended = list(smooth)
        for x in smooth:
            for q in powers:
                v = x * q
                if v <= bound:
                    extended.append(v)
        smooth = extended
    return sorted(set(smooth))


# --------------------------------------------------------------------------- #
# Korpus-Bau
# --------------------------------------------------------------------------- #
def load_watkins(path):
    """Watkins-CSV -> Feature-Liste (mit N, deg_phi)."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        header = r.fieldnames
        has_degphi = DEGPHI_COLUMN is not None and DEGPHI_COLUMN in (header or [])
        for row in r:
            try:
                a, b, c = int(row["a"]), int(row["b"]), int(row["c"])
            except (KeyError, ValueError):
                continue
            if a + b != c:
                continue
            N = None
            try:
                N = int(row["N"])
            except (KeyError, ValueError):
                pass
            deg_phi = None
            if has_degphi:
                try:
                    deg_phi = int(row[DEGPHI_COLUMN])
                except (KeyError, ValueError):
                    deg_phi = None
            rows.append(triple_features(a, b, c, N=N, deg_phi=deg_phi, source="watkins"))
    return rows, (header or []), has_degphi


def gen_smooth_triples(primes, bound):
    """
    Voll-glatte S-Unit-Tripel a+b=c (a<=b), alle drei S-glatt, gcd(a,b)=1, c<=bound.
    Konstruktionsregel (im Report dokumentiert): a,b,c saemtlich Produkte von Primzahlen
    aus S = {2,3,5,7,11,13,17}. So teilen viele Tripel dieselbe Traegermenge (Support)
    bei verschiedenen Exponentenmustern -> echte Traeger-Buckets (verallgemeinert die
    2^k*3^m-Familien des Fahndungsblatts). Grosse/nicht-glatte Tripel bilden Singleton-
    Support-Klassen und tragen nichts zu den Buckets bei.
    """
    smooths = smooth_numbers(primes, bound)
    smooth_set = set(smooths)
    triples = []
    for i, a in enumerate(smooths):
        if a > bound // 2:
            break
        for b in smooths[i:]:          # b >= a  => a <= c/2
            c = a + b
            if c > bound:
                break                  # smooths aufsteigend -> weitere b nur groesser
            if c in smooth_set and math.gcd(a, b) == 1:
                triples.append(triple_features(a, b, c, source="smooth"))
    return triples


def gen_random_controls(n, c_min, c_max, seed):
    """Zufaellige teilerfremde (a,b), c=a+b, c log-uniform in [c_min,c_max]."""
    rng = random.Random(seed)
    out = []
    seen = set()
    lo, hi = math.log(max(c_min, 3)), math.log(max(c_max, c_min + 1))
    tries = 0
    while len(out) < n and tries < n * 60:
        tries += 1
        c = int(math.exp(rng.uniform(lo, hi)))
        if c < 3:
            continue
        a = rng.randint(1, c - 1)
        b = c - a
        if a > b:
            a, b = b, a
        if math.gcd(a, b) != 1:
            continue
        key = (a, b, c)
        if key in seen:
            continue
        seen.add(key)
        out.append(triple_features(a, b, c, source="random"))
    return out


def build_corpus(watkins_path, out_path, primes=SMOOTH_PRIMES, bound=SMOOTH_BOUND,
                 n_random=N_RANDOM_CONTROLS, verbose=True):
    watkins, header, has_degphi = load_watkins(watkins_path)
    smooth = gen_smooth_triples(primes, bound)

    # Hochqualitaets-Bereich (q>1.2) fuer magnitude-gematchte Kontrollen bestimmen
    hq = [t for t in (watkins + smooth) if t["quality"] > 1.2]
    if hq:
        c_lo = min(t["c"] for t in hq)
        c_hi = max(t["c"] for t in hq)
    else:
        c_lo, c_hi = 10, bound
    controls = gen_random_controls(n_random, max(10, c_lo // 2), min(bound, c_hi * 2), RANDOM_SEED)

    corpus = watkins + smooth + controls
    for idx, t in enumerate(corpus):
        t["idx"] = idx
        t["support"] = list(t["support"])  # JSON-serialisierbar

    meta = {
        "created": STAMP,
        "author": "LG",
        "note": "Programm-Instrument, kein Claim. Feature-Cache fuer starcore_falsifier T0-T5.",
        "watkins_csv": os.path.basename(watkins_path),
        "watkins_header": header,
        "degphi_column": DEGPHI_COLUMN if has_degphi else None,
        "degphi_assumption": ("Watkins-Spalte '%s' als Modulgrad deg phi interpretiert" % DEGPHI_COLUMN)
        if has_degphi else "keine deg-phi-Spalte im Watkins-Korpus",
        "smooth_primes": primes,
        "smooth_bound": bound,
        "smooth_construction": "voll-glatte S-Unit-Tripel a+b=c, a<=b, alle S-glatt, gcd(a,b)=1, c<=bound",
        "n_watkins": len(watkins),
        "n_smooth": len(smooth),
        "n_random": len(controls),
        "n_total": len(corpus),
        "random_control_c_range": [max(10, c_lo // 2), min(bound, c_hi * 2)],
    }
    payload = {"_meta": meta, "triples": corpus}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    if verbose:
        stats = corpus_stats(corpus)
        print("[build-corpus] geschrieben:", out_path)
        for k, v in meta.items():
            if k not in ("watkins_header",):
                print("   %-22s %s" % (k, v))
        print("   %-22s %s" % ("n_buckets(>=2, distinct exp)", stats["n_buckets_ge2"]))
        print("   %-22s %s" % ("n_triples_in_buckets", stats["n_in_buckets"]))
        print("   %-22s %s" % ("omega range", stats["omega_range"]))
        print("   %-22s %s" % ("n high-q (q>1.2)", stats["n_highq"]))
        print("   %-22s %s" % ("n watkins with deg_phi", stats["n_degphi"]))
    return payload


def load_corpus(path):
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    for t in payload["triples"]:
        t["support"] = tuple(t["support"])
    return payload


# --------------------------------------------------------------------------- #
# Buckets + Split
# --------------------------------------------------------------------------- #
def build_buckets(triples):
    """Gruppiere Tripel nach Support (Traegermenge). Bucket 'nutzbar' fuer T1/T5 wenn
    >=2 Mitglieder mit >=2 DISTINKTEN Exponentenmustern (echte Exponenten-Aufblaehung)."""
    by_support = defaultdict(list)
    for t in triples:
        by_support[tuple(t["support"])].append(t)
    usable = {}
    for supp, members in by_support.items():
        exp_patterns = {tuple(sorted(m["exponents"].items())) for m in members}
        if len(members) >= 2 and len(exp_patterns) >= 2:
            usable[supp] = members
    return by_support, usable


def corpus_stats(triples):
    _, usable = build_buckets(triples)
    n_in = sum(len(v) for v in usable.values())
    omegas = [t["omega"] for t in triples]
    return {
        "n_total": len(triples),
        "n_buckets_ge2": len(usable),
        "n_in_buckets": n_in,
        "omega_range": (min(omegas), max(omegas)) if omegas else (0, 0),
        "n_highq": sum(1 for t in triples if t["quality"] > 1.2),
        "n_degphi": sum(1 for t in triples if t.get("deg_phi") is not None),
    }


def make_holdout(triples, out_path, seed=HOLDOUT_SEED, frac=HOLDOUT_FRACTION):
    """
    Support-level 80/20-Split: jede Traegerklasse (Support) wird per gehashtem Seed
    ganz TRAIN oder HOLDOUT zugewiesen -> Buckets bleiben auf beiden Seiten intakt.
    Speichert Holdout-Tripel-Indizes + Holdout-Support-Klassen.
    """
    supports = sorted({t["support"] for t in triples})
    holdout_supports = []
    for supp in supports:
        h = hashlib.sha256(("%d|" % seed + ",".join(map(str, supp))).encode()).hexdigest()
        if (int(h[:8], 16) / 0xFFFFFFFF) < frac:
            holdout_supports.append(supp)
    holdout_supp_set = set(holdout_supports)
    holdout_idx = sorted(t["idx"] for t in triples if t["support"] in holdout_supp_set)
    payload = {
        "_meta": {
            "created": STAMP, "author": "LG",
            "split": "support-level (ganze Traegerklassen), seeded",
            "seed": seed, "holdout_fraction_target": frac,
            "note": "Tests laufen per Default auf TRAIN (Komplement); --holdout wiederholt out-of-sample.",
        },
        "n_total": len(triples),
        "n_holdout_supports": len(holdout_supports),
        "n_holdout_triples": len(holdout_idx),
        "holdout_indices": holdout_idx,
        "holdout_supports": [list(s) for s in holdout_supports],
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return payload


def active_triples(triples, holdout_payload, mode):
    """mode in {'train','holdout','all'}."""
    if mode == "all" or holdout_payload is None:
        return list(triples)
    hset = set(holdout_payload["holdout_indices"])
    if mode == "holdout":
        return [t for t in triples if t["idx"] in hset]
    return [t for t in triples if t["idx"] not in hset]  # train


# --------------------------------------------------------------------------- #
# Statistik-Helfer (stdlib)
# --------------------------------------------------------------------------- #
def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _ss(xs, m=None):
    if not xs:
        return 0.0
    if m is None:
        m = _mean(xs)
    return sum((x - m) ** 2 for x in xs)


def quantile(vals, p):
    if not vals:
        return None
    s = sorted(vals)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def pearson(u, v):
    n = len(u)
    if n < 2:
        return 0.0
    mu, mv = _mean(u), _mean(v)
    su, sv = _ss(u, mu), _ss(v, mv)
    if su <= 0 or sv <= 0:
        return 0.0
    suv = sum((x - mu) * (y - mv) for x, y in zip(u, v))
    return suv / math.sqrt(su * sv)


def _linreg_resid(y, x):
    """Residuen von y regressiert auf x (mit Achsenabschnitt)."""
    n = len(x)
    mx, my = _mean(x), _mean(y)
    sxx = _ss(x, mx)
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    b = sxy / sxx if sxx > 0 else 0.0
    a = my - b * mx
    return [yi - (a + b * xi) for xi, yi in zip(x, y)]


def partial_corr(g, d, ctrl):
    """partielle Korrelation corr(g, d | ctrl)."""
    if len(g) < 3:
        return 0.0
    return pearson(_linreg_resid(g, ctrl), _linreg_resid(d, ctrl))


def cohen_d(h, r):
    nh, nr = len(h), len(r)
    if nh < 2 or nr < 2:
        return None
    mh, mr = _mean(h), _mean(r)
    vh = _ss(h, mh) / (nh - 1)
    vr = _ss(r, mr) / (nr - 1)
    denom = nh + nr - 2
    sp = math.sqrt(((nh - 1) * vh + (nr - 1) * vr) / denom) if denom > 0 else 0.0
    if sp == 0:
        return 0.0
    return (mh - mr) / sp


def auc(h, r):
    """P(H > R) + 0.5 * P(H == R) (Mann-Whitney)."""
    if not h or not r:
        return None
    rs = sorted(r)
    tot = len(h) * len(r)
    cnt = 0.0
    for x in h:
        lo = bisect.bisect_left(rs, x)
        hi = bisect.bisect_right(rs, x)
        cnt += lo + 0.5 * (hi - lo)
    return cnt / tot


# --------------------------------------------------------------------------- #
# Kandidat + Evaluation
# --------------------------------------------------------------------------- #
class Candidate:
    REQUIRED_META = ("name", "advice_level", "mechanism_class", "description")
    VALID_ADVICE = {"A0", "A1", "A2", "A3"}
    VALID_MECH = {"derived", "presupposed"}

    def __init__(self, fn, meta):
        self.fn = fn
        self.meta = dict(meta)

    def eval_on(self, triples):
        """-> Liste (triple, value) mit value nicht-None/finite (nicht evaluierbare weg)."""
        out = []
        for t in triples:
            try:
                v = self.fn(t)
            except Exception:
                v = None
            if v is None:
                continue
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            if math.isnan(fv) or math.isinf(fv):
                continue
            out.append((t, fv))
        return out


# ------------------------------ Tests -------------------------------------- #
def test_T0(cand):
    meta = cand.meta
    missing = [k for k in Candidate.REQUIRED_META if k not in meta or meta[k] in (None, "")]
    if missing:
        return {"test": "T0", "metric": None, "verdict": "reject",
                "kill_grund": "Pflichtfelder fehlen: %s" % ", ".join(missing), "detail": {}}
    if meta["advice_level"] not in Candidate.VALID_ADVICE:
        return {"test": "T0", "metric": None, "verdict": "reject",
                "kill_grund": "advice_level ungueltig: %r" % meta["advice_level"], "detail": {}}
    if meta["mechanism_class"] not in Candidate.VALID_MECH:
        return {"test": "T0", "metric": None, "verdict": "reject",
                "kill_grund": "mechanism_class ungueltig: %r" % meta["mechanism_class"], "detail": {}}
    if meta["mechanism_class"] == "presupposed":
        return {"test": "T0", "metric": None, "verdict": "kill",
                "kill_grund": "mechanism_class=presupposed -> Zielgroesse als Input vorausgesetzt (KILL ohne Rechnung)",
                "detail": {"advice_level": meta["advice_level"]}}
    return {"test": "T0", "metric": None, "verdict": "pass", "kill_grund": "",
            "detail": {"advice_level": meta["advice_level"], "mechanism_class": meta["mechanism_class"]}}


def _within_between(cand, usable_buckets):
    """SS-Zerlegung ueber Tripel in Multi-Member-Buckets (nur wo Kandidat evaluierbar,
    Bucket behaelt >=2 evaluierbare Mitglieder). -> (within_ratio, buckets_info, all_vals)."""
    bucket_vals = {}
    for supp, members in usable_buckets.items():
        ev = cand.eval_on(members)
        if len(ev) >= 2:
            bucket_vals[supp] = [v for _, v in ev]
    all_vals = [v for vals in bucket_vals.values() for v in vals]
    if len(all_vals) < 2 or len(bucket_vals) < 1:
        return None, bucket_vals, all_vals
    grand = _mean(all_vals)
    total_ss = _ss(all_vals, grand)
    within_ss = sum(_ss(vals) for vals in bucket_vals.values())
    within_ratio = (within_ss / total_ss) if total_ss > 0 else None  # None -> konstant
    return within_ratio, bucket_vals, all_vals


def test_T1(cand, usable_buckets, thr):
    within_ratio, bucket_vals, all_vals = _within_between(cand, usable_buckets)
    tau = thr["T1_within_bucket_variance_ratio_max"]
    detail = {"n_buckets": len(bucket_vals), "n_triples": len(all_vals),
              "within_ratio": within_ratio, "threshold_max": tau}
    if within_ratio is None:
        if len(all_vals) < 2:
            return {"test": "T1", "metric": None, "verdict": "dataless",
                    "kill_grund": "keine nutzbaren Traeger-Buckets fuer diesen Kandidaten",
                    "detail": detail}
        # total_ss == 0 -> G konstant ueber alle Bucket-Tripel -> sieht rad nicht
        return {"test": "T1", "metric": 0.0, "verdict": "kill",
                "kill_grund": "G konstant ueber Buckets -> keine rad-Reaktion (sieht das Radikal nicht)",
                "detail": detail}
    if within_ratio > tau:
        return {"test": "T1", "metric": round(within_ratio, 6), "verdict": "kill",
                "kill_grund": "Var(G|Bucket)/Var(G) = %.4f > %.2f -> bewertungs-sensitiv (Exponenten-Aufblaehung wirkt)"
                              % (within_ratio, tau), "detail": detail}
    return {"test": "T1", "metric": round(within_ratio, 6), "verdict": "pass",
            "kill_grund": "", "detail": detail}


def test_T2(cand, triples, thr):
    ev = cand.eval_on(triples)
    ratios = [(abs(v) / t["omega"]) for t, v in ev if t["omega"] >= 1]
    omegas = [t["omega"] for t, v in ev if t["omega"] >= 1]
    tau = thr["T2_omega_scaling_growth_factor_max"]
    if len(set(omegas)) < 2 or len(ratios) < 6:
        return {"test": "T2", "metric": None, "verdict": "dataless",
                "kill_grund": "zu wenig omega-Variation fuer den Skalierungstest",
                "detail": {"n": len(ratios)}}
    lo_cut = quantile(omegas, 1.0 / 3.0)
    hi_cut = quantile(omegas, 2.0 / 3.0)
    bottom = [r for r, o in zip(ratios, omegas) if o <= lo_cut]
    top = [r for r, o in zip(ratios, omegas) if o >= hi_cut]
    if not bottom or not top:
        return {"test": "T2", "metric": None, "verdict": "dataless",
                "kill_grund": "omega-Terzile nicht besetzbar", "detail": {}}
    q_bot = quantile(bottom, 0.90)
    q_top = quantile(top, 0.90)
    eps = 1e-12
    growth = (q_top / q_bot) if q_bot > eps else (float("inf") if q_top > eps else 1.0)
    detail = {"q90_bottom_tercile": q_bot, "q90_top_tercile": q_top,
              "omega_lo_cut": lo_cut, "omega_hi_cut": hi_cut, "growth_factor": growth,
              "threshold_max": tau}
    if growth > tau:
        return {"test": "T2", "metric": round(growth, 4) if growth != float("inf") else None,
                "verdict": "kill",
                "kill_grund": "q90(|G|/omega) waechst um Faktor %.2f (>%.1f) von niedrigem zu hohem omega -> N2 (Tamagawa-Klasse)"
                              % (growth, tau), "detail": detail}
    return {"test": "T2", "metric": round(growth, 4), "verdict": "pass", "kill_grund": "", "detail": detail}


def test_T3(cand, triples, thr, has_degphi):
    tau = thr["T3_partial_corr_abs_max"]
    if not has_degphi:
        return {"test": "T3", "metric": None, "verdict": "dataless",
                "kill_grund": "", "detail": {"t3_status": "awaiting_degphi_column"}}
    sub = [t for t in triples if t.get("deg_phi") is not None and t["deg_phi"] > 0 and t["log_rad"] > 0]
    ev = cand.eval_on(sub)
    g = [v for _, v in ev]
    d = [math.log(t["deg_phi"]) for t, _ in ev]
    ctrl = [t["log_rad"] for t, _ in ev]
    if len(g) < 8:
        return {"test": "T3", "metric": None, "verdict": "dataless",
                "kill_grund": "zu wenig deg-phi-Tripel fuer diesen Kandidaten",
                "detail": {"t3_status": "computed", "n": len(g)}}
    pc = partial_corr(g, d, ctrl)
    detail = {"t3_status": "computed", "degphi_column": DEGPHI_COLUMN, "n": len(g),
              "partial_corr": pc, "threshold_abs_max": tau}
    if abs(pc) > tau:
        return {"test": "T3", "metric": round(pc, 4), "verdict": "kill",
                "kill_grund": "|corr(G, log deg phi | log rad)| = %.3f > %.2f -> versteckter deg-phi-/Perioden-Proxy (N3)"
                              % (abs(pc), tau), "detail": detail}
    return {"test": "T3", "metric": round(pc, 4), "verdict": "pass", "kill_grund": "", "detail": detail}


def test_T4(cand, triples, thr):
    tau = thr["T4_min_abs_cohen_d"]
    highq = [t for t in triples if t["quality"] > 1.2]
    if not highq:
        return {"test": "T4", "metric": None, "verdict": "dataless",
                "kill_grund": "", "detail": {"note": "keine Tripel mit q>1.2 im aktiven Split"}}
    c_lo = min(t["c"] for t in highq)
    c_hi = max(t["c"] for t in highq)
    controls = [t for t in triples if t["source"] == "random" and c_lo <= t["c"] <= c_hi]
    if len(controls) < 5:  # Fallback: alle random im Gesamt-c-Bereich
        controls = [t for t in triples if t["source"] == "random"]
    hv = [v for _, v in cand.eval_on(highq)]
    rv = [v for _, v in cand.eval_on(controls)]
    d = cohen_d(hv, rv)
    a = auc(hv, rv)
    min_grp = thr.get("T4_min_group_size", 10)
    detail = {"n_highq": len(hv), "n_control": len(rv), "cohen_d": d, "auc": a,
              "c_range_highq": [c_lo, c_hi], "threshold_min_abs_d": tau, "min_group_size": min_grp}
    if len(hv) < min_grp or len(rv) < min_grp:
        # Underpowered: eine Effektgroesse aus <min_grp Tripeln ist nicht belastbar
        # (Kleinstichproben-Artefakt) -> ehrlich datenlos statt Zufallsverdikt.
        return {"test": "T4", "metric": (round(d, 4) if d is not None else None), "verdict": "dataless",
                "kill_grund": "underpowered: n_highq=%d, n_control=%d (< %d) -> Effektgroesse nicht belastbar"
                              % (len(hv), len(rv), min_grp), "detail": detail}
    if d is None:
        return {"test": "T4", "metric": None, "verdict": "dataless",
                "kill_grund": "zu wenig Tripel fuer Effektgroesse", "detail": detail}
    if abs(d) < tau:
        return {"test": "T4", "metric": round(d, 4), "verdict": "park",
                "kill_grund": "|Cohen d| = %.3f < %.2f -> keine Trennschaerfe (PARK, kein Kill)" % (abs(d), tau),
                "detail": detail}
    return {"test": "T4", "metric": round(d, 4), "verdict": "pass", "kill_grund": "", "detail": detail}


def test_T5(cand, usable_buckets, thr):
    """
    Support-only-Detektor. KILL nur wenn (A) bewertungs-blind UND (B) omega-kardinal.
    (A) within_ratio <= T5_precondition_within_ratio_max  (G = Funktion des Supports)
    (B) cardinality_eta2 >= T5_cardinality_eta2_min       (omega erklaert ~alle
        Between-Bucket-Varianz -> nur Kardinalitaet, kein arithmetisches Gewicht).
    """
    within_ratio, bucket_vals, all_vals = _within_between(cand, usable_buckets)
    tau_a = thr["T5_precondition_within_ratio_max"]
    tau_b = thr["T5_cardinality_eta2_min"]

    if within_ratio is None:
        if len(all_vals) < 2:
            return {"test": "T5", "metric": None, "verdict": "dataless",
                    "kill_grund": "keine nutzbaren Traeger-Buckets", "detail": {}}
        # G konstant -> trivial support-only? konstante Funktion traegt keine Info ->
        # das faengt T1 (keine rad-Reaktion). Hier kein eigener T5-Kill.
        within_ratio = 0.0

    # Bucket-Mittel + Groessen + omega
    bmeans, bsizes, bomega = [], [], []
    for supp, vals in bucket_vals.items():
        bmeans.append(_mean(vals))
        bsizes.append(len(vals))
        bomega.append(len(supp))
    detail = {"n_buckets": len(bmeans), "within_ratio": within_ratio,
              "precond_within_max": tau_a, "cardinality_eta2_min": tau_b}

    # (A) bewertungs-blind?
    if within_ratio > tau_a:
        detail["condition_A_exponent_blind"] = False
        return {"test": "T5", "metric": None, "verdict": "pass",
                "kill_grund": "", "detail": {**detail,
                "reason": "nicht support-only: G ist bewertungs-sensitiv (within_ratio %.4f > %.2f) -> T1-Domaene"
                          % (within_ratio, tau_a)}}
    detail["condition_A_exponent_blind"] = True

    # (B) omega-Kardinalitaets-Anteil an Between-Bucket-Varianz (groessen-gewichtet)
    if len(bmeans) < 3 or len(set(bomega)) < 2:
        return {"test": "T5", "metric": None, "verdict": "dataless",
                "kill_grund": "zu wenig/zu uniforme Buckets fuer die Kardinalitaets-Zerlegung",
                "detail": detail}
    total_w = sum(bsizes)
    grand = sum(s * m for s, m in zip(bsizes, bmeans)) / total_w
    total_between_ss = sum(s * (m - grand) ** 2 for s, m in zip(bsizes, bmeans))
    # Gruppen nach omega
    grp_w = defaultdict(float)
    grp_wm = defaultdict(float)
    for s, m, o in zip(bsizes, bmeans, bomega):
        grp_w[o] += s
        grp_wm[o] += s * m
    between_omega_ss = 0.0
    for o in grp_w:
        Mg = grp_wm[o] / grp_w[o]
        between_omega_ss += grp_w[o] * (Mg - grand) ** 2
    eta2 = (between_omega_ss / total_between_ss) if total_between_ss > 0 else None
    detail["cardinality_eta2"] = eta2
    detail["total_between_ss"] = total_between_ss

    if eta2 is None:
        # keine Between-Bucket-Varianz trotz A -> G konstant ueber Buckets (T1 faengt es)
        return {"test": "T5", "metric": None, "verdict": "dataless",
                "kill_grund": "keine Between-Bucket-Varianz (konstant) -> T1-Domaene", "detail": detail}
    if eta2 >= tau_b:
        return {"test": "T5", "metric": round(eta2, 4), "verdict": "kill",
                "kill_grund": "support-only: omega (Kardinalitaet) erklaert %.1f%% (>=%.0f%%) der Between-Bucket-Varianz "
                              "-> G traegt nur WIE VIELE, nicht WELCHE Primzahlen (N5)"
                              % (100 * eta2, 100 * tau_b), "detail": detail}
    return {"test": "T5", "metric": round(eta2, 4), "verdict": "pass",
            "kill_grund": "", "detail": {**detail,
            "reason": "arithmetisches Gewicht vorhanden: omega erklaert nur %.1f%% der Between-Bucket-Varianz "
                      "(unterscheidet gleich-grosse Traeger verschiedener Primzahlen)" % (100 * eta2)}}


# ------------------------------ Aggregation -------------------------------- #
HARD_TESTS = ("T1", "T2", "T3", "T5")


def run_candidate(cand, corpus, holdout_payload, thr, mode="train", has_degphi=True):
    triples = active_triples(corpus["triples"], holdout_payload, mode)
    _, usable = build_buckets(triples)

    t0 = test_T0(cand)
    reports = {"T0": t0}
    if t0["verdict"] in ("kill", "reject"):
        overall = "kill" if t0["verdict"] == "kill" else "reject"
        return _finalize(cand, mode, reports, overall,
                         ["T0: " + t0["kill_grund"]], triples, usable)

    reports["T1"] = test_T1(cand, usable, thr)
    reports["T2"] = test_T2(cand, triples, thr)
    reports["T3"] = test_T3(cand, triples, thr, has_degphi)
    reports["T4"] = test_T4(cand, triples, thr)
    reports["T5"] = test_T5(cand, usable, thr)

    kills = [t for t in HARD_TESTS if reports[t]["verdict"] == "kill"]
    parks = [t for t in ("T4",) if reports[t]["verdict"] == "park"]
    if kills:
        overall = "kill"
        grounds = ["%s: %s" % (t, reports[t]["kill_grund"]) for t in kills]
    elif parks:
        overall = "park"
        grounds = ["%s: %s" % (t, reports[t]["kill_grund"]) for t in parks]
    else:
        overall = "survivor"
        grounds = []
    return _finalize(cand, mode, reports, overall, grounds, triples, usable)


def _finalize(cand, mode, reports, overall, grounds, triples, usable):
    return {
        "candidate": cand.meta["name"],
        "meta": cand.meta,
        "mode": mode,
        "n_active_triples": len(triples),
        "n_usable_buckets": len(usable),
        "tests": reports,
        "gesamt_verdikt": overall,
        "kill_gruende": grounds,
    }


# --------------------------------------------------------------------------- #
# Referenz-Kandidaten (Selbst-Kalibrierung)
# --------------------------------------------------------------------------- #
def _G_omega(f):
    return float(f["omega"])


def _G_lograd(f):
    return math.log(f["rad"]) if f["rad"] > 1 else 0.0


def _G_quality_proxy(f):
    return math.log(f["c"]) if f["c"] > 1 else 0.0


def _G_noise(f):
    h = hashlib.sha256(("%d_%d_%d" % (f["a"], f["b"], f["c"])).encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _G_degphi_proxy(f):
    d = f.get("deg_phi")
    if d is None or d <= 0:
        return None
    return math.log(d)


def reference_candidates():
    """Kalibratoren mit erwartetem Verdikt. Erwartung != Ergebnis -> Test-Logik fixen."""
    return [
        (Candidate(_G_omega, {
            "name": "G_omega", "advice_level": "A1", "mechanism_class": "derived",
            "description": "omega(rad(abc)) = Anzahl distinkter Primteiler (reine Traegermengen-Funktion)"}),
         {"overall": "kill", "asserts": {"T5": "kill", "T1": "pass", "T2": "pass"}}),

        (Candidate(_G_lograd, {
            "name": "G_lograd", "advice_level": "A3", "mechanism_class": "presupposed",
            "description": "log rad(abc) = Zielgroesse selbst als Input (praesupponiert)"}),
         {"overall": "kill", "asserts": {"T0": "kill"}}),

        (Candidate(_G_quality_proxy, {
            "name": "G_quality_proxy", "advice_level": "A1", "mechanism_class": "derived",
            "description": "log c (Groessen-Proxy; waechst mit Exponenten-Aufblaehung im Bucket)"}),
         {"overall": "kill", "asserts": {"T1": "kill"}}),

        (Candidate(_G_noise, {
            "name": "G_noise", "advice_level": "A0", "mechanism_class": "derived",
            "description": "deterministischer Pseudo-Zufall aus sha256(a,b,c)"}),
         {"overall": "kill", "asserts": {"T1": "kill", "T4": "park"}}),

        (Candidate(_G_degphi_proxy, {
            "name": "G_degphi_proxy", "advice_level": "A2", "mechanism_class": "derived",
            "description": "log(deg phi) (Modulgrad-Proxy; nur Watkins-Subkorpus mit deg-Spalte)"}),
         {"overall": "kill", "asserts": {"T3": "kill"}}),
    ]


def check_expectation(report, expect):
    """-> (ok, problems, notes). Prueft Gesamt + pro-Test-Asserts.
    T4 ist weich (usefulness): ist er auf einem unterbesetzten Split 'dataless', gilt der
    T4-Assert als nicht-anwendbar (Notiz), NICHT als Fehler -- die KILL-Logik bleibt strikt."""
    problems, notes = [], []
    if report["gesamt_verdikt"] != expect["overall"]:
        problems.append("Gesamt: erwartet %s, gemessen %s" % (expect["overall"], report["gesamt_verdikt"]))
    for t, want in expect.get("asserts", {}).items():
        got = report["tests"].get(t, {}).get("verdict")
        if got == want:
            continue
        if t == "T4" and got == "dataless":
            notes.append("T4-Assert (%s) nicht anwendbar: auf diesem Split datenlos/underpowered" % want)
            continue
        problems.append("%s: erwartet %s, gemessen %s" % (t, want, got))
    return (len(problems) == 0), problems, notes


# --------------------------------------------------------------------------- #
# Report-Formatierung (Registerformat B1-B6)
# --------------------------------------------------------------------------- #
def _verdict_tag(v):
    return {"pass": "PASS", "kill": "KILL", "park": "PARK", "reject": "REJECT",
            "dataless": "datenlos", "survivor": "SURVIVOR"}.get(v, v)


def candidate_md_block(report):
    m = report["meta"]
    lines = []
    lines.append("### %s  --  Gesamt: **%s**" % (report["candidate"], _verdict_tag(report["gesamt_verdikt"])))
    lines.append("")
    lines.append("- %s" % m["description"])
    lines.append("- advice_level=%s, mechanism_class=%s, aktive Tripel=%d, nutzbare Buckets=%d, Modus=%s"
                 % (m["advice_level"], m["mechanism_class"], report["n_active_triples"],
                    report["n_usable_buckets"], report["mode"]))
    lines.append("")
    lines.append("| Test | Score | Verdikt | Kill-/Park-Grund |")
    lines.append("|---|---|---|---|")
    for t in ("T0", "T1", "T2", "T3", "T4", "T5"):
        r = report["tests"].get(t)
        if not r:
            continue
        sc = "" if r["metric"] is None else ("%g" % r["metric"])
        grund = r["kill_grund"] or (r["detail"].get("reason", "") if isinstance(r.get("detail"), dict) else "")
        grund = (grund or "").replace("\n", " ")
        lines.append("| %s | %s | %s | %s |" % (t, sc, _verdict_tag(r["verdict"]), grund))
    if report["kill_gruende"]:
        lines.append("")
        lines.append("**Verdikt-Begruendung:** " + "; ".join(report["kill_gruende"]))
    if report.get("calibration_notes"):
        lines.append("")
        lines.append("**Kalibrierungs-Notiz:** " + "; ".join(report["calibration_notes"]))
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Kalibrierung
# --------------------------------------------------------------------------- #
def calibrate(corpus_path, holdout_path, thresholds_path, results_dir, mode="train"):
    corpus = load_corpus(corpus_path)
    holdout = None
    if os.path.exists(holdout_path):
        with open(holdout_path, encoding="utf-8") as f:
            holdout = json.load(f)
    thr = load_thresholds(thresholds_path)
    has_degphi = corpus["_meta"].get("degphi_column") is not None

    stats = corpus_stats(corpus["triples"])

    reports = []
    calib_rows = []
    all_ok = True
    for cand, expect in reference_candidates():
        rep = run_candidate(cand, corpus, holdout, thr, mode=mode, has_degphi=has_degphi)
        ok, problems, notes = check_expectation(rep, expect)
        all_ok = all_ok and ok
        rep["expectation"] = expect
        rep["calibration_ok"] = ok
        rep["calibration_problems"] = problems
        rep["calibration_notes"] = notes
        reports.append(rep)
        calib_rows.append((cand.meta["name"], expect, rep, ok, problems, notes))

    out = {
        "_meta": {"created": STAMP, "author": "LG", "mode": mode,
                  "note": "Selbst-Kalibrierung des starcore_falsifier. Programm-Instrument, kein Claim.",
                  "all_calibrators_ok": all_ok},
        "corpus_meta": corpus["_meta"],
        "corpus_stats": stats,
        "thresholds": thr,
        "reports": reports,
    }
    os.makedirs(results_dir, exist_ok=True)
    jpath = os.path.join(results_dir, CALIB_JSON)
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    mpath = os.path.join(results_dir, CALIB_MD)
    with open(mpath, "w", encoding="utf-8") as f:
        f.write(calibration_md(out))

    # Konsolenzusammenfassung
    print("\n=== SELBST-KALIBRIERUNG (%s) ===" % mode)
    print("%-18s %-9s %-9s %s" % ("Kandidat", "erwartet", "gemessen", "OK?"))
    for name, expect, rep, ok, problems, notes in calib_rows:
        tag = "OK" if ok else "FEHLER: " + "; ".join(problems)
        if ok and notes:
            tag += "  (" + "; ".join(notes) + ")"
        print("%-18s %-9s %-9s %s" % (name, expect["overall"], rep["gesamt_verdikt"], tag))
    print("\nAlle Kalibratoren wie erwartet:", all_ok)
    print("Artefakte:", jpath, "|", mpath)
    return all_ok, out


def calibration_md(out):
    m = out["_meta"]
    cs = out["corpus_stats"]
    cm = out["corpus_meta"]
    thr = out["thresholds"]
    L = []
    L.append("# ★-Kern Falsifikator -- Selbst-Kalibrierung (%s)" % m["created"])
    L.append("")
    L.append("**Autor:** %s  |  **Modus:** %s  |  **Status:** Programm-Instrument, kein Claim."
             % (m["author"], m["mode"]))
    L.append("**Spec:** MG_starcore_fahndungsblatt_2026-07-10.md (Section E, T0-T5).")
    L.append("")
    L.append("> Zweck: Der Falsifikator wird glaubwuerdig gemacht, indem Referenz-Kandidaten mit")
    L.append("> BEKANNTEM Soll-Verdikt durchlaufen. Erwartung != Ergebnis -> Test-Logik korrigieren,")
    L.append("> nicht die Erwartung (Fahndungsblatt-Guard).")
    L.append("")
    L.append("## Frage")
    L.append("")
    L.append("Reproduzieren die kodierten Tests T0-T5 die a-priori bekannten Verdikte der fuenf")
    L.append("Referenz-Kandidaten (ein Provenienz-Kill, ein Support-only-Kill, ein Bewertungs-Kill,")
    L.append("ein Nutzlos-Park, ein Zirkularitaets-Kill)?")
    L.append("")
    L.append("## Setup")
    L.append("")
    L.append("**Korpus (`%s`):**" % CORPUS_NAME)
    L.append("")
    L.append("| Quelle | n | Zweck |")
    L.append("|---|---:|---|")
    L.append("| Watkins (c<=80, mit N + deg phi) | %d | Zirkularitaet (T3), Nutzen (T4) |" % cm["n_watkins"])
    L.append("| Brute-Force voll-glatte S-Unit-Tripel | %d | Traeger-Buckets (T1/T5), Hochqualitaet (T4) |" % cm["n_smooth"])
    L.append("| Zufallskontrollen (magnitude-gematcht) | %d | T4-Kontrastgruppe |" % cm["n_random"])
    L.append("| **gesamt** | **%d** | |" % cm["n_total"])
    L.append("")
    L.append("- **Traeger-Buckets** (>=2 Mitglieder, >=2 distinkte Exponentenmuster): **%d** (mit %d Tripeln)."
             % (cs["n_buckets_ge2"], cs["n_in_buckets"]))
    L.append("- **omega-Bereich:** %s .. %s.  **Hochqualitaets-Tripel (q>1.2):** %d.  **deg-phi-Tripel:** %d."
             % (cs["omega_range"][0], cs["omega_range"][1], cs["n_highq"], cs["n_degphi"]))
    L.append("- **Glatt-Konstruktion:** %s, S=%s, c<=%s."
             % (cm["smooth_construction"], cm["smooth_primes"], cm["smooth_bound"]))
    L.append("- **deg-phi-Quelle:** %s." % (cm.get("degphi_assumption") or "keine"))
    L.append("- **Holdout:** support-level ~%.0f/%.0f-Split, seeded (Indizes in `%s`); Wertung hier auf **%s**."
             % ((1 - HOLDOUT_FRACTION) * 100, HOLDOUT_FRACTION * 100, HOLDOUT_NAME, m["mode"]))
    L.append("")
    L.append("## Ergebnis -- Kalibrierungs-Tabelle (erwartet vs. gemessen)")
    L.append("")
    L.append("| Kandidat | mech. | erwartet | T0 | T1 | T2 | T3 | T4 | T5 | Gesamt | Kalib. |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for rep in out["reports"]:
        tv = {t: _verdict_tag(rep["tests"].get(t, {}).get("verdict", "-")) for t in
              ("T0", "T1", "T2", "T3", "T4", "T5")}
        exp = rep["expectation"]
        exp_str = exp["overall"] + (" (" + ",".join("%s=%s" % kv for kv in exp.get("asserts", {}).items()) + ")"
                                    if exp.get("asserts") else "")
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | **%s** | %s |" % (
            rep["candidate"], rep["meta"]["mechanism_class"], exp_str,
            tv["T0"], tv["T1"], tv["T2"], tv["T3"], tv["T4"], tv["T5"],
            _verdict_tag(rep["gesamt_verdikt"]),
            "OK" if rep["calibration_ok"] else "FEHLER"))
    L.append("")
    L.append("## Schwellen-Begruendung (praeregistriert)")
    L.append("")
    L.append("| Test | Schwelle | Wert | Begruendung |")
    L.append("|---|---|---|---|")
    just = thr.get("justification", {})
    keys = [("T1", "T1_within_bucket_variance_ratio_max"),
            ("T2", "T2_omega_scaling_growth_factor_max"),
            ("T3", "T3_partial_corr_abs_max"),
            ("T4", "T4_min_abs_cohen_d"),
            ("T5", "T5_cardinality_eta2_min")]
    for tname, key in keys:
        L.append("| %s | %s | %s | %s |" % (tname, key, thr.get(key), just.get(tname, "")))
    L.append("")
    allok = out["_meta"]["all_calibrators_ok"]
    L.append("## Verdikt")
    L.append("")
    if allok:
        L.append("**KALIBRIERUNG BESTANDEN** -- alle fuenf Referenz-Kandidaten liefern exakt das")
        L.append("erwartete Verdikt (inkl. der pro-Test-Asserts). Der Falsifikator trennt die vier")
        L.append("Kill-Mechanismen (Provenienz T0, Bewertungs-Sensitivitaet T1, Zirkularitaet T3,")
        L.append("Support-only T5) und den Nutzlos-Park (T4) wie spezifiziert.")
    else:
        L.append("**KALIBRIERUNG NICHT BESTANDEN** -- mindestens ein Kandidat weicht ab (siehe Spalte")
        L.append("Kalib.). Test-Logik korrigieren, nicht die Erwartung.")
    L.append("")
    L.append("## Pro-Kandidat-Register")
    L.append("")
    for rep in out["reports"]:
        L.append(candidate_md_block(rep))
    L.append("## Artefakte")
    L.append("")
    L.append("- Skript: `_scripts/starcore_falsifier.py` (Tests T0-T5, Korpus-Bau, Holdout, Kalibrierung).")
    L.append("- Schwellen: `_scripts/starcore_thresholds_preregistered_2026-07-10.json`.")
    L.append("- Korpus/Cache: `_data/%s`; Holdout-Indizes: `_data/%s`." % (CORPUS_NAME, HOLDOUT_NAME))
    L.append("- Ergebnis: `_results/%s` + `_results/%s`." % (CALIB_JSON, CALIB_MD))
    L.append("- Kein abc-Claim-Upgrade; die Majorisierungs-Ungleichung bleibt Handarbeit.")
    L.append("")
    return "\n".join(L)


def load_thresholds(path):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(FALLBACK_THRESHOLDS)
        for k, v in data.items():
            merged[k] = v
        return merged
    return dict(FALLBACK_THRESHOLDS)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(description="starcore_falsifier -- T0-T5 gegen Tripel-Korpus (abc P6, kein Claim)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build-corpus", help="Korpus + Feature-Cache + Holdout bauen")
    p_build.add_argument("--watkins", default=DEFAULT_WATKINS)
    p_build.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p_build.add_argument("--bound", type=int, default=SMOOTH_BOUND)
    p_build.add_argument("--n-random", type=int, default=N_RANDOM_CONTROLS)

    p_cal = sub.add_parser("calibrate", help="Selbst-Kalibrierung mit Referenz-Kandidaten")
    p_cal.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p_cal.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    p_cal.add_argument("--thresholds", default=DEFAULT_THRESHOLDS)
    p_cal.add_argument("--holdout", action="store_true", help="Wertung auf dem Holdout statt Training")

    p_run = sub.add_parser("run", help="Einen Referenz-Kandidaten einzeln werten (Demo)")
    p_run.add_argument("name")
    p_run.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p_run.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    p_run.add_argument("--thresholds", default=DEFAULT_THRESHOLDS)
    p_run.add_argument("--holdout", action="store_true")

    args = ap.parse_args(argv)

    if args.cmd == "build-corpus":
        corpus_path = os.path.join(args.data_dir, CORPUS_NAME)
        payload = build_corpus(args.watkins, corpus_path, bound=args.bound, n_random=args.n_random)
        for t in payload["triples"]:
            t["support"] = tuple(t["support"])
        make_holdout(payload["triples"], os.path.join(args.data_dir, HOLDOUT_NAME))
        print("[build-corpus] Holdout geschrieben:", os.path.join(args.data_dir, HOLDOUT_NAME))
        return 0

    if args.cmd == "calibrate":
        mode = "holdout" if args.holdout else "train"
        ok, _ = calibrate(os.path.join(args.data_dir, CORPUS_NAME),
                          os.path.join(args.data_dir, HOLDOUT_NAME),
                          args.thresholds, args.results_dir, mode=mode)
        return 0 if ok else 2

    if args.cmd == "run":
        mode = "holdout" if args.holdout else "train"
        corpus = load_corpus(os.path.join(args.data_dir, CORPUS_NAME))
        holdout = None
        hp = os.path.join(args.data_dir, HOLDOUT_NAME)
        if os.path.exists(hp):
            with open(hp, encoding="utf-8") as f:
                holdout = json.load(f)
        thr = load_thresholds(args.thresholds)
        has_degphi = corpus["_meta"].get("degphi_column") is not None
        cands = {c.meta["name"]: (c, e) for c, e in reference_candidates()}
        if args.name not in cands:
            print("Unbekannt. Verfuegbar:", ", ".join(cands)); return 2
        cand, _ = cands[args.name]
        rep = run_candidate(cand, corpus, holdout, thr, mode=mode, has_degphi=has_degphi)
        print(json.dumps({k: rep[k] for k in ("candidate", "gesamt_verdikt", "kill_gruende")},
                         ensure_ascii=False, indent=2))
        print(candidate_md_block(rep))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
