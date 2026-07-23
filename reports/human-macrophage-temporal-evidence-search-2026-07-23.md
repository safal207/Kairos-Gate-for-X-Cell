# Human macrophage temporal-evidence search

**Search date:** 2026-07-23  
**Search ID:** `HMTE-2026-07-23-v1`  
**Machine-readable record:** `examples/human-macrophage-temporal-evidence-search.2026-07-23.json`

## Executive verdict

```text
HUMAN_DIRECT_REPLICATION_GAP
```

The search found several strong human macrophage and monocyte resources for domain adaptation, donor-level longitudinal analysis, trained-immunity modeling, post-restimulation single-cell response analysis, and foundation-model benchmarking.

It did **not** find an independent public human dataset that links an individual cell's molecular state before inflammatory stimulation to that same cell's later inflammatory phenotype while retaining independent biological units and sufficient technical lineage.

The eligibility criteria were not weakened.

## Frozen target

```text
human macrophage pre-stimulation molecular state
                    ↓ same cell
          inflammatory transition
                    ↓
        later cytokine/signaling phenotype
```

This target is intentionally narrower than:

- pre/post measurements from different cells of one donor;
- separate aliquots from the same culture;
- post-stimulation single-cell RNA-seq;
- longitudinal sampling of the same person;
- population-level RNA linked to population-level cytokines;
- a human macrophage atlas without a future phenotype.

Those resources can be valuable without being direct replication.

## Search surfaces

Primary and public sources searched included:

- NCBI GEO;
- PubMed and PubMed Central;
- Dryad;
- CaltechAUTHORS supplementary data;
- primary article data-availability statements.

Frozen queries included combinations of:

- human macrophage or monocyte;
- baseline or pre-stimulation molecular state;
- later cytokine, signaling, reporter, or functional response;
- same-cell, lineage-linked, live-cell imaging, longitudinal, and single-cell RNA sequencing;
- trained immunity and inflammatory restimulation.

## Candidate assessment

| Candidate | Useful evidence | Classification | Why it is not direct same-cell replication |
|---|---|---|---|
| **GSE184241** | Human monocyte scRNA-seq before vaccination and at 2 weeks/3 months, with ex-vivo LPS conditions; three donors | `DONOR_LEVEL_TEMPORAL_SUPPORT` | Baseline and responsive transcriptomes are different cells. Identity is longitudinal at donor level, not cell level. |
| **Dryad 10.5061/dryad.stqjq2cjc + GSE323311** | 2026 human macrophage trained-immunity package with donor metadata, single-molecule RNA imaging, cytometry, ATAC-seq, and code | `DONOR_LEVEL_TEMPORAL_SUPPORT` | Pre-restimulation state and later cytokine measurements are not linked in the same individual cell. |
| **GSE85243** | Time-resolved human monocyte-to-macrophage RNA-seq with later TNF/IL6 restimulation readouts | `DONOR_LEVEL_TEMPORAL_SUPPORT` | Population or aliquot RNA and population cytokine measurements cannot recover cell-level identity. |
| **GSE235094** | Human trained-monocyte transcriptomes before and after secondary LPS, with inflammatory cytokine context | `DONOR_LEVEL_TEMPORAL_SUPPORT` | Bulk condition samples and secreted outputs are not linked to the same cell's pre-state. |
| **GSE137043** | Longitudinal human volunteer monocyte transcriptome/epigenome and cytokine response after controlled malaria infection | `DONOR_LEVEL_TEMPORAL_SUPPORT` | Subject-level rather than same-cell; raw-data access is restricted. |
| **GSE126085** | Human CD14 monocyte-to-macrophage scRNA time series at days 0, 3, and 6 across donors | `HUMAN_DOMAIN_REFERENCE` | Destructive samples at different time points and no linked later inflammatory phenotype. |
| **GSE296669** | Multimodal human tissue macrophages across donors and tissues with ex-vivo polarization and secreted-protein context | `HUMAN_DOMAIN_REFERENCE` | Donor/tissue aliquots, not a single cell measured before and after response. |
| **GSE130070** | Human CD14 monocyte scRNA after LPS with or without IL-10 signaling blockade | `SINGLE_CELL_POST_RESPONSE_SUPPORT` | RNA is measured after exposure and therefore cannot be a baseline predictor. |

## Highest-value human resources

### 1. GSE184241: best current Geneformer-compatible benchmark

GSE184241 is the highest-priority public resource for testing human single-cell representation models because it provides:

- human CD14 monocytes;
- explicit donor identity;
- longitudinal visits;
- unstimulated and ex-vivo LPS conditions;
- raw and processed single-cell expression data.

A defensible computational task is donor-held-out classification or representation analysis of vaccination/time/LPS state.

