# Next Evidence Planner v0.1

## Purpose

The Next Evidence Planner converts a validated Dataset Readiness result into a bounded, machine-readable description of the evidence still required to change the current decision.

It does not infer missing facts, accept evidence, contact authors, or change the readiness verdict.

## CLI

```bash
kairos plan-next-evidence \
  --result examples/live-seq-gse141064.readiness-result.v0.1.json
```

The command emits:

```text
kairos.evidence-request-plan.v0.1
```

A successful plan generation returns exit code `0`. Invalid or unsupported readiness results fail closed with exit code `1`.

## v0.1 supported states

- `BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED`;
- `READY_FOR_PREREGISTRATION`.

Other readiness statuses are intentionally rejected until a reviewed evidence template exists for them.

## Live-seq evidence request

For GSE141064, the planner requires source-backed answers for:

1. the independent experimental-unit definition;
2. the exact mapping of all selected sample IDs to units;
3. shared culture, day, imaging, extraction, and repeated-measurement dependencies;
4. the semantics of plate, well, index, sequencing-run, `Date`, `Probe`, and sample-name labels;
5. the effective independent-unit count after dependency grouping;
6. a scientifically defensible held-out split defined before model fitting.

Every item remains blocking until its minimum content is present in an acceptable evidence source.

## Acceptable evidence classes

- public author clarification;
- immutable supplementary methods;
- pinned protocol;
- machine-readable metadata with explicit semantics;
- versioned lab documentation.

A source class is not accepted merely because it exists. The supplied material must answer the requirement and be linked to the exact dataset and cohort.

## Forbidden substitutions

The plan explicitly rejects:

- technical-label diversity without source-backed semantics;
- individual cells counted as independent replicates without evidence;
- random cell splits presented as generalization evidence;
- grouping selected after viewing responses or model performance;
- sample-name pattern inference by itself;
- synthetic or foundation-model output used as replicate evidence.

## Decision mapping

```text
complete source-backed semantics + sufficient units
  -> REPLICATE_GROUPING_VERIFIED

source-backed semantics + too few units
  -> BLOCKED_EFFECTIVE_SAMPLE_SIZE

technical grouping only
  -> EXPLORATORY_ONLY_TECHNICAL_GROUPING

missing, incomplete, or contradictory semantics
  -> BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

The mapping describes possible future dispositions. Generating the plan does not apply any disposition.

## Result binding

The plan records the SHA-256 digest of the exact readiness-result file used as input. This prevents a plan generated for one result from being silently attached to another dataset state.

The committed Live-seq pair is:

```text
examples/live-seq-gse141064.readiness-result.v0.1.json
examples/live-seq-gse141064.evidence-request-plan.v0.1.json
```

## Authority boundary

All plans keep the following false:

```text
readiness_verdict_changed
model_fitting_authorized
author_contact_authorized
experiment_authorization
clinical_authorization
merge_authorization
```

A human may independently decide to contact an author, review evidence, preregister a model, or merge code. The planner itself grants none of those permissions.
