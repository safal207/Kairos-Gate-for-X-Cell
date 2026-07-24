# Live-seq GSE141064 feasibility audit

This audit checks whether public Live-seq metadata and count-matrix sample IDs can support a future preregistered phase-conditioned benchmark.

It does **not** fit a model, establish causality, validate X-Cell, or authorize biological experimentation.

## Pinned sources

See [`manifests/live-seq-gse141064.sources.v0.1.json`](../manifests/live-seq-gse141064.sources.v0.1.json).

The inspected upstream analysis is pinned to:

```text
DeplanckeLab/Live-seq
6633d4d468f56031ea197474e09921088d878512
```

The upstream software is GPL-3.0. Dataset reuse and redistribution terms are tracked separately and remain an explicit blocking decision.

## Local inputs

Download the published files outside the repository:

```text
GSE141064 metadata or the pinned upstream meta.final.csv
GSE141064_count.final.csv.gz
```

Do not commit source biological data to this repository.

Record the downloaded byte-level SHA-256 digests in the audit output and, after review, in an exact-run evidence manifest.

## Run

```bash
python scripts/audit_live_seq_gse141064.py \
  /path/to/meta.final.csv \
  /path/to/GSE141064_count.final.csv.gz \
  --data-reuse-status unclear
```

The default is deliberately blocked until reuse terms are documented.

After a human provenance review establishes the intended local-analysis and derived-output boundary:

```bash
python scripts/audit_live_seq_gse141064.py \
  /path/to/meta.final.csv \
  /path/to/GSE141064_count.final.csv.gz \
  --data-reuse-status clear
```

The flag records the review decision; it does not grant rights or replace legal terms.

## Cohort rule

The auditor reproduces the narrow recorded-cell rule found in the pinned upstream analysis:

```text
sampling_type == Live_seq
Cell_type == Raw264.7_G9
treatment == not_treated
Batch == 8_8
mCherry.log.intercept > 0
```

Cohort membership is frozen **without consulting `mCherry.log.slope`**. Only after selection does the auditor check whether every selected cell has a finite downstream response label.

This separation prevents the outcome from silently changing the study population. Missing response labels produce `BLOCKED_MISSING_RESPONSE_LABELS`; they do not remove cells from the cohort.

The auditor only reads the count-matrix header. No expression modelling occurs.

## Real-input result

For the pinned inputs audited on July 22, 2026:

```text
metadata rows:                1012
count-matrix sample columns:  1012
identifier sets match:        yes
selected cohort:              17
response-complete cells:      17
missing response labels:      0
declared replicate groups:    0
status:                       BLOCKED_INSUFFICIENT_REPLICATES
```

The exact result is recorded in [`evidence/live-seq-gse141064/feasibility.real.v0.1.json`](../evidence/live-seq-gse141064/feasibility.real.v0.1.json).

## Fail-closed outcomes

```text
READY_FOR_PREREGISTRATION
BLOCKED_MISSING_CELL_LINKAGE
BLOCKED_MISSING_RESPONSE_LABELS
BLOCKED_INSUFFICIENT_REPLICATES
BLOCKED_LICENSE_UNCLEAR
BLOCKED_DATA_INTEGRITY
```

`READY_FOR_PREREGISTRATION` means only that a model protocol may now be frozen before fitting. It does not mean the phase hypothesis is supported.

## Leakage boundary for the next PR

The future real-data protocol must exclude from predictors:

- `mCherry.log.intercept`;
- `mCherry.log.slope`;
- `mCherry.AUC`;
- all post-LPS fields;
- response-derived labels;
- any feature-processing decision fitted using held-out cells.

Repeated measurements or double extractions from one cell must remain in the same split. A replicate-aware split must be fixed before reporting performance.

A random cell split is not accepted as evidence of experimental generalization.

## Authority

All outputs are `RESEARCH_ONLY`. No wet-lab, animal, human, clinical, therapeutic, deployment, approval, ownership, delivery, or merge authority is produced by the audit.
