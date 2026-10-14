# Aggregate data dictionary

All tables contain experimental aggregates, never patient-level rows. Cohort keys: `CODE` = CODE-15%; `MIMIC` = MIMIC-IV-ECG. Encoder key `SMS` is the historical internal name for the displayed age-auxiliary configuration; `diagnosis` denotes the joint survival/diagnosis-supervised reference.

| File | Grain | Important fields |
|---|---|---|
| `primary.csv` | cohort × encoder | global age-R²; signed full/≥75 Q per 1,000; absolute ≥75 Q; Uno’s C; IBS; horizon |
| `age_thresholds.csv` | cohort × encoder × threshold | threshold in years; signed and absolute Q per 1,000 |
| `rank_agreement.csv` | cohort × threshold × panel | rho; exact unadjusted two-sided p; encoder count; permutation count; exclusion flag |
| `budget_selection.csv` | cohort × budget × selector × endpoint | mean; lower/upper 95% Monte Carlo mean bounds; valid and attempted repetitions |
| `auxiliary_survival.csv` | cohort × SSL method × condition | base/age-supervised Q and C; patient-bootstrap 95% endpoint intervals |
| `external_within_cohort.csv` | method/configuration × metric | equal four-cohort mean; SD across five matched training seeds |
| `external_auxiliary.csv` | SSL method × metric | base/age-supervised mean; paired delta; 95% seed-mean interval; seed count |
| `provenance.json` | source artifact | aggregate-source identities, hashes, transformations and uncertainty definitions |

`Q = 1,000 × (KM observed event risk − mean predicted event risk)`. Positive means risk underestimation. Q units are risk difference per 1,000, not a count of actual events. Uno’s C and probabilities use the unit interval; age-R² may be negative.

`budget` is a fraction (0.05 = 5%). `selected_older_error` is per 1,000; `selected_uno_c` is on the 0–1 scale. `age_r2` in this file is a **holdout** selector. It is not the primary pooled OOF metric. `random` is an exported comparator, omitted from the crowded eight-selector figure only; its rows remain available.

Budgets share fixed references; repeated subgroup thresholds overlap. No row should be treated as an independent patient or as an independent replication. Source-specific uncertainty types must not be interchanged.
