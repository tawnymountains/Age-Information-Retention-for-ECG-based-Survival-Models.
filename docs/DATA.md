# Data access and publication scope

This repository contains **aggregate experimental results** and executable **synthetic-data examples**. It does not redistribute clinical datasets or pretrained weights.

Researchers must obtain the appropriate source data and permissions independently:

- [MIMIC-IV-ECG on PhysioNet](https://physionet.org/content/mimic-iv-ecg/): follow the source's current credentialing and data-use requirements. Associated MIMIC clinical tables and linkage are not included here.
- [CODE-15% original project](https://github.com/antonior92/automatic-ecg-diagnosis): consult original access instructions and the applicable terms. Mortality linkage used in a study must be separately authorized; public waveforms do not imply public death-registry linkage.
- [PTB-XL](https://physionet.org/content/ptb-xl/), and Chapman, Georgia and CPSC: consult each original data source and its terms. This package does not grant additional rights.

Do not upload patient IDs, dates, medical notes, waveforms, embeddings, row-level predictions, credentials or derived linkage keys to a public issue or pull request. Derived arrays are not automatically safe to publish merely because raw waveforms have been removed.

The exported CSVs have encoder/cohort/threshold/condition/selector-level grain. They are not patient records. The release excludes BioRender drawings and other externally licensed manuscript graphics; all bundled plots are generated from the aggregate tables.

Institutional, coauthor, funder and dataset-specific permissions still apply. A repository scanner and aggregate-only export are technical precautions, not legal or ethics certification.
