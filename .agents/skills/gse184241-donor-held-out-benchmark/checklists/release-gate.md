# Release gate

A benchmark artifact is releasable only when every item passes.

## Input identity

- [ ] Official GSE184241 processed-count URL recorded.
- [ ] Official barcode-workbook URL recorded.
- [ ] SHA-256 recorded for both files.
- [ ] Count-matrix cell IDs exactly match barcode `Sample_ID` values.
- [ ] Plate-to-donor and visit-to-time mappings are frozen from GEO metadata.

## Biological-unit firewall

- [ ] Biological grouping unit is donor.
- [ ] Exactly three leave-one-donor-out folds exist.
- [ ] No cell-random split is permitted.
- [ ] Held-out donor is absent from feature selection, scaling, PCA, tuning, calibration, and threshold selection.
- [ ] Cell-level metrics are not described as independent biological replication.

## Model comparison

- [ ] Prevalence baseline present.
- [ ] Visit-metadata baseline present.
- [ ] `NFKBIA`-only baseline present.
- [ ] Frozen inflammatory panel present.
- [ ] Train-donor-only PCA state present.
- [ ] Metadata-plus-state baseline present.
- [ ] Metrics reported per donor and macro-averaged.
- [ ] Hyperparameters are frozen or nested entirely inside training donors.

## Geneformer boundary

- [ ] Status is either exact-passported execution or `GENEFORMER_RUNTIME_HOLD`.
- [ ] Any executed model has exact checkpoint and runtime.
- [ ] Input conversion and cell-order hashes are preserved.
- [ ] Embedding artifact and hash are preserved.
- [ ] Training-overlap status is visible.
- [ ] Same donor folds are used for Geneformer and baselines.

## Claims and safety

- [ ] Same-cell future-response prediction remains blocked.
- [ ] `NFKBIA`-specific effect remains unestablished unless separately identified.
- [ ] Causal, clinical, and therapeutic claims remain blocked.
- [ ] No physical biological execution is authorized.
- [ ] Exact-head CI and retained artifacts are linked.
