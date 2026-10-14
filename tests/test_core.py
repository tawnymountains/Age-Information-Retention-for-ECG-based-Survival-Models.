import unittest
import numpy as np
from ecg_audit import global_age_r2, km_event_risk, subgroup_error, rank_agreement, crossfit_age, select_encoder


class MetricTests(unittest.TestCase):
    def test_r2(self):
        self.assertEqual(global_age_r2([1, 2, 3], [1, 2, 3]), 1)
        self.assertLess(global_age_r2([1, 2, 3], [9, 9, 9]), 0)
        with self.assertRaises(ValueError):
            global_age_r2([2, 2], [1, 3])

    def test_km_ties_and_censoring(self):
        # At time 1: one event out of four; at time 2: one event out of two.
        self.assertAlmostEqual(km_event_risk([1, 1, 2, 3], [1, 0, 1, 0], 2), .625)
        self.assertEqual(km_event_risk([1, 2], [0, 0], 2), 0)
        with self.assertRaises(ValueError):
            km_event_risk([1, 2], [1, 0], 3)

    def test_q_sign_and_empty(self):
        r = subgroup_error([1, 2, 3, 4], [1, 0, 0, 0], [.1]*4, [80]*4, horizon=2, threshold=75)
        self.assertAlmostEqual(r["q_per_1000"], 150)
        with self.assertRaises(ValueError):
            subgroup_error([1, 2], [1, 0], [.1, .1], [40, 50], horizon=1, threshold=75)

    def test_exact_rank(self):
        r = rank_agreement([1, 2, 3], [3, 2, 1], exact=True)
        self.assertAlmostEqual(r["rho_agree"], 1)
        self.assertAlmostEqual(r["exact_p"], 1/3)
        tied = rank_agreement([1, 1, 2], [2, 2, 1], exact=True)
        self.assertAlmostEqual(tied["exact_p"], 1/3)

    def test_invalid_rank(self):
        for errors in [[1, 1, 1], [1, -2, 3], [1, float("nan"), 3]]:
            with self.assertRaises(ValueError):
                rank_agreement([1, 2, 3], errors)

    def test_selection(self):
        self.assertEqual(select_encoder({"b": 2, "a": 2}, candidates=["a", "b"], maximize=True), "a")
        self.assertEqual(select_encoder({"a": 2, "b": 1}, candidates=["a", "b"], maximize=False), "b")
        with self.assertRaises(ValueError):
            select_encoder({"a": 1}, candidates=["a", "b"], maximize=True)
        with self.assertRaises(ValueError):
            select_encoder({"a": 1, "b": np.nan}, candidates=["a", "b"], maximize=True)

    def test_patient_groups_never_split(self):
        rng = np.random.default_rng(4)
        groups = np.repeat(np.arange(30), 2)
        age = np.repeat(rng.uniform(20, 90, 30), 2)
        x = np.column_stack([age + rng.normal(size=60), rng.normal(size=60)])
        r = crossfit_age(x, age, groups, alphas=[.1, 1], outer_folds=5, inner_folds=3)
        for group in np.unique(groups):
            self.assertEqual(len(np.unique(r["outer_fold"][groups == group])), 1)
        self.assertTrue(np.isfinite(r["oof_prediction"]).all())
        self.assertGreater(r["global_age_r2"], .9)


if __name__ == "__main__":
    unittest.main()
