# GSE141064 `Nfkbia` partner-laboratory evidence handoff

## Status

```text
READY_FOR_PARTNER_SCIENTIFIC_REVIEW
```

This status means the computational evidence question is coherent enough for review by a qualified institution. It does **not** authorize physical biological work.

## Evidence question

What evidence would distinguish whether basal `Nfkbia` carries candidate-specific information about a later inflammatory response beyond broader baseline cellular state and technical structure?

Required temporal structure:

```text
biological source
  -> independent biological unit
  -> same cell or defensible longitudinal unit
  -> molecular pre-state
  -> inflammatory transition
  -> later response phenotype
```

The partner institution must independently determine the scientifically appropriate macrophage model and all physical methods.

## Why a partner review is justified

- `Nfkbia` is the first-ranked discovery candidate among 362 genes in the original small dataset.
- Its nominal linear-model evidence is stronger than the other candidates, but bootstrap multiple-testing stability is poor.
- Exact biological independence for the original 17-cell set is unresolved.
- Plate and sequencing-run labels are technical structures, not biological replicates.
- GSE94383 supplies independent conceptual pathway coupling, but measures RNA after stimulation and therefore does not directly replicate the target temporal claim.
- No independent public dataset was found with the complete required pre-state, same-unit later phenotype, biological independence, endpoint compatibility, and technical lineage.
- No identifying design currently separates direct `Nfkbia` action from broader cell state or technical confounding.

## Hypotheses to distinguish

| Hypothesis | Distinguishing evidence |
|---|---|
| Shared upstream state | A frozen broader-state model absorbs most `Nfkbia`-specific information while retaining external predictive value. |
| Direct candidate effect | `Nfkbia` retains candidate-specific information beyond state and technical models, with supporting evidence from an independently approved identifying design. |
| Marker only | `Nfkbia` becomes redundant after state adjustment and lacks candidate-specific identifying evidence. |
| Technical confounding | The signal follows technical lineage or materially weakens after balanced technical adjustment. |
| Small context-specific effect | Multiple independent collections preserve a modest direction with documented heterogeneity. |
| Null or instability | Frozen independent estimates are null, unstable, or directionally inconsistent. |

A ranking among these explanations is not causal identification.

## Experimental-unit contract

The smallest independent biological unit must be defined and justified by the partner institution before outcome analysis.

The returned evidence must preserve:

- biological-source identifier;
- independent-unit identifier;
- unit-to-cell or longitudinal-unit lineage;
- condition assignment at the biological-unit level;
- collection, operator, imaging, plate, library, and run lineage;
- biological-unit-level uncertainty.

Cells, wells, plates, libraries, sequencing runs, reads, and image frames cannot substitute for biological replication.

The partner's quantitative reviewer must provide a prospective precision or power justification. This handoff does not prescribe a numeric sample size.

## Frozen model comparison

Before outcome inspection, the following model families must be versioned:

1. `Nfkbia`-only candidate model;
2. broader baseline-state model;
3. technical-confounder model;
4. combined state, candidate, and technical model;
5. null and negative-control models.

Any post-freeze change requires a superseding record that preserves the original decision and reason for change.

## Data-return contract

The partner should return lawful, de-identified where required, machine-readable evidence sufficient to reconstruct:

- biological and technical lineage;
- ordered phases or timestamps;
- missingness and exclusions;
- raw or minimally processed measurements where permitted;
- normalization and transformation provenance;
- exact model inputs and outputs;
- uncertainty and diagnostics;
- protocol and analysis deviations;
- immutable references and checksums.

The contract asks for evidence structure, not laboratory procedures.

## Decision limits

A result favoring shared state would not identify every component of that state as causal.

A result favoring candidate-specific action could support only a bounded statement within the independently approved and validated design. It would not automatically support tissue, clinical, or therapeutic claims.

A marker-only result would support possible measurement utility, not intervention targeting.

A technically confounded result would block biological interpretation of the affected estimate.

A small stable effect would remain context-limited until transported and independently reproduced.

A null or unstable result must be retained as a negative result rather than hidden.

## Automatic HOLD conditions

Return `HOLD` when:

- biological-source or independent-unit lineage cannot be reconstructed;
- the proposed molecular pre-state occurs after the transition or timing is ambiguous;
- later phenotype cannot be linked to the same longitudinal unit;
- condition is aliased with operator, collection phase, imaging phase, plate, library, or run;
- exclusions, missingness, or transformations are outcome-dependent or undocumented;
- the frozen model plan changes after outcome inspection without a superseding record;
- applicable competence, oversight, containment, ethics, consent, or data-governance requirements remain unresolved.

The partner institution must additionally apply its own safety and quality stop criteria.

## Governance boundary

Review is required from the institutionally appropriate combination of:

- qualified principal investigator;
- domain biologist;
- statistician or quantitative methodologist;
- biosafety authority, where applicable;
- ethics or human/animal research authority, where applicable;
- data-protection and governance authority;
- quality or reproducibility reviewer.

The institution, not Kairos Gate and not an AI system, determines which approvals apply and whether any study may proceed.

## Claim firewall

Currently supported with limits:

- exploratory association in the original observed cells;
- `Nfkbia` as a strong but unstable discovery candidate;
- independent conceptual NF-kB/`Nfkbia` pathway coupling;
- a documented direct temporal replication gap.

Not established or blocked:

- prediction on independent biological units;
- direct causal action of basal `Nfkbia`;
- tissue-level generalization;
- clinical relevance;
- therapeutic relevance.

## Safety boundary

This package contains no physical protocol, recipes, concentrations, doses, treatment instructions, biological-modification instructions, infection procedures, implantation procedures, or human-experimentation instructions.

```text
SCIENTIFIC_REVIEW_READY
PHYSICAL_EXECUTION_NOT_AUTHORIZED
AI_DOES_NOT_AUTHORIZE_EXECUTION
```
