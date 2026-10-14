# Evidence and release notes — v0.2.0

## Changed from the early SMS showcase

The public presentation now follows the current age-information-retention study: ten survival encoders, global age-R², signed subgroup risk error, age-threshold sensitivity, limited-budget selection, and auxiliary age supervision. It removes the earlier calibration-bound interface, label-break-even claims and stale transfer-results table. No old scientific number is silently carried over because it looked favorable.

The ten-encoder panel includes the jointly survival-and-diagnosis-supervised reference. It is not the unrelated diagnosis-only checkpoint. Survival encoders originate from CODE training; external diagnostic-cohort encoders are trained within those cohorts.

## Results included

- Primary survival results: 20 cohort/encoder rows.
- Age thresholds: 100 cohort/encoder/threshold rows.
- Full-panel and no-age-auxiliary rank tests: 20 rows.
- Budget-selection endpoints: 180 cohort/budget/selector/endpoint rows, including the random baseline in the CSV.
- Matched auxiliary-survival configurations: 24 rows with endpoint intervals.
- External within-cohort averages: 32 metric rows; auxiliary paired changes: 18 rows.

## Material distinctions retained

1. **Budget age scores are holdout scores.** They are not the primary nested-OOF global age-R². The figures and documentation use `Holdout age-R²`.
2. **Limited labels apply to selection.** The reported performance comes from fixed full-selection-set references, not final models fitted on each small budget.
3. **Historical MIMIC auxiliary Uno’s C mismatch.** For SSL-MAE + age, an earlier draft reported 0.7386, whereas the saved fitted-model audit gives 0.7282897200. For DAE + age, the draft reported 0.7318, whereas the audit gives 0.7140604635. This release retains the artifact values, including their lower point estimates than the corresponding baselines (0.7303191017 and 0.7181054038). It does not assert every auxiliary model improves C. The manuscript itself is not altered by this release.
4. **External diagnostic trade-offs are retained.** SSL-MAE age supervision increases age-R² but reduces average AUROC and AUPRC. CLOCS-style aliases are disclosed; five training seeds do not establish patient-level generalization uncertainty.
5. **Direct 256-D sensitivity is not a finished release result.** Primary runs had outputs, but the budget-reference verification stage was incomplete/failed at snapshot. No partial direct-256D result is mixed with the PCA-32 main evidence here.
6. **Scope is associative and research-only.** No calibrated risk guarantee, prospective clinical utility, causal interpretation or superiority of all metrics is asserted.

## Reproduction boundary

The public functions are newly packaged reference implementations, not a copied version of the private orchestration and all training scripts. Aggregate source hashes support provenance but do not provide access to restricted underlying data. Rebuilding visuals validates presentation consistency; it does not independently re-run the clinical study.
