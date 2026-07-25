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

Rejects same-study material, technical reruns, shared biological material, and reprocessed target data as independent replication.

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

## Independent conceptual candidate: GSE94383

The exact public dynamics and expression tables contain the same 823 unique cell IDs.

| Metric | Value |
|---|---:|
| Spearman rho | **0.178** |
| Bootstrap 95% CI | **0.110 to 0.243** |
| Stratified permutation p | **0.0002** |
| Leave-one-ID-prefix-out rho range | **0.153 to 0.200** |

```text
CONCEPTUAL_SIGNAL_SUPPORTED
```

This supports weak but stable independent pathway coupling. It is not direct temporal replication because RNA is measured after stimulation rather than before a future `Tnf-mCherry` phenotype.

## Current causal boundary

```text
RANKED_NOT_IDENTIFIED
DIRECT_REPLICATION_GAP
TOP_DISCOVERY_CANDIDATE_NOT_STABLE_UNIQUE_DRIVER
```

The leading current explanation is a broader shared upstream cellular state. `Nfkbia` remains a useful discovery candidate, not an identified unique causal driver.

## Partner-laboratory evidence boundary

```text
READY_FOR_PARTNER_SCIENTIFIC_REVIEW
PHYSICAL_EXECUTION_NOT_AUTHORIZED
AI_DOES_NOT_AUTHORIZE_EXECUTION
```

Scientific-review readiness does not authorize physical work. Any future validation must be designed and governed by a competent institution under all applicable scientific, ethical, biosafety, legal, quality, consent, containment, and data-governance requirements.

## Validation

Foundation checks:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m kairos_gate examples/phase-conditioned-transition.json
python scripts/validate_handoff.py examples/tip-kairos-handoff.json
python scripts/run_phase_benchmark.py testdata/phase-window-tiny.json
```

BioEvidence contract checks:

```bash
python scripts/validate_experimental_unit_audit.py examples/gse141064.experimental-unit-audit.json
python scripts/validate_provenance_confounder_graph.py examples/gse141064.provenance-confounder-graph.json
python scripts/validate_independent_replication_search.py examples/gse141064.independent-replication-search.json
python scripts/validate_causal_hypothesis_ranking.py examples/gse141064.nfkbia-causal-hypotheses.json
python scripts/validate_temporal_replication_gate.py examples/gse141064.temporal-replication-gate.json
python scripts/validate_partner_lab_evidence_handoff.py examples/gse141064.nfkbia-partner-lab-handoff.json
```

## Safety boundary

Kairos Gate does not claim to:

- reverse aging;
- provide medical advice, diagnosis, treatment, or patient-level decisions;
- establish that meditation, sound, music, intention, or an undefined information field directly reprograms cells;
- prove biological safety from transcriptomic prediction;
- authorize wet-lab, animal, or human experimentation;
- represent or speak for Xaira Therapeutics, the X-Cell authors, or the Live-seq authors.

The repository is licensed under MIT. Citation metadata is provided in `CITATION.cff`.
