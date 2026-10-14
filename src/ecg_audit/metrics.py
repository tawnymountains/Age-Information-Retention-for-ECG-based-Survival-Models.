"""Auditable metric definitions. Q always means observed minus predicted risk."""
from functools import lru_cache
from itertools import islice, permutations
import math
import numpy as np
from scipy.stats import rankdata, spearmanr


def _vector(values, name):
    a = np.asarray(values, dtype=float)
    if a.ndim != 1 or not len(a) or not np.isfinite(a).all():
        raise ValueError(f"{name} must be a nonempty finite vector")
    return a


def global_age_r2(age, oof_prediction):
    """One pooled OOF R², not an average of fold R² values. May be negative."""
    y, pred = _vector(age, "age"), _vector(oof_prediction, "oof_prediction")
    if y.shape != pred.shape:
        raise ValueError("age and prediction lengths differ")
    denominator = np.sum((y - y.mean()) ** 2)
    if denominator <= 0:
        raise ValueError("R² is undefined for constant age")
    return float(1 - np.sum((y - pred) ** 2) / denominator)


def km_event_risk(time, event, horizon):
    """1-KM(H); events at H included, tied censorings remain in the risk set."""
    t, e = _vector(time, "time"), _vector(event, "event")
    if t.shape != e.shape or np.any(t < 0) or not np.isin(e, [0, 1]).all():
        raise ValueError("Invalid event indicators or observation times")
    if not np.isfinite(horizon) or horizon < 0 or horizon > t.max():
        raise ValueError("Horizon must be nonnegative and within observed follow-up")
    survival = 1.0
    for u in np.unique(t[(e == 1) & (t <= horizon)]):
        survival *= 1.0 - np.sum((t == u) & (e == 1)) / np.sum(t >= u)
    return float(1 - survival)


def subgroup_error(time, event, risk, age, *, horizon, threshold):
    """Return subgroup Q and |Q| per 1,000; requires a supported subgroup horizon."""
    t, e, r, a = [_vector(v, name) for v, name in
                   [(time, "time"), (event, "event"), (risk, "risk"), (age, "age")]]
    if not (t.shape == e.shape == r.shape == a.shape):
        raise ValueError("All patient arrays must be aligned")
    if np.any((r < 0) | (r > 1)) or not np.isfinite(threshold):
        raise ValueError("Risk must be in [0, 1] and threshold finite")
    mask = a >= threshold
    if not mask.any():
        raise ValueError("Empty age subgroup")
    observed = km_event_risk(t[mask], e[mask], horizon)
    predicted = float(r[mask].mean())
    q = 1000 * (observed - predicted)
    return {"n": int(mask.sum()), "observed_risk": observed,
            "mean_predicted_risk": predicted, "q_per_1000": q,
            "abs_q_per_1000": abs(q)}


@lru_cache(maxsize=24)
def _exact_null(x_ranks, y_ranks):
    """Enumerate permutations of pairings, including multiplicity of tied ranks."""
    x, y = np.asarray(x_ranks), np.asarray(y_ranks)
    x, y = x - x.mean(), y - y.mean()
    denominator = np.linalg.norm(x) * np.linalg.norm(y)
    iterator = permutations(y.tolist())
    chunks = []
    while True:
        batch = list(islice(iterator, 40000))
        if not batch:
            break
        chunks.append(np.abs(np.asarray(batch) @ x / denominator))
    return np.sort(np.concatenate(chunks))


def rank_agreement(age_scores, absolute_errors, *, exact=False):
    """Spearman(age score, -absolute error); positive means preferred ranks agree.

    Exact p is two-sided, unadjusted, exhaustive (n <= 10). No causal inference.
    """
    x, y = _vector(age_scores, "age_scores"), _vector(absolute_errors, "absolute_errors")
    if x.shape != y.shape or len(x) < 3 or np.any(y < 0):
        raise ValueError("At least three aligned encoders and nonnegative errors required")
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        raise ValueError("Spearman correlation is undefined for constant ranks")
    rho = float(spearmanr(x, -y).statistic)
    result = {"n_encoders": len(x), "rho_agree": rho}
    if exact:
        if len(x) > 10:
            raise ValueError("Exhaustive enumeration is limited to ten encoders")
        order = np.argsort(x, kind="stable")
        xr = tuple(rankdata(x)[order])
        yr = tuple(sorted(rankdata(-y)))
        null = _exact_null(xr, yr)
        count = len(null) - np.searchsorted(null, abs(rho) - 1e-12, side="left")
        result.update(exact_p=float(count / math.factorial(len(x))),
                      permutations=math.factorial(len(x)))
    return result
