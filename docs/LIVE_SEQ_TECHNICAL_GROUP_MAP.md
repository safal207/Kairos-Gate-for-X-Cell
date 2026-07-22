# Live-seq technical group map

This layer supports issue #14 by mapping public metadata for the 17-cell recorded cohort.

It reports:

- plate-like prefixes derived from `sample_name`;
- prefixes derived from `original_sample_name`;
- sequencing runs;
- i5 and i7 indexes;
- index pairs;
- published `Date` and `Probe` fields.

## Critical distinction

These are **technical group candidates**, not verified biological replicates.

```text
technical difference != independent experiment
plate label != independent culture
well label != biological replicate
index pair != replicate
cell != independent experimental unit by default
```

The output is intentionally fixed to:

```text
EXPLORATORY_ONLY_TECHNICAL_GROUPING
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

until a pinned publication section, supplementary method, upstream code location, or author clarification establishes the experimental-unit semantics.

## Run

```bash
python scripts/summarize_live_seq_technical_groups.py /path/to/meta.final.csv
```

The script uses the same response-independent cohort rule as the feasibility auditor and does not read `mCherry.log.slope`.

## What can unlock confirmation

A source-backed statement must establish:

1. what physical or experimental unit was independently prepared;
2. which cells share that unit;
3. whether plates or imaging sessions correspond to independent source cultures;
4. whether repeated cells or extractions exist;
5. which unit can be held out without leakage.

Until then, technical groups may support sensitivity analysis only. They may not be presented as evidence of biological generalization.

## Authority

The summary is `RESEARCH_ONLY`. It authorizes no model fitting, biological experiment, clinical use, deployment, or merge.
