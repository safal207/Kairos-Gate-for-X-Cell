# Bio Independent Replication Finder — Release Gate v0.1

## Target freeze

- [ ] Target study and accession are exact.
- [ ] The target claim is written before candidate outcomes are inspected.
- [ ] Claim level and current evidence status are explicit.
- [ ] Species, system, phenotype, assay, and required biological unit are recorded or marked unknown.

## Search coverage

- [ ] Repositories and literature sources searched are listed.
- [ ] Search timestamp and query/scope are recorded for completed searches.
- [ ] Related-record and BioProject links are checked.
- [ ] Raw-file, sample-ID, library-ID, and checksum overlap are checked when available.
- [ ] Search limitations are explicit.

## Independence

- [ ] Different accession is not treated as proof of independence.
- [ ] Donor, animal, patient, clone, culture, organoid, tissue, aliquot, and extraction-event overlap are checked.
- [ ] Same-study split accessions are blocked as independent replication.
- [ ] Technical reruns and alternate flow cells are blocked.
- [ ] Reprocessed or derived target data are blocked.
- [ ] Accepted candidates have at least F3 evidence and compatible biological units.

## Compatibility

- [ ] Biological-source independence is assessed separately.
- [ ] Experimental-unit compatibility is assessed separately.
- [ ] Species, biological system, phenotype, assay, time, provenance, and sample size are not collapsed into one opaque score.
- [ ] Direct, conceptual, external-validation, and method-transfer roles are distinguished.
- [ ] Related but non-equivalent systems are not called direct replications.

## Prespecification

- [ ] Primary endpoint is defined before candidate outcome analysis.
- [ ] Expected direction or effect is defined.
- [ ] Biological grouping key is defensible.
- [ ] Exclusion criteria are defined.
- [ ] Success, mixed, and failure criteria are defined.
- [ ] The target is not rewritten after inspecting results.

## Claim gate

- [ ] Discovery alone is not called replication.
- [ ] F5 is used only after a completed prespecified analysis on independent material.
- [ ] No candidate accepted means overall verdict cannot be `ACCEPT_WITH_LIMITS`.
- [ ] Prediction, generalization, causal, tissue, and clinical claims remain bounded to actual evidence.

## Safety

- [ ] Mode is `computational_only`.
- [ ] `physical_biology_authorized` is false.
- [ ] No operational wet-lab or treatment instructions are included.
- [ ] A new physical study is routed through an authorized institution, ethics review, biosafety review, and explicit experimental-unit planning.

## Reproducibility

- [ ] Machine-readable search record validates.
- [ ] Same-study-as-replication negative fixture fails closed.
- [ ] Exact commit and CI run are recorded.

Reviewer note:

```text
Best current candidate:
Independence evidence:
Dominant compatibility gap:
Current verdict:
Next valid action:
```
