# Dataset Readiness Scanner v0.1

## Purpose

The Dataset Readiness Scanner determines whether a versioned dataset contract is technically ready for preregistered modelling before any model is fitted.

It does not evaluate biological truth, treatment efficacy, safety, causality, or clinical usefulness.

## Architecture

```text
source files
  -> dataset-specific adapter
  -> canonical dataset contract
  -> invariant readiness engine
  -> machine-readable verdict
  -> exact-head evidence artifact
```

Dataset-specific column names are permitted only inside adapters. The invariant engine consumes canonical fields:

- metadata identifiers;
- matrix identifiers;
- selected-record flag;
- response availability;
- declared independent unit;
- repeated-measurement identity;
- replicate-semantics classification.

## CLI

```bash
kairos audit-dataset \
  --manifest examples/live-seq-gse141064.dataset-manifest.v0.1.json \
  --metadata meta.final.csv \
  --matrix GSE141064_count.final.csv.gz
```

The command emits JSON and returns:

- `0` for `READY_FOR_PREREGISTRATION`;
- `2` for a scientifically or technically blocked outcome;
- `1` for an invalid manifest, unreadable input, digest mismatch, or other contract failure.

## Outcomes

- `READY_FOR_PREREGISTRATION`
- `EXPLORATORY_ONLY`
- `BLOCKED_DATA_INTEGRITY`
- `BLOCKED_MISSING_CELL_LINKAGE`
- `BLOCKED_MISSING_RESPONSE_LABELS`
- `BLOCKED_REPEATED_CELL_GROUP_LEAKAGE`
- `BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED`
- `BLOCKED_EFFECTIVE_SAMPLE_SIZE`
- `BLOCKED_LICENSE_UNCLEAR`

## Readiness order

The engine fails closed in this order:

1. identifier and canonical-contract integrity;
2. selected-record linkage to the matrix;
3. downstream-label availability without changing cohort membership;
4. repeated-identity leakage across split groups;
5. replicate semantics;
6. effective independent-unit count;
7. reuse terms;
8. bounded ready or exploratory classification.

## Adapter boundary

### `live-seq-gse141064`

Implements the reviewed GSE141064 cohort rule without consulting `mCherry.log.slope` during selection. `Date|Probe` remains a candidate grouping only, and the adapter reports replicate semantics as unresolved.

### `tabular-v0.1`

Uses manifest-provided field mappings and selection rules. It exists both as a reusable adapter and as a proof that the invariant engine is not coupled to Live-seq column names.

The adapter configuration can declare replicate semantics as:

- `verified`;
- `technical_only`;
- `unresolved`.

A technical grouping never unlocks confirmatory readiness.

## Provenance

Every metadata and matrix source must include:

- HTTPS URL;
- source version;
- SHA-256 digest.

Mutable GitHub branch URLs and `latest` aliases fail validation. Input files are hashed before adapter execution.

## Authority boundary

`model_fitting_authorized=true` means only that the declared technical readiness contract passed. It does not authorize:

- wet-lab, animal, or human experiments;
- clinical use;
- therapeutic claims;
- causal claims;
- deployment;
- merge actions.

## Current Live-seq disposition

The reviewed real GSE141064 cohort remains blocked because independent experimental-unit semantics are unresolved. The scanner must not reinterpret plate, index, well, sequencing-run, `Date`, or `Probe` diversity as verified biological replication without source-backed evidence.
