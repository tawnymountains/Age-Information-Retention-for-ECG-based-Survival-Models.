import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicFileTests(unittest.TestCase):
    def test_repository_links(self):
        target = "https://github.com/tawnymountains/ecg-age-retention"
        obsolete = "https://github.com/tawnymountains/sms-ecg-audit"
        for name in ["README.md", "pyproject.toml", "CITATION.cff", "docs/index.html", "scripts/render_results.py", "docs/UPLOAD.md"]:
            with self.subTest(file=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertIn(target, text)
                self.assertNotIn(obsolete, text)

    def test_primary_snapshot(self):
        with (ROOT / "results/primary.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 20)
        for cohort in ["CODE", "MIMIC"]:
            subset = [r for r in rows if r["cohort"] == cohort]
            self.assertEqual(len({r["encoder"] for r in subset}), 10)
            self.assertTrue(all(float(r["q75_per_1000"]) > 0 for r in subset))

    def test_config_omissions_explicit(self):
        import json
        config = json.loads((ROOT / "configs/study.template.json").read_text())
        for key in ["ridge_alpha_grid", "cox_penalty", "encoder_training_config", "training_seeds", "patient_split_manifest"]:
            self.assertIsNone(config[key])

    def test_published_representative_values(self):
        with (ROOT / "results/rank_agreement.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        expected = {("CODE", "0"): .854545454545, ("MIMIC", "0"): .818181818182,
                    ("CODE", "1"): .8, ("MIMIC", "1"): .75}
        for row in rows:
            if row["age_threshold"] == "75":
                self.assertAlmostEqual(float(row["rho_agree"]), expected[(row["cohort"], row["exclude_age_auxiliary"])], places=9)


if __name__ == "__main__":
    unittest.main()
