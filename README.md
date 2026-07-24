# Kairos Gate for X-Cell

**Research-only protocol and evidence-governance layer for phase-conditioned cellular transition assessment.**

X-Cell asks what a perturbation may cause. Kairos Gate asks **when** a predicted transition is sufficiently supported for further research while preserving experimental-unit identity, provenance, uncertainty, and claim boundaries.

> `CANDIDATE_WINDOW`, `CONCEPTUAL_SIGNAL_SUPPORTED`, and `READY_FOR_PARTNER_SCIENTIFIC_REVIEW` are research classifications. They are not biological, experimental, clinical, treatment, deployment, or merge authorization.

## Project steward

> **Alexey (Alex Lim, [@safal207](https://github.com/safal207)) — founder and evidence-systems builder**
>
> QA engineer, AI-product builder, and entrepreneur focused on turning uncertain, high-stakes ideas into testable protocols, traceable artifacts, and bounded decisions.
>
> **Mission:** build trustworthy infrastructure for agentic science where models may propose possibilities, but evidence contracts and authorized humans determine what is supported and what may proceed.
>
> **Role boundary:** Alexey does not present himself as a biologist or clinician and does not authorize experiments or treatment. His contribution is QA, product thinking, causal and evidence architecture, reproducibility, traceability, and governance.

Project navigation:

- [`MASTER_ROADMAP.md`](MASTER_ROADMAP.md) — milestones, gates, and deferred work;
- [`BACKLOG.md`](BACKLOG.md) — dependency-ordered execution queue;
- [Epic #24](https://github.com/safal207/Kairos-Gate-for-X-Cell/issues/24) — canonical GitHub roadmap.

## Core research question

Does adding a measurable pre-intervention phase variable improve held-out cellular perturbation-response prediction relative to a matched static-state baseline?

```text
static baseline:
cell state + perturbation -> response

phase-conditioned:
cell state + perturbation + measurable phase -> response
```

A positive predictive result does not establish causality. Controlled or valid quasi-experimental evidence is required before making a causal timing claim.

## Foundation protocol v0.1

The foundation provides:

- strict Draft 2020-12 transition validation;
- supported pre-intervention phase admission with timestamp ordering;
- rejection of `NaN`, `Infinity`, JSON overflow literals, and non-finite in-memory values;
- deterministic research-only classifications;
- hard identity, toxicity, and reversibility exclusions;
- a synthetic phase benchmark with baseline, conditioning, ablation, and shuffle control;
- a versioned TIP-to-Kairos handoff with immutable evidence references;
- FAIR-oriented reproducibility, Model Card, and Data Card templates;
- exact-head CI evidence and installed-wheel validation.

### Research-only classifications

- `CANDIDATE_WINDOW` — current model-level criteria support further research;
- `WAIT` — timing or expected effectiveness is below the current threshold;
- `EXCLUDE` — a hard identity, toxicity, or reversibility boundary is violated;
- `INSUFFICIENT_EVIDENCE` — supported phase evidence or evidence quality is inadequate.

Hard exclusions take precedence over missing evidence. A known high-risk record cannot be softened into `INSUFFICIENT_EVIDENCE`.

## BioEvidence OS v0.1

Before asking how to influence a biological system, BioEvidence OS asks whether the experimental units are defensible, observations are traceable, competing explanations remain visible, independent evidence is genuinely independent, temporal identity matches the claim, and the requested conclusion stays within evidence limits.

### 1. `bio-experimental-unit-auditor`

Location: [`.agents/skills/bio-experimental-unit-auditor/SKILL.md`](.agents/skills/bio-experimental-unit-auditor/SKILL.md)

- distinguishes biological units from cells, wells, plates, libraries, and sequencing runs;
- reconstructs source-to-analysis lineage;
- detects pseudoreplication;
- fails closed when biological independence is not established.

### 2. `bio-provenance-confounder-graph`

Location: [`.agents/skills/bio-provenance-confounder-graph/SKILL.md`](.agents/skills/bio-provenance-confounder-graph/SKILL.md)

- creates explicit source-to-claim nodes and edges;
- keeps unknown events visible;
- detects identity collisions, broken paths, cycles, and aliased confounders;
- blocks unconditional claims through load-bearing unknown paths.

### 3. `bio-independent-replication-finder`

Location: [`.agents/skills/bio-independent-replication-finder/SKILL.md`](.agents/skills/bio-independent-replication-finder/SKILL.md)

- rejects same-study accessions, shared biological material, technical reruns, and reprocessed target data;
- separates direct replication, conceptual replication, external validation, and method transfer;
- requires machine-checkable evidence and a prespecified test.

### 4. `bio-causal-hypothesis-ranker`

Location: [`.agents/skills/bio-causal-hypothesis-ranker/SKILL.md`](.agents/skills/bio-causal-hypothesis-ranker/SKILL.md)

- compares direct action, shared state, marker-only, technical-confounding, small-effect, and chance explanations;
- requires evidence for and against, predictions, falsifiers, and discriminators;
- ranks explanations without translating rank into causal identification;
- blocks identification unless temporal, experimental-unit, design, confounder, and independent-validation gates pass.

### 5. `bio-temporal-replication-gate`

Location: [`.agents/skills/bio-temporal-replication-gate/SKILL.md`](.agents/skills/bio-temporal-replication-gate/SKILL.md)

- requires the molecular pre-state to precede the transition;
- requires the later phenotype to be linked to the same cell or a defensible longitudinal unit;
- prevents post-stimulation RNA from being described as a basal predictor;
- records a machine-readable replication gap rather than lowering eligibility standards.

### 6. `bio-partner-lab-evidence-handoff`

Location: [`.agents/skills/bio-partner-lab-evidence-handoff/SKILL.md`](.agents/skills/bio-partner-lab-evidence-handoff/SKILL.md)

- converts a documented public-data gap into a bounded evidence question for an authorized institution;
- defines biological-unit, timing, identity, model-comparison, data-return, stop, and governance contracts;
- requires a decision matrix covering shared state, direct effect, marker-only, technical confounding, small effects, and null results;
- contains no physical biological procedures;
- separates scientific-review readiness from authorization to execute a study.

All six skills are computational and documentary only.

## Reference case: GSE141064 Batch 8_8

The public metadata and code audit recovered exact metadata-to-count linkage and a response-independent 17-cell cohort. Plate, index, and run labels are technical grouping candidates; no source-backed reply has established independent cultures, collection days, imaging sessions, or biological replicate semantics for the selected cohort.

Current boundary:

```text
EXPLORATORY_ONLY_TECHNICAL_GROUPING
BLOCKED_REPLICATE_SEMANTICS_UNRESOLVED
```

Consequences:

- exploratory cell-level description is allowed with limits;
- leave-one-plate-out is technical sensitivity only;
- plate-based biological pseudobulk is blocked;
- collection day, extraction round, imaging session, and source-culture dependencies remain unresolved;
- prediction on new biological units is not established;
- causal, tissue, clinical, diagnostic, treatment, and therapeutic claims are blocked.

The author-clarification request remains tracked in [DeplanckeLab/Live-seq#9](https://github.com/DeplanckeLab/Live-seq/issues/9).

Machine-readable records:

- [`examples/gse141064.experimental-unit-audit.json`](examples/gse141064.experimental-unit-audit.json)
- [`examples/gse141064.provenance-confounder-graph.json`](examples/gse141064.provenance-confounder-graph.json)
- [`examples/gse141064.independent-replication-search.json`](examples/gse141064.independent-replication-search.json)
- [`examples/gse141064.nfkbia-causal-hypotheses.json`](examples/gse141064.nfkbia-causal-hypotheses.json)
- [`examples/gse141064.temporal-replication-gate.json`](examples/gse141064.temporal-replication-gate.json)
- [`examples/gse141064.nfkbia-partner-lab-handoff.json`](examples/gse141064.nfkbia-partner-lab-handoff.json)

## Independent conceptual candidate: GSE94383

GSE94383 measures LPS-induced NF-kB dynamics and RNA-seq in the same RAW264.7 cells. The exact public tables were downloaded and checksum-verified and contained the same **823 unique cell IDs**, with no duplicates.

| Metric | Value |
|---|---:|
| Spearman rho | **0.178** |
| Bootstrap 95% CI | **0.110 to 0.243** |
| Stratified permutation p | **0.0002** |
| Leave-one-ID-prefix-out rho range | **0.153 to 0.200** |

```text
CONCEPTUAL_SIGNAL_SUPPORTED
```

This is weak but stable independent pathway coupling. It is not direct temporal replication because RNA is measured after stimulation rather than before a future `Tnf-mCherry` phenotype.

Persistent evidence:

- [`reports/gse94383-conceptual-replication-2026-07-23.md`](reports/gse94383-conceptual-replication-2026-07-23.md)
- [`reports/gse94383-conceptual-replication-2026-07-23.json`](reports/gse94383-conceptual-replication-2026-07-23.json)

## Causal-hypothesis ranking

Current ranking:

1. shared upstream cellular state;
2. direct `Nfkbia` negative-feedback effect;
3. small context-specific real effect;
4. technical confounding;
5. state marker only;
6. chance or overfitting.

```text
RANKED_NOT_IDENTIFIED
```

Rank 1 is not a causal winner. The direct-effect hypothesis has no identifying intervention, the experimental unit is unresolved, major confounders are not separable, and direct external temporal replication is absent.

## Direct temporal replication gap

The frozen target is:

```text
basal pre-LPS transcriptome
        ↓ same cell
LPS transition
        ↓
later Tnf-promoter response dynamics
```

No independent public dataset found in the searched surfaces simultaneously provides the required pre-state, later same-cell phenotype, independent biological units, endpoint compatibility, and technical lineage.

```text
DIRECT_REPLICATION_GAP
```

Persistent report:

- [`reports/gse141064-direct-temporal-replication-gap-2026-07-23.md`](reports/gse141064-direct-temporal-replication-gap-2026-07-23.md)

## Original Supplementary Table 4 diagnostic

The publisher workbook contains **362 tested genes** for prediction of later `Tnf-mCherry` slope.

| Metric | `Nfkbia` value |
|---|---:|
| LM p-value | **0.0002735** |
| LM FDR | **0.0996** |
| R² | **0.5977** |
| Coefficient | **−0.1239** |
| Bootstrap p-value | **0.01198** |
| Bootstrap FDR | **0.6056** |

`Nfkbia` is the only gene with LM FDR at or below 0.10, but no gene reaches bootstrap FDR at or below 0.20.

```text
TOP_DISCOVERY_CANDIDATE_NOT_STABLE_UNIQUE_DRIVER
```

This supports `Nfkbia` as a discovery candidate in the original small sample, not as an externally replicated unique driver.

## Partner-laboratory evidence handoff

```text
READY_FOR_PARTNER_SCIENTIFIC_REVIEW
PHYSICAL_EXECUTION_NOT_AUTHORIZED
AI_DOES_NOT_AUTHORIZE_EXECUTION
```

The handoff freezes the evidence question, competing explanations, biological-unit and temporal-identity requirements, candidate and control model families, machine-readable data-return requirements, interpretation limits, HOLD conditions, and institutional governance gates.

Persistent report:

- [`reports/gse141064-nfkbia-partner-lab-handoff-2026-07-23.md`](reports/gse141064-nfkbia-partner-lab-handoff-2026-07-23.md)

## Repository layout

```text
README.md
CHANGELOG.md
MASTER_ROADMAP.md
BACKLOG.md
kairos_gate/                 foundation validators
kairos_gate/schemas/         packaged runtime schemas
.agents/skills/              evidence-contract skills
schemas/                     public schemas
examples/                    canonical records
protocols/                   preregistered protocols
evidence/                    committed derived evidence
reports/                     human-readable and machine-readable findings
reviews/                     external-review packets
testdata/                    synthetic and negative fixtures
tests/                       regression tests
scripts/                     validators, probes, and evidence runners
docs/                        architecture, research, safety, and reproducibility docs
```

## Quick start

Install the package and runtime dependency first:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m kairos_gate examples/phase-conditioned-transition.json
python scripts/validate_handoff.py examples/tip-kairos-handoff.json
python scripts/run_phase_benchmark.py testdata/phase-window-tiny.json
```

Run the six BioEvidence contracts:

```bash
python scripts/validate_experimental_unit_audit.py examples/gse141064.experimental-unit-audit.json
python scripts/validate_provenance_confounder_graph.py examples/gse141064.provenance-confounder-graph.json
python scripts/validate_independent_replication_search.py examples/gse141064.independent-replication-search.json
python scripts/validate_causal_hypothesis_ranking.py examples/gse141064.nfkbia-causal-hypotheses.json
python scripts/validate_temporal_replication_gate.py examples/gse141064.temporal-replication-gate.json
python scripts/validate_partner_lab_evidence_handoff.py examples/gse141064.nfkbia-partner-lab-handoff.json
```

To reproduce the exact-head foundation evidence flow:

```bash
export KAIROS_EXACT_HEAD="$(git rev-parse HEAD)"
python scripts/run_ci_evidence.py
python scripts/run_ci_evidence.py --enforce
```

## Relationship to the wider protocol family

The primary internal bridge is [Transition Intelligence Protocol](https://github.com/safal207/transition-intelligence-protocol):

```text
IFP: Is the initial state sufficiently known?
TIP: Which transition is justified next?
Kairos Gate: Is this a candidate phase window for that transition?
BioEvidence OS: Which conclusions are supported, limited, unresolved, or blocked?
```

Additional roles are documented in [Ecosystem Bridge](docs/ECOSYSTEM_BRIDGE.md), including T-Trace, CML, LiminalDB, PythiaLabs, ProofPath, LRI, SOMA, and Lifetra.

## Validation

CI verifies:

- complete foundation schema and deterministic-decision boundaries;
- six valid BioEvidence contracts;
- paired fail-closed leakage cases, including pseudoreplication, hidden confounding, same-study reuse, false causal identification, timing leakage, and false physical authorization;
- publisher checksums and exact cell-ID compatibility for GSE94383;
- the frozen conceptual-replication analysis;
- the original Live-seq Supplementary Table 4 structure and `Nfkbia` ranking;
- reproducibility artifacts tied to the exact commit.

## Safety boundary

Kairos Gate is a computational research protocol. It does not provide or authorize wet-lab procedures, biological modification, genetic modification, pathogen work, animal or human experimentation, diagnosis, treatment, or clinical decisions.

Physical validation must be performed through a competent authorized institution with scientific supervision and every scientific, ethical, biosafety, legal, quality, consent, containment, and data-governance process it determines is applicable.

## Roadmap

- [x] Foundation protocol and exact-head validation.
- [x] Experimental-unit and pseudoreplication firewall.
- [x] Biological provenance and confounder graph.
- [x] Independent-evidence classifier.
- [x] Conceptual-replication analysis.
- [x] Causal-hypothesis ranking.
- [x] Direct temporal replication gate and gap record.
- [x] Original Supplementary Table 4 diagnostic.
- [x] Non-operational partner-laboratory evidence handoff.
- [ ] Receive and disposition external biology and statistics reviews.
- [ ] Integrate the model-governance stack in dependency order.
- [ ] Build the accession-to-evidence MVP.
- [ ] Publish the technical report and one reviewed partner case or documented negative result.

## License and citation

The repository is licensed under MIT. Citation metadata is provided in [`CITATION.cff`](CITATION.cff).
