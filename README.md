# Kairos Gate for X-Cell

Kairos Gate is a computational evidence and safety layer for deciding when a predicted cellular transition is sufficiently supported to move from hypothesis to authorized biological validation.

The project starts with a narrower and more important problem:

> Before asking how to influence a biological system, can we prove what the true experimental units were, trace every observation to its source, expose competing batch explanations, locate genuinely independent evidence, and state only the claims the evidence supports?

## Biological evidence stack v0.1

### 1. `bio-experimental-unit-auditor`

Location: [`.agents/skills/bio-experimental-unit-auditor/SKILL.md`](.agents/skills/bio-experimental-unit-auditor/SKILL.md)

The skill:

- distinguishes biological units from cells, wells, plates, libraries, and sequencing runs;
- reconstructs source-to-analysis lineage;
- detects pseudoreplication;
- applies F0–F5 evidence levels and L1–L4 audit depth;
- separates descriptive, associative, predictive, causal, tissue, and clinical claims;
- fails closed when biological independence is not established.

### 2. `bio-provenance-confounder-graph`

Location: [`.agents/skills/bio-provenance-confounder-graph/SKILL.md`](.agents/skills/bio-provenance-confounder-graph/SKILL.md)

The skill:

- creates explicit nodes for biological sources, collection events, cells, technical containers, libraries, runs, data artifacts, transformations, outputs, and claims;
- traces source-to-claim paths;
- keeps unknown events visible rather than guessing lineage;
- detects orphan claims, identity collisions, broken paths, and cyclic provenance;
- models condition and outcome paths for candidate confounders;
- classifies confounders as separable, partially separable, aliased, or unknown;
- blocks unconditional acceptance when load-bearing high-risk confounders remain.

### 3. `bio-independent-replication-finder`

Location: [`.agents/skills/bio-independent-replication-finder/SKILL.md`](.agents/skills/bio-independent-replication-finder/SKILL.md)

The skill:

- freezes the exact biological claim before inspecting candidate outcomes;
- builds a structured repository-search fingerprint;
- distinguishes independent experiments from same-study accessions, shared biological sources, technical reruns, and reprocessed target data;
- checks biological-source and experimental-unit independence separately from assay similarity;
- separates direct replication, conceptual replication, external validation, and method transfer;
- requires at least F3 machine-checkable evidence before accepting a candidate;
- requires a prespecified endpoint, biological grouping key, exclusions, and success criteria;
- never calls discovery alone a completed replication.

All three skills are computational-only and do not authorize physical biological work.

## Reference case: GSE141064 Batch 8_8

Author clarification indicates that:

- plate labels are technical library-preparation structures rather than independent biological experiments;
- `exp8_*` labels sequencing runs or flow cells;
- cells were collected across multiple days and extraction rounds;
- exact per-cell collection grouping was not retained.

Accordingly:

- exploratory cell-level description is allowed with limits;
- leave-one-plate-out is only a technical sensitivity analysis;
- plate-based pseudobulk biological inference is blocked;
- collection day/extraction round and imaging session remain high-risk unresolved confounders;
- alternate exp8 plates, libraries, runs, or reprocessed records cannot serve as independent replication;
- no independent public candidate has yet been verified;
- prediction on new biological units is not established;
- causal, tissue, clinical, and therapeutic claims are blocked.

Machine-readable records:

- [`examples/gse141064.experimental-unit-audit.json`](examples/gse141064.experimental-unit-audit.json)
- [`examples/gse141064.provenance-confounder-graph.json`](examples/gse141064.provenance-confounder-graph.json)
- [`examples/gse141064.independent-replication-search.json`](examples/gse141064.independent-replication-search.json)

## Contract validation

```bash
python scripts/validate_experimental_unit_audit.py \
  examples/gse141064.experimental-unit-audit.json

python scripts/validate_provenance_confounder_graph.py \
  examples/gse141064.provenance-confounder-graph.json

python scripts/validate_independent_replication_search.py \
  examples/gse141064.independent-replication-search.json
```

CI verifies three positive paths:

- the GSE141064 experimental-unit audit;
- the GSE141064 provenance/confounder graph;
- a valid independent-candidate contract plus the current GSE141064 replication-search `HOLD` state.

CI also verifies that three invalid cases fail closed:

- plate labels presented as biological replicates;
- a causal claim accepted through an aliased hidden-batch path;
- a split accession from the same biological material presented as independent replication.

## Safety boundary

Kairos Gate is currently a computational research protocol. It does not provide or authorize wet-lab procedures, biological modification, human experimentation, treatment, or clinical decisions.

Physical biological validation must be performed through a competent authorized institution with appropriate scientific supervision, ethics approval, biosafety review, consent, data governance, containment, and stop criteria.

## Roadmap

- [x] Experimental-unit resolution and pseudoreplication firewall.
- [x] Biological provenance and confounder graph.
- [x] Independent-dataset replication finder contract.
- [ ] Execute live repository search for the first verified GSE141064 candidate.
- [ ] Causal hypothesis ranking with uncertainty.
- [ ] Safe handoff specification for partner laboratories.
- [ ] Result reconciliation and negative-result memory.
