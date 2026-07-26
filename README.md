# Kairos Gate for X-Cell

**Research-only protocol for phase-conditioned cellular transition assessment and bounded biological evidence governance.**

Kairos Gate asks two linked questions:

1. Is a measurable pre-intervention phase a useful predictive context for a proposed cellular transition?
2. Is the evidence package strong enough to support the exact claim being made without pseudoreplication, broken provenance, temporal leakage, or unauthorized escalation?

> Every output is a research classification. It is not permission to conduct biological work or make a clinical decision.

## Project steward

**Alexey (Alex Lim, [@safal207](https://github.com/safal207)) — founder and evidence-systems builder.**

Alexey contributes QA, product thinking, causal and evidence architecture, reproducibility, traceability, and governance. He does not present himself as a biologist or clinician and does not authorize experiments or treatment.

Project navigation:

- [`MASTER_ROADMAP.md`](MASTER_ROADMAP.md) — direction, milestones, gates, and deferred work;
- [`BACKLOG.md`](BACKLOG.md) — ordered execution queue and definitions of done;
- [Epic #24](https://github.com/safal207/Kairos-Gate-for-X-Cell/issues/24) — canonical GitHub roadmap.

## Kairos transition foundation

The v0.1 foundation contains:

- a strict Draft 2020-12 transition schema;
- complete date-time and pre-intervention phase validation;
- hard identity, toxicity, and reversibility exclusions;
- deterministic research-only classifications;
- a synthetic phase-ablation and phase-shuffle benchmark;
- a versioned TIP-to-Kairos handoff;
- exact-head CI evidence and installed-wheel validation;
- FAIR-oriented model, data, reproducibility, causal, and safety documentation.

Research-only classifications:

- `CANDIDATE_WINDOW`;
- `WAIT`;
- `EXCLUDE`;
- `INSUFFICIENT_EVIDENCE`.

Hard exclusions take precedence over missing evidence. A known high-risk record cannot be softened into `INSUFFICIENT_EVIDENCE`.

## Biological evidence stack v0.1

### 1. `bio-experimental-unit-auditor`

Separates biological units from cells, wells, plates, libraries, runs, and analysis rows. It reconstructs source lineage and blocks pseudoreplication when biological independence is not established.

### 2. `bio-provenance-confounder-graph`

Preserves source-to-claim paths, unresolved events, identity collisions, confounders, and broken lineage rather than hiding them behind a final score.

### 3. `bio-independent-replication-finder`

Rejects same-study material, technical reruns, shared biological material, unresolved independent units, and reprocessed target data as accepted replication.

### 4. `bio-causal-hypothesis-ranker`

Compares direct effects, shared state, marker-only explanations, technical confounding, selection bias, small effects, chance, and overfitting without translating rank into causal identification.

### 5. `bio-temporal-replication-gate`

Requires the molecular pre-state to precede the transition and the later phenotype to remain linked to the same cell or defensible longitudinal unit.

### 6. `bio-partner-lab-evidence-handoff`

Converts a documented public-data gap into a bounded scientific-review package for a qualified institution. It contains no physical biological procedure and grants no execution authority.

All six skills are computational and documentary only.

## Reference case: GSE141064 Batch 8_8

The public metadata and count matrix have exact 1,012-to-1,012 identifier linkage. A response-independent rule recovers 17 recorded Raw264.7_G9 cells with complete downstream response labels.

Current result:

```text
BLOCKED_INSUFFICIENT_REPLICATES
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

Publicly available evidence shows plate-like labels, one `exp8` experiment prefix, one sequencing run, and unique index pairs. It does **not** currently establish independent biological cultures, collection days, or imaging sessions for these 17 cells.

The author-clarification request remains open in `DeplanckeLab/Live-seq#9`. Until source-backed clarification arrives:

- exploratory cell-level description is allowed with limits;
- leave-one-plate-out remains a technical sensitivity analysis;
- plate-based biological pseudobulk is blocked;
- prediction on new biological units is not established;
- causal, tissue, clinical, and therapeutic claims remain blocked.

## Descriptive pathway context: GSE94383

The exact public dynamics and expression tables contain the same 823 unique cell IDs. A weak positive direction is visible within the matched table:

| Metric | Value | Evidence use |
|---|---:|---|
| Spearman rho | **0.178** | observed within-table association |
| Cell-level bootstrap interval | **0.110 to 0.243** | descriptive sensitivity only |
| Cell-level permutation score | **0.0002** | non-inferential while biological N is unresolved |
| Leave-one-ID-prefix-out rho range | **0.153 to 0.200** | technical sensitivity only |

```text
DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED
INDEPENDENT_BIOLOGICAL_UNIT_UNRESOLVED
REPLICATION_STATUS_HOLD
```

The 823 cells are observations, not 823 independent biological replicates. ID-prefix semantics and effective biological N remain unresolved. Cell-level intervals, permutation scores, and prefix exclusion cannot promote the result to independent biological support, conceptual triangulation, replication, or generalization. RNA is also measured after stimulation rather than before a future `Tnf-mCherry` phenotype.

## Current causal boundary

```text
RANKED_NOT_IDENTIFIED
DIRECT_REPLICATION_GAP
TOP_DISCOVERY_CANDIDATE_NOT_STABLE_UNIQUE_DRIVER
```

The leading current explanation is a broader shared upstream cellular state. `Nfkbia` remains a useful discovery candidate, not an identified unique causal driver. GSE94383 contributes descriptive pathway context only and does not satisfy the independent-validation gate.

## Partner-laboratory evidence boundary

```text
READY_FOR_PARTNER_SCIENTIFIC_REVIEW
PHYSICAL_EXECUTION_NOT_AUTHORIZED
AI_DOES_NOT_AUTHORIZE_EXECUTION
```

Scientific-review readiness does not authorize physical work. Any future validation must be designed and governed by a competent institution under all applicable scientific, ethical, biosafety, legal, quality, consent, containment, and data-governance requirements.

## v0.2 preview.4: AI-designed molecule claim auditor

Issue [#47](https://github.com/safal207/Kairos-Gate-for-X-Cell/issues/47) introduces a separate preview contract for auditing the path from generative molecular design to public claims.

The second flagship case is the 2026 SynTnpB study in *Science* (`10.1126/science.aed6123`):

```text
AI proposal
  -> generated candidate space
  -> candidate-stage reconciliation
  -> selected variants
  -> reported cellular activity
  -> deposited structural record
  -> safety and application claims
```

Current bounded verdict:

```text
SYN_TNPB_ACTIVITY = SUPPORTED_WITH_LIMITS
WILD_TYPE_TNPB_COMPARATOR_SUPERIORITY = SUPPORTED_WITH_LIMITS
SELECTED_STRUCTURE = SUPPORTED_WITH_LIMITS
UNIVERSAL_CRISPR_SUPERIORITY = BLOCKED
CLINICAL_OR_AGRICULTURAL_READINESS = NOT_ESTABLISHED
INDEPENDENT_REPLICATION = NOT_ASSESSED
PHYSICAL_EXECUTION = NOT_AUTHORIZED
```

### Evidence authority

The preview does not equate publication with executable replication:

```text
F2 = peer-reviewed or repository-reported observation
F3 = digested executable analysis or reproducibility bundle
F4 = deposited repository record or explicit author/laboratory confirmation
F5 = frozen unrelated-laboratory replication or risk evidence
```

The public functional statements in the SynTnpB reference record are classified as **F2**, not F3. The deposited RCSB structure `9YYG` is represented as F4 structural evidence. Independent replication remains unestablished because no provenance-bearing F5 unrelated-laboratory evidence object is registered.

### Fail-closed additions in preview.4

- publication reporting cannot be mislabeled as F3 or F4;
- replication references must resolve to external provenance-bearing evidence objects;
- established replication requires F5 and matching unrelated-laboratory identity, materials, unit, endpoint, and artifact kind;
- platform generalization requires matching F5 evidence and broad coverage across targets, laboratories, delivery systems, organisms, and populations;
- a complete denominator must reconcile generated, excluded, screened, failed, and selected candidates;
- known partial counts must remain physically possible, including `screened <= generated` and `selected <= screened`;
- cryo-EM evidence is structurally bound and cannot be relabeled as delivery, toxicity, or another risk endpoint;
- cellular activity assays cannot silently become safety or structural evidence;
- F5 artifact kinds must agree with their declared external evidence kinds;
- established risk dimensions require external risk-assessment evidence with matching endpoints and defined minimum levels;
- one generated mutation suite currently exercises 13 normative negative paths;
- the exact-head receipt hashes every audit included in the positive result.

This preview is stacked on the hardened schema-first authority and is not part of the v0.1 release claim. It contains no sequences, physical procedures, delivery instructions, or experimental authorization.

## Validation

Foundation checks:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m kairos_gate examples/phase-conditioned-transition.json
python scripts/validate_handoff.py examples/tip-kairos-handoff.json
python scripts/run_phase_benchmark.py testdata/phase-window-tiny.json
```

BioEvidence records must use the canonical schema-first gateway:

```bash
python scripts/validate_bioevidence_contract.py experimental-unit examples/gse141064.experimental-unit-audit.json
python scripts/validate_bioevidence_contract.py provenance-confounder examples/gse141064.provenance-confounder-graph.json
python scripts/validate_bioevidence_contract.py independent-replication examples/gse141064.independent-replication-search.json
python scripts/validate_bioevidence_contract.py causal-hypothesis examples/gse141064.nfkbia-causal-hypotheses.json
python scripts/validate_bioevidence_contract.py temporal-replication examples/gse141064.temporal-replication-gate.json
python scripts/validate_bioevidence_contract.py partner-handoff examples/gse141064.nfkbia-partner-lab-handoff.json
python scripts/validate_bioevidence_contract.py ai-designed-molecule examples/syntnpb-2026.ai-designed-molecule-claim-audit.json
python scripts/run_ai_designed_molecule_regressions.py
```

The gateway applies the public Draft 2020-12 schema and format checks before semantic validation. Direct semantic scripts are implementation details and cannot override schema invalidity.

## Safety boundary

Kairos Gate does not claim to:

- reverse aging;
- provide medical advice, diagnosis, treatment, or patient-level decisions;
- establish that meditation, sound, music, intention, or an undefined information field directly reprograms cells;
- prove biological safety from transcriptomic prediction;
- authorize wet-lab, animal, agricultural-field, or human experimentation;
- represent or speak for Xaira Therapeutics, the X-Cell authors, the Live-seq authors, the SynTnpB authors, or their institutions.

The repository is licensed under MIT. Citation metadata is provided in `CITATION.cff`.
