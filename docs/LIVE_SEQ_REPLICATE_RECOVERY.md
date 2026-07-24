# Live-seq replicate recovery boundary

## Current result

The pinned GSE141064 inputs pass exact metadata-to-count-matrix linkage and recover 17 recorded Raw264.7_G9 cells with downstream response measurements.

The current feasibility status is:

```text
BLOCKED_INSUFFICIENT_REPLICATES
```

This is a scientific design blocker, not a technical pipeline failure.

## What is missing

For the selected recorded-cell cohort, the metadata fields used by the v0.1 protocol for declared replicate grouping (`Date` and `Probe`) are empty. Sample names contain plate-like identifiers, but the repository and publication have not yet been shown to define those plates as independent biological or experimental replicates.

A plate identifier must not be silently promoted into a biological replicate.

## Allowed next investigation

1. Trace the 17 selected cells through the pinned upstream analysis and supplementary methods.
2. Determine the documented meaning of `plate1` through `plate5`, `exp8_*`, index pairs, and imaging runs.
3. Check whether any cells share a source culture, imaging session, plate, extraction event, or repeated-cell identity.
4. Establish whether a leave-one-group-out design has a scientifically defensible grouping unit.
5. Record the source and exact quotation or code location supporting that interpretation.
6. Ask the dataset authors only if the public materials do not resolve the grouping semantics.

## Forbidden shortcuts

- Do not use a random cell split as confirmation of generalization.
- Do not call technical wells or sequencing indexes biological replicates.
- Do not select the grouping rule after observing model performance.
- Do not merge Fucci cells with Live-seq cells without an exact per-cell mapping.
- Do not claim timing causality from a predictive association.

## Possible outcomes

```text
REPLICATE_GROUPING_VERIFIED
EXPLORATORY_ONLY_TECHNICAL_GROUPING
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
BLOCKED_EFFECTIVE_SAMPLE_SIZE
```

Only `REPLICATE_GROUPING_VERIFIED` can unlock a confirmatory preregistration. An exploratory technical grouping must remain explicitly labelled exploratory.

## Authority boundary

This investigation is research-only. It does not authorize biological experiments, clinical use, therapeutic claims, deployment, or merge actions.
