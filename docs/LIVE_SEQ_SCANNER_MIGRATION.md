# Live-seq Audit to Dataset Readiness Scanner Migration

## Decision

The Dataset Readiness Scanner is the sole implementation of invariant readiness rules for GSE141064.

The historical script remains temporarily as a deprecated compatibility entrypoint. It no longer contains its own cohort, linkage, response, repeated-identity, replicate, licensing, or readiness decision logic.

## Canonical command

```bash
kairos audit-dataset \
  --manifest examples/live-seq-gse141064.dataset-manifest.v0.1.json \
  --metadata meta.final.csv \
  --matrix GSE141064_count.final.csv.gz
```

## Deprecated compatibility command

```bash
python scripts/audit_live_seq_gse141064.py \
  meta.final.csv \
  GSE141064_count.final.csv.gz \
  --data-reuse-status unclear
```

The compatibility command:

- preserves positional arguments and exit codes;
- emits a deprecation notice to standard error;
- builds a bounded manifest for the supplied files;
- delegates adaptation and all readiness decisions to the scanner;
- returns `kairos.dataset-readiness-result.v0.1` on valid inputs;
- returns a machine-readable compatibility error only when the scanner cannot construct a valid result.

It must not acquire independent readiness logic.

## Historical status transition

```text
BLOCKED_INSUFFICIENT_REPLICATES
  -> BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

This is a versioned refinement of the reason for blocking.

It does not mean that:

- the dataset became more ready;
- the dataset became less ready;
- a replicate count was newly measured;
- plate, index, sequencing-run, `Date`, or `Probe` labels became biological replicates;
- modelling or experiments were authorized.

The new status is more precise because the missing evidence concerns the semantics of independent experimental units, not merely a numeric count.

## Evidence preservation

The historical snapshot remains unchanged at:

```text
evidence/live-seq-gse141064/feasibility.real.v0.1.json
```

Its supersession is recorded additively at:

```text
evidence/live-seq-gse141064/feasibility.supersession.v0.2.json
```

The migration workflow binds:

- exact head SHA;
- Git tree SHA;
- exact Scanner PR #18 stack base;
- pinned metadata and matrix digests;
- historical snapshot digest;
- supersession-record digest;
- canonical scanner-result digest;
- compatibility-result digest.

Historical commits and old artifacts are not rewritten or deleted.

## Required equivalence

Before the compatibility shim can be removed, exact-head CI must prove:

```text
metadata identifiers:                1012
matrix identifiers:                  1012
full identifier sets match:          true
selected sample IDs:                 exact historical list of 17
response-complete records:           17
missing selected IDs:                0
cross-group repeated identities:     0
independent-unit semantics:          unresolved
preregistration gate:                false
all action-authority fields:         false
```

The compatibility result and canonical scanner result must contain the same selected sample IDs and the same current blocked status.

## Workflow consolidation

`.github/workflows/live-seq-real-data.yml` is the canonical real-input workflow.

The separate `dataset-readiness-real.yml` workflow is removed to prevent duplicated downloads, assertions, and evidence paths. The retained workflow invokes `kairos audit-dataset` and checks compatibility equivalence as a bounded migration assertion.

## Removal criteria for the shim

The deprecated script may be removed only after:

1. no supported automation or documentation calls it;
2. the canonical workflow has remained green on exact-head public inputs;
3. equivalent or stronger scanner regressions cover all prior failure modes;
4. a removal note is added to the changelog;
5. historical evidence references remain resolvable.

## Authority boundary

The migration does not fit a model or estimate an effect.

Every result keeps the following false:

```text
model_fitting_authorized
experiment_authorization
clinical_authorization
merge_authorization
```

BioNeMo and Geneformer remain downstream and blocked until a separate source-backed readiness gate passes.
