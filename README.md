# Kairos Gate for X-Cell

Kairos Gate is a computational evidence and safety layer for deciding when a predicted cellular transition is sufficiently supported to move from hypothesis to authorized biological validation.

> Before asking how to influence a biological system, can we prove the experimental units, trace every observation, expose competing explanations, locate genuinely independent evidence, enforce temporal identity, and state only the claims the evidence supports?

## Biological evidence stack v0.1

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
- distinguishes direct replication, conceptual replication, external validation, and method transfer;
- requires F3 machine-checkable evidence and a prespecified test.

### 4. `bio-causal-hypothesis-ranker`

Location: [`.agents/skills/bio-causal-hypothesis-ranker/SKILL.md`](.agents/skills/bio-causal-hypothesis-ranker/SKILL.md)

- compares direct action, shared state, marker-only, technical-confounding, small-effect, and chance explanations;
- requires evidence for and against, predictions, falsifiers, and discriminators;
- ranks explanations without translating rank into causal identification;
- blocks identification unless every temporal, experimental-unit, identifying-design, confounder, and independent-validation gate passes.

### 5. `bio-temporal-replication-gate`

Location: [`.agents/skills/bio-temporal-replication-gate/SKILL.md`](.agents/skills/bio-temporal-replication-gate/SKILL.md)

- requires the molecular pre-state to precede the transition;
- requires the later phenotype to be linked to the same cell or defensible longitudinal unit;
- prevents post-stimulation RNA from being described as a basal predictor;
- separates direct temporal replication from partial, conceptual, cross-sectional, and method-transfer evidence;
- records a machine-readable replication gap rather than lowering eligibility standards.

All five skills are computational-only and do not authorize physical biological work.

## Reference case: GSE141064 Batch 8_8

Author clarification indicates that plate labels and `exp8_*` runs are technical structures, while exact per-cell collection grouping was not retained.

Consequences:

- exploratory cell-level description is allowed with limits;
- leave-one-plate-out is technical sensitivity only;
- plate-based biological pseudobulk is blocked;
- collection day, extraction round, and imaging session remain unresolved confounders;
- prediction on new biological units is not established;
- causal, tissue, clinical, and therapeutic claims are blocked.

Machine-readable records:

- [`examples/gse141064.experimental-unit-audit.json`](examples/gse141064.experimental-unit-audit.json)
- [`examples/gse141064.provenance-confounder-graph.json`](examples/gse141064.provenance-confounder-graph.json)
- [`examples/gse141064.independent-replication-search.json`](examples/gse141064.independent-replication-search.json)
- [`examples/gse141064.nfkbia-causal-hypotheses.json`](examples/gse141064.nfkbia-causal-hypotheses.json)
- [`examples/gse141064.temporal-replication-gate.json`](examples/gse141064.temporal-replication-gate.json)

## Independent conceptual candidate: GSE94383

GSE94383 measures LPS-induced NF-kB dynamics and RNA-seq in the same RAW264.7 cells.

The exact public tables were downloaded and checksum-verified. The dynamics and expression tables contained the same **823 unique cell IDs**, with no duplicates.

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

No independent public dataset found in the searched repository and literature surfaces simultaneously provides the required pre-state, later same-cell phenotype, independent biological units, endpoint compatibility, and technical lineage.

```text
DIRECT_REPLICATION_GAP
```

GSE94383 remains conceptual; GSE162992 is held as incomplete; GSE65528, GSE65529, and GSE161125 provide cross-sectional support; Raman2RNA is method-transfer evidence only.

Persistent report:

- [`reports/gse141064-direct-temporal-replication-gap-2026-07-23.md`](reports/gse141064-direct-temporal-replication-gap-2026-07-23.md)

## Original Supplementary Table 4 diagnostic

The publisher workbook contains **362 tested genes** for prediction of later `Tnf-mCherry` slope.

`Nfkbia` is ranked first by linear-model p-value:

| Metric | Value |
|---|---:|
| LM p-value | **0.0002735** |
| LM FDR | **0.0996** |
| R² | **0.5977** |
| Coefficient | **−0.1239** |
| Bootstrap p-value | **0.01198** |
| Bootstrap FDR | **0.6056** |

`Nfkbia` is the only gene with LM FDR ≤ 0.10, but **no gene** reaches bootstrap FDR ≤ 0.20.

```text
TOP_DISCOVERY_CANDIDATE_NOT_STABLE_UNIQUE_DRIVER
```

This supports `Nfkbia` as a strong discovery candidate in the original small sample, not as an externally replicated unique driver. Winner's-curse risk remains high.

Persistent evidence:

- [`reports/gse141064-supplementary-table4-probe-2026-07-23.json`](reports/gse141064-supplementary-table4-probe-2026-07-23.json)

## Validation

```bash
python scripts/validate_experimental_unit_audit.py examples/gse141064.experimental-unit-audit.json
python scripts/validate_provenance_confounder_graph.py examples/gse141064.provenance-confounder-graph.json
python scripts/validate_independent_replication_search.py examples/gse141064.independent-replication-search.json
python scripts/validate_causal_hypothesis_ranking.py examples/gse141064.nfkbia-causal-hypotheses.json
python scripts/validate_temporal_replication_gate.py examples/gse141064.temporal-replication-gate.json
```

CI verifies:

- five valid biological-evidence contracts;
- five invalid cases that must fail closed;
- publisher checksums and exact cell-ID compatibility for GSE94383;
- the frozen GSE94383 conceptual-replication analysis;
- the original Live-seq Supplementary Table 4 structure and `Nfkbia` ranking;
- reproducibility artifacts tied to the exact commit.

## Safety boundary

Kairos Gate is a computational research protocol. It does not provide or authorize wet-lab procedures, biological modification, human experimentation, treatment, or clinical decisions.

Physical validation must be performed through a competent authorized institution with scientific supervision, applicable ethics approval, biosafety review, consent, data governance, containment, and stop criteria.

## Roadmap

- [x] Experimental-unit resolution and pseudoreplication firewall.
- [x] Biological provenance and confounder graph.
- [x] Independent-dataset replication finder.
- [x] Live repository search and conceptual-replication run.
- [x] Causal hypothesis ranking.
- [x] Direct temporal replication gate and gap record.
- [x] Original Supplementary Table 4 diagnostic.
- [ ] Resolve GSE94383 ID-prefix and collection-batch semantics.
- [ ] Build safe partner-laboratory evidence handoff.
- [ ] Add result reconciliation and negative-result memory.
