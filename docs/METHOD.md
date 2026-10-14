# Method and interfaces

## Three different questions

1. **Representation measurement:** how much chronological-age information can a fixed linear probe decode from a frozen ECG representation?
2. **Survival evaluation:** how does absolute-risk error in older patients relate to this measurement across candidate encoders?
3. **Selection and training:** can age-based scoring support encoder selection, and can auxiliary age supervision change learned representations?

The association between age-R² and subgroup error is empirical, not a proof that increasing this metric must improve every risk model. Global mean-risk agreement is not a complete characterization of calibration over the risk range.

## Global age-R²

For held-out predictions from patient-grouped outer folds:

```text
global age-R² = 1 - sum_i(age_i - predicted_age_i)^2
                    / sum_i(age_i - mean(age))^2
```

Pool the out-of-fold predictions before calculating R². Do not average fold R² values. The metric can be negative. All ECGs belonging to the same patient stay in the same fold. Fit standardization and Ridge within training folds; select regularization using inner folds only. `crossfit_age` implements this reference design and requires a user-supplied regularization grid. Exact study partitions and training configuration are not supplied.

## Primary survival evaluation

The survival encoders are trained on CODE-15% and frozen. Their representations are used for independently fitted cohort-specific Cox models; MIMIC is not a transfer of a fitted CODE Cox model. The four external diagnostic cohorts have a different within-cohort training design described below.

- Representation: 256 dimensions.
- Primary readout family: standardize → PCA-32 → standardize → penalized Cox.
- Fit transforms and Cox only on the designated development population.
- Evaluate on an independent population.
- Horizons: CODE-15%, 5 years; MIMIC-IV-ECG, 90 days.
- Chronological age is not an input to the ECG-only primary readout.
- The primary CODE Cox fit uses combined encoder-training and validation populations; budget reference fits use the full selection population instead. Do not interchange their endpoints.

The optional `fit_cox_reference` exposes the readout family. Solver settings and penalty must be supplied explicitly. Its deterministic full-SVD PCA is a public adapter, not a claim of bit-exact equivalence to the private implementation. Numerical convergence, follow-up support and censoring assumptions require additional evaluation in a real study.

## Signed subgroup mean-risk error

```text
Q_tau(H) = 1000 * [1 - KM_tau(H) - mean(predicted_event_risk_H | age >= tau)]
```

Positive Q indicates underestimation; negative Q indicates overestimation. `|Q|` ignores direction. The observed risk is Kaplan–Meier-based, not the raw proportion dying before H. Patient-level clinical interpretation also depends on censoring and risk-model assumptions. The public helper rejects unsupported horizons rather than extrapolating KM beyond observed follow-up.

## Rank agreement

```text
rho_agree = Spearman(global_age_R2, -absolute_subgroup_Q)
```

Higher age-R² and lower |Q| therefore have positive agreement. The main analysis uses ten encoders. Omitting age-auxiliary leaves nine, including the diagnosis-supervised reference. Exact two-sided p-values exhaust permutations of pairings; they are unadjusted exploratory tests. Age-threshold subgroups overlap and are not independent replications.

## Budgeted encoder selection

Each sampled budget is divided into fitting and scoring patients. Scores are used to select a candidate; independent evaluation endpoints are then read from fixed reference models fitted on the full selection set. The budget is not a restriction on final reference-model fitting.

The available age selector computes holdout age-R². The public release does not relabel it as nested-OOF global age-R². At an incomplete repetition, a selector requiring every candidate score is not evaluated; `n_valid` is exported alongside `n_attempted=50`. CI widths describe Monte Carlo variation of the selection procedure conditional on fixed model/evaluation data. A zero-width interval can occur when the same model is chosen every time; it is not zero patient-level uncertainty.

MIMIC diagnosis selection uses six targets from machine-generated reports. Uncertain statements are masked per label. These labels are not adjudicated diagnostic ground truth. At 5% budget, the MIMIC diagnostic selectors have 47 valid repetitions out of 50; CODE diagnostic selectors have 44/50. Other invalid repetitions are retained in the denominators rather than hidden.

## Auxiliary supervision and inference

```text
training_loss = original_SL_or_SSL_loss + age_weight * auxiliary_age_loss
```

`AgeAuxiliary` accepts an arbitrary supplied encoder; it is not restricted to a supervised objective. The wrapper illustrates integration only; it does not implement six complete SSL algorithms. The auxiliary head is discarded for ECG-only inference. Adding chronological age to downstream Cox inputs is a separate option that requires age at inference. It is neither implied nor required by the training-only auxiliary head.

The exported auxiliary survival rows contain both original and age-supervised configurations for every method. Patient-bootstrap endpoint CIs are conditional on fixed fitted models; inference about paired differences requires paired-difference intervals, not overlap of these endpoint CIs.

## External within-cohort experiments

PTB-XL, Chapman, Georgia and CPSC encoders were trained separately within each cohort and frozen for age and diagnostic probing. No survival outcome is asserted for these analyses. Table summaries weight the four cohorts equally, then summarize five matched training seeds.

- Table-I-style evidence has eight configurations, not the ten survival encoders: it excludes the survival-only and Mean-Teacher survival configurations.
- The CLOCS-style single-record fallback in Chapman, Georgia and CPSC uses the SimCLR construction. Those conditions are aliases, not independent runs.
- One Georgia DAE baseline seed had negative age-R² and did not outperform the age-label permutation null; it is retained in aggregates.
- Native patient IDs were available for PTB-XL. Other cohorts used available record identities plus exact duplicate-waveform grouping; longitudinal identity was not independently established.
- Sparse diagnostic classes limit interpretation. Diagnostic gains are not universal: the paired SSL-MAE AUROC and AUPRC changes are negative.

No average in this release should be interpreted as a pooled, patient-weighted, cross-cohort clinical validation.
