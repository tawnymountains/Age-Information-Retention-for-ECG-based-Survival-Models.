"""Runnable synthetic representation demo. NO real ECGs, patients or paper results."""
import json
import numpy as np
from ecg_audit import crossfit_age, subgroup_error, rank_agreement, select_encoder


def main():
    rng = np.random.default_rng(2026)  # Arbitrary public demo seed, not a study seed.
    n = 240
    ages = rng.uniform(35, 90, n)
    groups = np.arange(n)
    x = rng.normal(size=(n, 24))
    x[:, 0] = (ages - 60) / 12 + rng.normal(0, .5, n)
    probe = crossfit_age(x, ages, groups, alphas=[.1, 1, 10], outer_folds=5, inner_folds=3)
    # Synthetic right-censored event times; time unit is arbitrary demo years.
    event_time = rng.exponential(1 / (.03 * np.exp((ages - 60) / 30)))
    censor_time = rng.uniform(3, 8, n)
    time = np.minimum(event_time, censor_time)
    event = event_time <= censor_time
    risk = 1 - np.exp(-.03 * 5 * np.exp((ages - 60) / 40))
    report = {
        "data_kind": "synthetic_demo_not_paper_evidence",
        "global_age_r2": probe["global_age_r2"],
        "older_subgroup": subgroup_error(time, event, risk, ages, horizon=5, threshold=75),
        "toy_rank_agreement": rank_agreement([.2, .4, .6, .8], [50, 40, 20, 30], exact=True),
        "toy_selected_encoder": select_encoder({"a": .2, "b": .6, "c": .4},
                                                 candidates=["a", "b", "c"], maximize=True)
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