It cannot validate the claim that an individual cell's baseline `NFKBIA` or broader transcriptome predicts that same cell's future response. The unit of generalization must remain donor or donor-visit, and cells from the same donor must not be split across training and test sets.

### 2. 2026 Dryad trained-immunity package: best current human response-dynamics resource

The Dryad package associated with the 2026 Cell Systems manuscripts contains imaging, sequencing, cytometry, donor metadata, extraction scripts, and plotting code. It includes quantitative cytokine RNA measurements across large numbers of primary human macrophages and captures the timing dependence of trained responses.

This package is ideal for:

- response-trajectory characterization;
- donor variability;
- gene-specific early-versus-late response behavior;
- comparison of trained and untrained human macrophage states;
- testing whether model-derived states align with donor-level or condition-level response summaries.

It is not direct same-cell temporal replication because the molecular pre-state and later response are not preserved as two measurements from the same living cell.

### 3. GSE85243 and GSE235094: donor-level temporal controls

These datasets provide clear temporal and functional structure at population level. They are useful for asking whether a human molecular state at a donor/condition level is associated with a later response, while explicitly demonstrating how much inference is lost when same-cell identity is absent.

They should be used as donor-level controls, not as cell-level validation.

### 4. GSE126085 and GSE296669: human domain-shift references

These resources are valuable for testing whether a human single-cell foundation model behaves coherently across:

- monocyte-to-macrophage differentiation;
- donor holdouts;
- tissue contexts;
- ex-vivo polarization states.

They can help answer whether a representation is human-macrophage compatible. They cannot by themselves answer the future-response question.

## Model-governance consequences

The search changes the BioNeMo plan in a useful way.

### Allowed next model work

1. Use **GSE184241** for a donor-held-out human Geneformer representation benchmark.
2. Use **GSE126085** for monocyte-to-macrophage state-space continuity.
3. Use **GSE296669** for tissue and donor domain-shift stress tests.
4. Use the **2026 Dryad package** as an external human response-timing benchmark at donor/condition and post-response single-cell levels.
5. Preserve exact model checkpoints, input hashes, transformations, donor splits, and output hashes in Model Evidence Passports.

### Still blocked

- cell-level future-response prediction;
- direct `NFKBIA`-specific prediction;
- causal interpretation;
- clinical or therapeutic inference;
- upgrading donor-level association into same-cell evidence;
- using an embedding to fill missing temporal identity.

## GSE94383 cell-ID prefix resolution

### Resolved boundary

```text
TECHNICAL_OR_CONDITION_PREFIX
NOT_A_BIOLOGICAL_REPLICATE
```

GEO documents that:

- cells are partitioned into stimulation/time samples;
- `cell_ids.csv` stores condition and cell ID;
- the data were generated in RAW264.7 cells on a Fluidigm C1 chip;
- imaging dynamics and transcriptomes are linked by cell ID.

No authoritative source located in this search establishes the supplementary-table prefixes as independent biological donors or biological replicates.

Therefore:

- leave-one-prefix-out remains a technical/condition sensitivity analysis;
- the 823 cells cannot be described as 823 independent biological replicates;
- prefixes cannot be used as random-effect biological groups;
- exact mapping of every prefix component to chip, harvest, acquisition field, or time condition remains unresolved and visible.

This resolves the load-bearing question: the prefixes are **not evidence of biological independence**, even though their full technical syntax is not yet decoded.

## Refreshed partner-laboratory evidence requirement

A direct human replication would need to return a non-operational evidence package containing:

- explicit independent human donors or other defensible biological units;
- a molecular pre-state measured before the inflammatory transition;
- retained identity linking that pre-state to the same cell's later phenotype;
- a defined later cytokine, signaling, reporter, or functional endpoint;
- donor, collection, stimulation, imaging, library, batch, and run lineage;
- prespecified candidate-only, broader-state, technical-confounder, combined, and null models;
- donor-level holdout validation;
- uncertainty and multiple-testing handling;
- machine-readable outputs and exact hashes.

```text
READY_TO_DISCUSS_WITH_AUTHORIZED_PARTNER
PHYSICAL_EXECUTION_NOT_AUTHORIZED
```

## Final claim boundary

Supported with limits:

- human macrophages and monocytes show reproducible donor-level and post-response single-cell inflammatory state structure;
- public human datasets can support species-compatible foundation-model benchmarking;
- trained-immunity resources provide valuable temporal response context.

Not established:

- a human macrophage's baseline transcriptome predicts its own later inflammatory response;
- `NFKBIA` contributes predictive information beyond broader cell state and technical context;
- any causal, tissue-wide, clinical, or therapeutic conclusion.

## Safety boundary

This report is computational and documentary. It contains no physical experimental protocol and does not authorize biological work, treatment, or clinical decisions.