"""Validate exported aggregates without access to patient data or private sources."""
import csv
import json
from pathlib import Path
import numpy as np
from ecg_audit import rank_agreement

ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT / "results" / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    p, t, r, b, a = [rows(n) for n in ["primary.csv", "age_thresholds.csv", "rank_agreement.csv",
                                      "budget_selection.csv", "auxiliary_survival.csv"]]
    assert (len(p), len(t), len(r), len(b), len(a)) == (20, 100, 20, 180, 24)
    assert len({(x["cohort"], x["encoder"]) for x in p}) == 20
    for row in p:
        assert np.isclose(abs(float(row["q75_per_1000"])), float(row["abs_q75_per_1000"]))
        assert 0 <= float(row["uno_c"]) <= 1 and 0 <= float(row["ibs"]) <= 1
        match = [x for x in t if x["cohort"] == row["cohort"] and x["encoder"] == row["encoder"] and x["age_threshold"] == "75"]
        assert len(match) == 1 and np.isclose(float(match[0]["abs_q_per_1000"]), float(row["abs_q75_per_1000"]))
    for row in r:
        group = [x for x in t if x["cohort"] == row["cohort"] and x["age_threshold"] == row["age_threshold"]
                 and not (row["exclude_age_auxiliary"] == "1" and x["encoder"] == "SMS")]
        result = rank_agreement([float(x["global_age_r2"]) for x in group],
                                [float(x["abs_q_per_1000"]) for x in group], exact=True)
        assert result["n_encoders"] == int(row["n_encoders"])
        assert abs(result["rho_agree"] - float(row["rho_agree"])) < 1e-12
        assert abs(result["exact_p"] - float(row["exact_p"])) < 1e-12
    for row in b:
        assert 0 < int(row["n_valid"]) <= int(row["n_attempted"]) == 50
        assert float(row["lower"]) <= float(row["mean"]) + 1e-10 <= float(row["upper"]) + 1e-10
    for row in a:
        assert float(row["signed_q_ci_low"]) <= float(row["signed_q_per_1000"]) <= float(row["signed_q_ci_high"])
    # Adverse C findings must not disappear from the public snapshot.
    for method in ["mae", "dae"]:
        pair = {x["condition"]: float(x["uno_c"]) for x in a if x["cohort"] == "MIMIC" and x["method_key"] == method}
        assert pair["age_aux_ecg"] < pair["base_ecg"]
    ep = rows("external_auxiliary.csv")
    assert len(ep) == 18
    for row in ep:
        assert np.isclose(float(row["plus_age_mean"]) - float(row["base_mean"]), float(row["paired_delta"]))
    print(json.dumps({"status":"PASS", "primary_rows":len(p), "threshold_rows":len(t),
                      "rank_rows":len(r), "budget_rows":len(b), "auxiliary_rows":len(a),
                      "external_paired_rows":len(ep), "patient_data_required":False}))


if __name__ == "__main__":
    main()
