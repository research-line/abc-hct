"""Probe Sage's modular-symbol API for constructing cusp-to-cusp elements.

This is a small companion to the G1/P1' prototype.  It records which element
constructors are available in the installed Sage build, so the actual
maximal-ideal test can target the local API instead of guessing.
"""

from __future__ import annotations

import json
from pathlib import Path

from sage.all import GF, Gamma0, ModularSymbols, QQ  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_results" / "g1_sage_modsym_api_probe_2026-05-09.json"


def summarize(obj) -> dict:
    names = dir(obj)
    interesting = [
        name
        for name in names
        if any(key in name.lower() for key in ("symbol", "manin", "cusp", "ambient", "coord", "basis", "vector"))
    ]
    return {
        "class": type(obj).__name__,
        "repr": repr(obj)[:500],
        "interesting_methods": interesting[:200],
    }


def vectorish(value) -> dict:
    out = {"type": type(value).__name__, "repr": repr(value)[:500]}
    for attr in ("parent", "base_ring", "degree", "dimension", "length"):
        if hasattr(value, attr):
            try:
                out[attr] = repr(getattr(value, attr)())[:200]
            except Exception as exc:
                out[attr] = f"{type(exc).__name__}: {exc}"
    return out


def try_call(label: str, func) -> dict:
    try:
        value = func()
        return {
            "label": label,
            "ok": True,
            "type": type(value).__name__,
            "repr": repr(value)[:500],
            "has_vector": hasattr(value, "vector"),
            "vector_repr": repr(value.vector())[:500] if hasattr(value, "vector") else None,
            "summary": vectorish(value),
        }
    except Exception as exc:
        return {"label": label, "ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> None:
    F = GF(3)
    M0 = ModularSymbols(Gamma0(30), 2, sign=0, base_ring=F)
    M = M0.cuspidal_submodule()
    ambient = M.ambient_module()

    trials = []
    for module_label, module in (("M0", M0), ("M", M), ("ambient", ambient)):
        trials.extend(
            [
                try_call(f"{module_label}.modular_symbol([0, QQ(5)/32])", lambda module=module: module.modular_symbol([0, QQ(5) / 32])),
                try_call(f"{module_label}.modular_symbol([QQ(0), QQ(5)/32])", lambda module=module: module.modular_symbol([QQ(0), QQ(5) / 32])),
                try_call(f"{module_label}([0, QQ(5)/32])", lambda module=module: module([0, QQ(5) / 32])),
                try_call(f"{module_label}.linear_combination_of_basis([1,0,...])", lambda module=module: module.linear_combination_of_basis([F(1)] + [F(0)] * (module.dimension() - 1))),
            ]
        )

    e = ambient.modular_symbol([0, QQ(5) / 32])
    extra_trials = [
        try_call("ambient.coordinate_vector(e)", lambda: ambient.coordinate_vector(e)),
        try_call("M0.coordinate_vector(e)", lambda: M0.coordinate_vector(e)),
        try_call("M.coordinate_vector(e)", lambda: M.coordinate_vector(e)),
        try_call("ambient.coordinate_vector(M0(e))", lambda: ambient.coordinate_vector(M0(e))),
        try_call("M0.free_module()", lambda: M0.free_module()),
        try_call("ambient.free_module()", lambda: ambient.free_module()),
        try_call("M.free_module()", lambda: M.free_module()),
        try_call("M.basis_matrix()", lambda: M.basis_matrix()),
        try_call("ambient.basis_matrix()", lambda: ambient.basis_matrix()),
        try_call("M0.basis_matrix()", lambda: M0.basis_matrix()),
    ]

    output = {
        "status": "ok",
        "module": summarize(M),
        "ambient": summarize(ambient),
        "trials": trials,
        "extra_trials": extra_trials,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
