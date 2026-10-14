# What is reproducible in this public release?

| Level | Included? | Meaning |
|---|---|---|
| Read displayed numeric results | Yes | Aggregate CSVs and provenance are bundled |
| Redraw figures and gallery | Yes | `python scripts/render_results.py` uses those CSVs |
| Recalculate rank statistics | Yes | `python scripts/validate_public_results.py` checks exact permutation results |
| Run reference metrics and probing | Yes | Public implementations and a synthetic example |
| Fit a reference Cox adapter to your own data | Optional | Install survival extras and supply governed inputs/settings |
| Integrate age supervision into your own encoder | Example | Generic optional PyTorch wrapper; not a full training recipe |
| Reproduce the study from raw ECGs | No | Data, linkage, partitions, weights and selected configuration are not released |

Omitted information is not replaced with invented scientific settings. The configuration template contains `null` values for unpublished fields. The synthetic demo has explicitly illustrative settings and generated data. Neither successful tests nor identical chart redraws establish reproduction of patient-level scientific results.

## Bring-your-own-data interface

`crossfit_age(features, ages, patient_groups, alphas=...)` expects aligned arrays. These should remain in a governed environment. Do not add them to this repository. Fit transforms within patient-grouped folds and use a prospectively specified regularization grid.

`subgroup_error(time, event, risk, age, horizon=..., threshold=...)` expects common time units, event indicators in {0,1}, and predicted event probabilities in [0,1]. The horizon must be supported in the subgroup. The helper does not establish censoring independence or clinical validity.

`select_encoder(scores, candidates=..., maximize=...)` requires a finite score for every candidate. It uses only selection scores, with a deterministic lexical tie-break. Evaluation outcomes must not be passed into selection or hyperparameter tuning.

The `survival` extra requires scikit-survival and its platform dependencies. Exact coefficients and patient-specific predictions are not distributed. The public adapter is not a deployment-ready model.

## Intentional omissions

The release excludes raw data, linkage tables, patient identities, patient-level labels/predictions/embeddings, checkpoint weights, private storage locations, original partition manifests, full training settings and original random seeds. Some omissions reflect data restrictions; others are author-selected release scope. We do not claim community or venue rules require withholding training hyperparameters.

If stronger reproducibility is required by a journal or collaborator, provide an approved protocol/configuration supplement and governed data-access path rather than claiming this showcase is a complete reproduction package.
