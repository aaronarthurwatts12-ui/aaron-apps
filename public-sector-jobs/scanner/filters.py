"""Title matching against config/roles.yaml, per organisation size band."""
import re
from pathlib import Path
import yaml

CFG = yaml.safe_load((Path(__file__).parent.parent / "config" / "roles.yaml").read_text())
_c = lambda pats: [re.compile(p, re.I) for p in pats]
FUNCS = {k: _c(v) for k, v in CFG["functions"].items()}
SEN = {b: {"require": _c(v["require"]), "exclude": _c(v["exclude"])} for b, v in CFG["seniority"].items()}
BAND_FUNCS = CFG["band_functions"]
GLOBAL_EX = _c(CFG.get("global_exclude", []))


def functions_for(title):
    return [name for name, pats in FUNCS.items() if any(p.search(title) for p in pats)]


def matches(title, band):
    """Return the matched function names if the title qualifies for this band, else []."""
    if band not in SEN:
        return []
    funcs = [f for f in functions_for(title) if f in BAND_FUNCS[band]]
    if not funcs:
        return []
    if any(p.search(title) for p in GLOBAL_EX):
        return []
    s = SEN[band]
    if any(p.search(title) for p in s["exclude"]):
        return []
    if s["require"] and not any(p.search(title) for p in s["require"]):
        return []
    return funcs
