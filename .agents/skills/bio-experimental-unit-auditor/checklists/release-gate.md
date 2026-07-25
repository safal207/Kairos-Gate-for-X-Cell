# Bio Experimental Unit Auditor — Release Gate v0.1

A study audit may be published only when every applicable gate below is satisfied.

## Source integrity

- [ ] Accession and study identity are exact.
- [ ] Retrieval time and evidence references are recorded.
- [ ] Article, supplement, metadata, and correspondence are distinguished.
- [ ] Missing files or unavailable metadata remain explicit.

## Experimental-unit resolution

- [ ] The exposure or intervention contrast is named.
- [ ] The independently assigned or sampled unit is identified, or marked not established.
- [ ] Cells, wells, plates, libraries, lanes, flow cells, runs, and analysis rows are classified separately.
- [ ] Repeated measurements are linked to their parent unit.
- [ ] Independence is never inferred from labels alone.

## Pseudoreplication controls

- [ ] Cell count is not presented as biological replicate count.
- [ ] Plate count is not presented as biological replicate count without F4/F5 evidence.
- [ ] Sequencing runs are treated as technical unless proven biological.
- [ ] Pseudobulk uses a defensible biological grouping key.
- [ ] Leave-one-group-out language matches the actual group semantics.

## Confounder controls

- [ ] Donor/source, day, operator, plate, library, run, imaging, storage, and order are checked.
- [ ] Perfect or near-perfect condition–batch confounding is reported.
- [ ] Unknown graph edges remain unknown.
- [ ] Alternative explanations are listed for high-risk paths.

## Claim firewall

- [ ] Descriptive, association, prediction, generalization, causal, tissue, and clinical claims have separate verdicts.
- [ ] No claim exceeds its evidence level.
- [ ] Lack of biological independence prevents unconditional ACCEPT.
- [ ] Tissue or therapeutic language is blocked without direct supporting evidence.
- [ ] The overall verdict matches the weakest load-bearing claim.

## Safety boundary

- [ ] Audit mode is `computational_only`.
- [ ] `physical_biology_authorized` is false.
- [ ] No operational wet-lab, pathogen, genetic modification, dosing, implantation, or treatment instructions are included.
- [ ] Any proposed physical experiment is routed to an authorized institution with ethics and biosafety review.

## Reproducibility

- [ ] Machine-readable audit conforms to the schema.
- [ ] Positive reference fixture validates.
- [ ] Negative pseudoreplication fixture fails closed.
- [ ] Exact commit and CI result are recorded.

## Verdict

- [ ] `ACCEPT`
- [ ] `ACCEPT_WITH_LIMITS`
- [ ] `HOLD`
- [ ] `BLOCK`

Reviewer note:

```text
Dominant uncertainty:
Evidence needed to resolve it:
Claims currently blocked:
Next valid action:
```
