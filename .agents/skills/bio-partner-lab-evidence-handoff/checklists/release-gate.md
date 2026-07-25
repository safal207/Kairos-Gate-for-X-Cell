# Partner Laboratory Evidence Handoff — Release Gate v0.1

A handoff may be marked `READY_FOR_PARTNER_SCIENTIFIC_REVIEW` only when every applicable gate passes.

## Evidence package

- [ ] Frozen evidence question is explicit.
- [ ] Current supporting, limiting, blocking, and negative evidence is preserved.
- [ ] At least two serious competing hypotheses are included.
- [ ] Every hypothesis has a distinguishing observation.
- [ ] The package does not represent a rank as causal identification.

## Experimental units

- [ ] Biological experimental unit is defined before outcome analysis.
- [ ] Assignment or sampling occurs at the biological-unit level.
- [ ] Source-to-unit-to-cell lineage is required.
- [ ] Cells, wells, plates, libraries, runs, reads, and image frames are not treated as biological replicates.
- [ ] The partner must provide a prospective precision or power justification.

## Timing and identity

- [ ] Molecular pre-state precedes the transition.
- [ ] Later phenotype follows the transition.
- [ ] Both measurements link to the same cell or defensible longitudinal unit.
- [ ] The full lineage is machine-auditable.
- [ ] Broken identity or reversed timing triggers `HOLD`.

## Analysis contract

- [ ] Candidate-only model is prespecified.
- [ ] Broader baseline-state model is prespecified.
- [ ] Technical-confounder model is prespecified.
- [ ] Combined model is prespecified.
- [ ] Null or negative-control model is prespecified.
- [ ] Model families are frozen before outcome inspection.
- [ ] Changes require a versioned superseding record.

## Data return

- [ ] Returned data are machine-readable and lawful.
- [ ] Biological and technical lineage is preserved.
- [ ] Timing, missingness, exclusions, and deviations are preserved.
- [ ] Transform and normalization provenance is preserved.
- [ ] Model inputs, outputs, diagnostics, and uncertainty are preserved.
- [ ] Source files and derived artifacts have checksums.

## Decision matrix

- [ ] Shared-state interpretation is covered.
- [ ] Direct-effect interpretation is covered.
- [ ] Marker-only interpretation is covered.
- [ ] Technical-confounding interpretation is covered.
- [ ] Small context-specific effect is covered.
- [ ] Null or instability is covered.
- [ ] Every outcome has an interpretation limit.

## Governance

- [ ] Partner institution determines applicable approvals.
- [ ] Qualified principal investigator is required.
- [ ] Domain biology review is required.
- [ ] Quantitative review is required.
- [ ] Biosafety, ethics, and data-governance reviews are required when applicable.
- [ ] `execution_authorized` is false.
- [ ] AI approval is never represented as institutional authorization.

## Safety and claims

- [ ] No physical protocol is included.
- [ ] No recipes, concentrations, dosing, treatment, modification, infection, implantation, or human-experiment instructions are included.
- [ ] Physical biology remains unauthorized.
- [ ] Causal claim remains not established or blocked.
- [ ] Tissue claim is blocked.
- [ ] Clinical and therapeutic claims are blocked.

## Reproducibility

- [ ] Record conforms to the machine-readable schema.
- [ ] Positive reference handoff validates.
- [ ] False authorization fixture fails closed.
- [ ] Exact commit and CI run are recorded.

## Verdict

- [ ] `READY_FOR_PARTNER_SCIENTIFIC_REVIEW`
- [ ] `HOLD`
- [ ] `BLOCK`

Reviewer note:

```text
Evidence question:
Independent biological unit:
Hypotheses to distinguish:
Required returned evidence:
Why execution is not authorized:
Claims still blocked:
```
