"""Choose using selection-set scores only, never independent evaluation outcomes."""
import math


def select_encoder(scores, *, candidates, maximize):
    names = list(candidates)
    if not names or len(set(names)) != len(names) or set(scores) != set(names):
        raise ValueError("Require exactly one score for every candidate; do not silently drop models")
    if not all(math.isfinite(float(scores[name])) for name in names):
        raise ValueError("Incomplete repetition: a candidate score is missing or nonfinite")
    # Predeclared lexical tie break, independent of evaluation endpoints.
    return sorted(names, key=lambda name: (-float(scores[name]) if maximize else float(scores[name]), name))[0]
