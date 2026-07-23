# Kairos Gate for X-Cell

Kairos Gate is a computational evidence and safety layer for deciding when a predicted cellular transition is sufficiently supported to move from hypothesis to authorized biological validation.

> Before asking how to influence a biological system, can we prove the experimental units, trace every observation, expose competing batch explanations, locate genuinely independent evidence, compare causal explanations, and state only the claims the evidence supports?

## Biological evidence stack v0.1

### 1. `bio-experimental-unit-auditor`

Location: [`.agents/skills/bio-experimental-unit-auditor/SKILL.md`](.agents/skills/bio-experimental-unit-auditor/SKILL.md)

- distinguishes biological units from cells, wells, plates, libraries, and sequencing runs;
- reconstructs source-to-analysis lineage;
- detects pseudoreplication;
- applies F0–F5 evidence levels and L1–L4 audit depth;
- separates descriptive, associative, predictive, causal, tissue, and clinical claims;
- fails closed when biological independence is not established.

### 2. `bio-provenance-confounder-graph`

Location: [`.agents/skills/bio-provenance-confounder-graph/SKILL.md`](.agents/skills/bio-provenance-confounder-graph/SKILL.md)

- creates explicit source-to-claim nodes and edges;
- keeps unknown events visible rather than guessing lineage;
- detects orphan claims, identity collisions, broken paths, and cycles;
- models condition and outcome paths for candidate confounders;
- classifies confounders as separable, partially separable, aliased, or unknown;
- blocks unconditional acceptance when load-bearing high-risk confounders remain.

### 3. `bio-independent-replication-finder`

Location: [`.agents/skills/bio-independent-replication-finder/SKILL.md`](.agents/skills/bio-independent-replication-finder/SKILL.md)

- freezes the claim before candidate outcomes are inspected;
- rejects same-study accessions, shared biological material, technical reruns, and reprocessed target data;
- checks biological-source independence separately from assay similarity;
- distinguishes direct replication, conceptual replication, external validation, and method transfer;
- requires at least F3 machine-checkable evidence for an accepted candidate;
- requires a prespecified endpoint, grouping key, exclusions, and success criteria.

### 4. `bio-causal-hypothesis-ranker`

Location: [`.agents/skills/bio-causal-hypothesis-ranker/SKILL.md`](.agents/skills/bio-causal-hypothesis-ranker/SKILL.md)

- converts an association into competing causal, non-causal, technical, and null explanations;
- ranks explanations without translating rank into causal identification;
- requires evidence for, evidence against, predictions, falsifiers, and a discriminator for every hypothesis;
- compares direct action, shared state, marker-only, technical confounding, small-effect, and chance explanations;
- carries experimental-unit, provenance, confounder, replication, and temporal constraints forward unchanged;
- blocks causal identification unless temporal, experimental-unit, identifying-design, confounder, and independent-validation gates all pass.

All four skills are computational-only and do not authorize physical biological work.

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

## First live independent candidate: GSE94383

A live repository search identified **GSE94383** as the strongest independent conceptual candidate. It measures LPS-induced NF-kB dynamics and RNA-seq in the same RAW264.7 cells.

The exact public tables were downloaded and checksum-verified. The dynamics and expression tables contained the same **823 unique cell IDs**, with no duplicates.

Frozen primary endpoint:

> Is post-LPS `Nfkbia` expression positively associated with recent preceding same-cell NF-kB activity after stratification by transcriptome harvest time?

Result:

| Metric | Value |
|---|---:|
| Spearman rho | **0.178** |
| Bootstrap 95% CI | **0.110 to 0.243** |
| Stratified permutation p | **0.0002** |
| Leave-one-ID-prefix-out rho range | **0.153 to 0.200** |

Verdict:

```text
CONCEPTUAL_SIGNAL_SUPPORTED
```

This is a weak but stable independent pathway-coupling signal. It is **not direct replication** of the GSE141064 claim because GSE94383 measures RNA after stimulation rather than basal RNA followed by a future `Tnf-mCherry` phenotype.

Persistent evidence:

- [`reports/gse94383-conceptual-replication-2026-07-23.md`](reports/gse94383-conceptual-replication-2026-07-23.md)
- [`reports/gse94383-conceptual-replication-2026-07-23.json`](reports/gse94383-conceptual-replication-2026-07-23.json)
- [`scripts/analyze_gse94383_conceptual_replication.py`](scripts/analyze_gse94383_conceptual_replication.py)

## First causal-hypothesis ranking

The `Nfkbia` case currently ranks the explanations as:

1. **Shared upstream cellular state** — best-supported explanation.
2. **Direct Nfkbia negative-feedback effect** — mechanistically plausible but not identified.
3. **Small context-specific real effect** — compatible with the weak independent signal.
4. **Technical confounding** — remains plausible because collection structure is incomplete.
5. **State marker only** — Nfkbia may track rather than control inflammatory readiness.
6. **Chance or overfitting** — weakened by independent pathway triangulation but still live for the exact 17-cell target result.

Current verdict:

```text
RANKED_NOT_IDENTIFIED
```

Rank 1 is not a causal winner. The direct-effect hypothesis has no identifying intervention, the experimental unit is unresolved, major confounders are not separable, and direct external replication is absent.

The highest-information next action is a frozen comparison of `Nfkbia`-only, broader baseline-state, and technical-confounder models on an independent dataset containing pre-stimulation transcriptomes linked to later inflammatory phenotypes.

## Validation

```bash
python scripts/validate_experimental_unit_audit.py \
  examples/gse141064.experimental-unit-audit.json

python scripts/validate_provenance_confounder_graph.py \
  examples/gse141064.provenance-confounder-graph.json

python scripts/validate_independent_replication_search.py \
  examples/gse141064.independent-replication-search.json

python scripts/validate_causal_hypothesis_ranking.py \
  examples/gse141064.nfkbia-causal-hypotheses.json
```

CI verifies:

- four valid biological-evidence contracts;
- four invalid cases that must fail closed;
- publisher checksums for GSE94383;
- exact cell-ID compatibility;
- the frozen GSE94383 conceptual-replication analysis;
- reproducibility artifacts tied to the exact commit.

## Safety boundary

Kairos Gate is a computational research protocol. It does not provide or authorize wet-lab procedures, biological modification, human experimentation, treatment, or clinical decisions.

Physical validation must be performed through a competent authorized institution with scientific supervision, applicable ethics approval, biosafety review, consent, data governance, containment, and stop criteria.

## Roadmap

- [x] Experimental-unit resolution and pseudoreplication firewall.
- [x] Biological provenance and confounder graph.
- [x] Independent-dataset replication finder contract.
- [x] Live repository search and first conceptual-replication run.
- [x] Causal hypothesis ranking with uncertainty.
- [ ] Resolve GSE94383 ID-prefix and collection-batch semantics.
- [ ] Find a pre-stimulation transcriptome linked to a later TNF-promoter phenotype.
- [ ] Safe handoff specification for partner laboratories.
- [ ] Result reconciliation and negative-result memory.
