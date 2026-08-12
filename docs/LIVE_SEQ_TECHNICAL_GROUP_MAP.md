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

These fields are **technical group candidates**. Public metadata alone do not establish biological replicate semantics.

```text
technical difference != independent experiment
plate label != independent culture
well label != biological replicate
index pair != replicate
```

The metadata-only output intentionally remains:

```text
EXPLORATORY_ONLY_TECHNICAL_GROUPING
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

because the CSV itself does not encode the missing experimental-unit semantics.

## External semantics overlay

On 2026-08-12, private researcher correspondence supplied contextual clarification for the narrow **cell-heterogeneity** question. That information is recorded separately in:

- [`LIVE_SEQ_REPLICATE_SEMANTICS.md`](LIVE_SEQ_REPLICATE_SEMANTICS.md)
- [`../evidence/live-seq-gse141064/replicate-semantics.external.v0.1.json`](../evidence/live-seq-gse141064/replicate-semantics.external.v0.1.json)

The clarified working semantics are:

```text
for cell heterogeneity:
  cell = biological replicate
  plate = sub-batch
```

This does **not** make plate an independent biological replicate and does not establish a held-out biological generalization unit.

Keeping this clarification separate from the metadata summary is intentional: correspondence-derived semantics must not be rewritten as if they were derivable from the CSV.

## Run

```bash
python scripts/summarize_live_seq_technical_groups.py /path/to/meta.final.csv
```

The script uses the same response-independent cohort rule as the feasibility auditor and does not read `mCherry.log.slope`.

## What remains blocked

The external clarification resolves the cell-level heterogeneity replicate question, but it does not establish:

1. an independent culture/day/donor/animal or equivalent held-out biological unit;
2. plate as an independent biological replicate;
3. a leakage-safe unit for claims of biological generalization.

Therefore plate-based holdout may be used only as a technical/sensitivity analysis unless further source-backed evidence establishes stronger semantics.

The next discriminating step is to quantify whether plate-associated variation is negligible. If it is material, plate must be modeled, stratified, or sensitivity-checked explicitly; if it is negligible, it can be treated as a minor sub-batch nuisance factor for the cell-heterogeneity analysis.

## Authority

The summary and semantics overlay are `RESEARCH_ONLY`. They authorize no biological experiment, clinical use, deployment, causal claim, or automatic merge.
