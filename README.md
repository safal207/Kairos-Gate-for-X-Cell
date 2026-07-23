# Kairos Gate for X-Cell

Kairos Gate is a computational evidence and safety layer for deciding when a predicted cellular transition is sufficiently supported to move from hypothesis to authorized biological validation.

The project starts with a narrower and more important problem:

> Before asking how to influence a biological system, can we prove what the true experimental units were, which observations are independent, and which claims the data can actually support?

## First vertical slice

### `bio-experimental-unit-auditor v0.1`

Location: [`.agents/skills/bio-experimental-unit-auditor/SKILL.md`](.agents/skills/bio-experimental-unit-auditor/SKILL.md)

The skill:

- distinguishes biological units from cells, wells, plates, libraries, and sequencing runs;
- reconstructs source-to-analysis lineage;
- detects pseudoreplication and batch confounding;
- applies F0–F5 evidence levels and L1–L4 audit depth;
- separates descriptive, associative, predictive, causal, tissue, and clinical claims;
- fails closed when biological independence is not established;
- remains computational-only and does not authorize physical biological work.

## Reference case

The first contract fixture audits **GSE141064 Batch 8_8**.

Author clarification indicates that plate labels are technical library-preparation structures rather than independent biological experiments, `exp8_*` labels sequencing runs or flow cells, cells were collected across multiple days, and exact per-cell collection grouping was not retained.

Accordingly:

- exploratory cell-level description is allowed with limits;
- leave-one-plate-out is only a technical sensitivity analysis;
- plate-based pseudobulk biological inference is blocked;
- prediction on new biological units is not established;
- causal, tissue, clinical, and therapeutic claims are blocked.

Machine-readable record: [`examples/gse141064.experimental-unit-audit.json`](examples/gse141064.experimental-unit-audit.json)

## Contract validation

```bash
python scripts/validate_experimental_unit_audit.py \
  examples/gse141064.experimental-unit-audit.json
```

The CI contract also verifies that a synthetic plate-as-biological-replicate fixture is rejected.

## Safety boundary

Kairos Gate is currently a computational research protocol. It does not provide or authorize wet-lab procedures, biological modification, human experimentation, treatment, or clinical decisions.

Physical biological validation must be performed through a competent authorized institution with appropriate scientific supervision, ethics approval, biosafety review, consent, data governance, containment, and stop criteria.

## Roadmap

1. Experimental-unit resolution and pseudoreplication firewall.
2. Biological provenance and confounder graph.
3. Independent-dataset replication finder.
4. Causal hypothesis ranking with uncertainty.
5. Safe handoff specification for partner laboratories.
6. Result reconciliation and negative-result memory.
