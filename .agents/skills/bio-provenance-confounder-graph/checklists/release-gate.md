# Bio Provenance Confounder Graph — Release Gate v0.1

## Source freeze

- [ ] Accession, article identifier, retrieval time, and evidence references are recorded.
- [ ] Code commit, workflow, environment, and processed-artifact identity are recorded when available.
- [ ] Author correspondence is identified separately from repository metadata.
- [ ] Missing source material remains explicit.

## Node integrity

- [ ] Every biological source, collection event, derived unit, technical container, library, run, artifact, transformation, output, and claim has a unique node.
- [ ] Unknown events are represented as nodes rather than silently inferred.
- [ ] Identity collisions are resolved or blocked.
- [ ] Every scientific claim has at least one incoming edge.

## Edge integrity

- [ ] Every edge references existing nodes.
- [ ] Every edge has a class, evidence level, status, confidence, and load-bearing flag.
- [ ] Provenance graph is acyclic.
- [ ] Pooling edges retain membership evidence.
- [ ] Transformations identify exact inputs and outputs.
- [ ] Inferred and unknown edges are not represented as observed.

## Confounder graph

- [ ] Donor/source, day, extraction round, operator, plate, library, run, imaging session, storage time, and processing order are evaluated where relevant.
- [ ] Each candidate confounder has both a condition path and an outcome path.
- [ ] Separability is classified as separable, partially separable, aliased, or unknown.
- [ ] Aliased and unknown load-bearing confounders cannot be ignored.
- [ ] Sensitivity analysis is not mislabeled as independent validation.

## Claim reachability

- [ ] Every claim has a reachability row.
- [ ] Complete-path status is accurate.
- [ ] Weakest evidence level is recorded.
- [ ] Unknown-edge count is recorded.
- [ ] High-risk confounders intersecting the claim path are listed.
- [ ] Independent validation is present, absent, or not established.
- [ ] Incomplete claims HOLD or BLOCK.
- [ ] Weak unvalidated F0–F2 claims HOLD or BLOCK.
- [ ] Claims with load-bearing high-risk confounders do not receive unconditional ACCEPT.

## Safety boundary

- [ ] Mode is `computational_only`.
- [ ] `physical_biology_authorized` is false.
- [ ] No operational wet-lab, pathogen, genetic modification, dosing, implantation, or treatment instructions are included.
- [ ] Any physical validation is routed to an authorized institution with ethics and biosafety review.

## Executable contract

- [ ] GSE141064 reference graph validates.
- [ ] Hidden-batch negative fixture fails closed.
- [ ] Exact commit and CI run are recorded.

## Reviewer record

```text
Provenance completeness:
Load-bearing unknown edges:
Aliased or unknown confounders:
Claims accepted with limits:
Claims held or blocked:
Next evidence action:
```
