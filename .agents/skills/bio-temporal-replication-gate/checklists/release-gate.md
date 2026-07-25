# Bio Temporal Replication Gate — Release Gate v0.1

## Frozen target

- [ ] Pre-state measurement is explicit.
- [ ] Stimulus or transition is explicit.
- [ ] Later phenotype is explicit.
- [ ] Same-cell or longitudinal identity requirement is explicit.
- [ ] Biological-unit requirement is explicit.
- [ ] Candidate-only, broader-state, and technical-confounder models are frozen.

## Direct-candidate requirements

- [ ] Molecular pre-state precedes the transition.
- [ ] Phenotype follows the transition.
- [ ] Pre-state and phenotype belong to the same cell or defensible longitudinal unit.
- [ ] Candidate is biologically independent of the target study.
- [ ] Biological units are established above technical containers.
- [ ] Endpoint mapping is compatible and frozen.
- [ ] Technical lineage is not unknown.
- [ ] Evidence level is F3 or stronger.

If any item is false, the candidate is not direct temporal replication.

## Leakage controls

- [ ] Post-stimulation RNA is not called a basal predictor.
- [ ] Different cells are not presented as same-cell longitudinal observations.
- [ ] Same-study evidence is not called external replication.
- [ ] Plates, libraries, lanes, runs, or cell count do not substitute for biological replication.
- [ ] Conceptual replication is not promoted to direct replication.
- [ ] Outcome inspection did not change the endpoint or model plan.

## Gap reporting

- [ ] A missing direct candidate returns `DIRECT_REPLICATION_GAP`.
- [ ] Missing fields are named explicitly.
- [ ] Eligibility standards are not weakened to avoid a gap verdict.
- [ ] Diagnostic reanalysis is not called validation.

## Safety

- [ ] Mode is computational only.
- [ ] Physical biology is not authorized.
- [ ] No operational biological protocol is included.
- [ ] Any future physical validation is routed to a qualified institution.

## Reproducibility

- [ ] Positive gap record validates.
- [ ] Post-stimulation timing-leakage fixture fails closed.
- [ ] Supplementary source identity and checksum are recorded when available.
- [ ] Exact commit and CI result are recorded.
