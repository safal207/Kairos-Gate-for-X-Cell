# GSE141064 direct temporal replication gap

## Frozen target

The target evidence structure is:

```text
basal pre-LPS transcriptome
        ↓ same cell or defensible longitudinal unit
LPS transition
        ↓
later Tnf-promoter response dynamics
```

A candidate must be biologically independent of GSE141064 and support a frozen comparison of:

1. an `Nfkbia`-only model;
2. a broader baseline-state model;
3. a technical-confounder model.

## Search result

No public dataset identified in the searched GEO, SRA, BioProject, PubMed, publisher-supplement, and related-record surfaces simultaneously provides:

- a transcriptome measured before LPS or a frozen compatible inflammatory transition;
- a later phenotype measured in the same cell;
- a TNF-promoter response or defensibly compatible endpoint;
- established independent biological units;
- sufficient technical lineage;
- adequate public data for a frozen external model comparison.

```text
DIRECT_REPLICATION_GAP
```

This gap is a result, not permission to weaken eligibility criteria.

## Candidate classification

| Candidate | Classification | Reason |
|---|---|---|
| GSE141064 | Same-study internal validation | Correct temporal design, but it is the target study and biological independence remains unresolved. |
| GSE94383 | Descriptive pathway context — `HOLD` | Same-cell NF-kB dynamics are linked to RNA measured after LPS, but timing differs and the independent biological unit for the analysed cells is unresolved. Cell-level uncertainty cannot establish replication. |
| GSE162992 | Relevant context — `HOLD` | Macrophage NF-kB and stimulated transcriptomics are relevant, but required temporal linkage and independent-unit semantics are not established. |
| GSE65528 | Method/context transfer | Expression and fluorescent infection phenotype are measured after exposure. |
| GSE65529 | Method/context transfer | Expression is linked to LPS-bead internalization after exposure, not to a basal predictor. |
| GSE161125 | Related non-equivalent evidence | Transcriptional and secretion programs are related, but one-to-one pre-state-to-later-response mapping is absent. |
| Raman2RNA | Method transfer only | Nondestructive transcriptome inference may be useful in future designs, but the published biology and endpoint do not replicate this claim. |

## Why GSE94383 does not close the gap

GSE94383 contains 823 matched cell records and shows a weak positive within-table association between preceding NF-kB activity and post-LPS `Nfkbia` expression.

However:

- RNA is collected after stimulation rather than as a basal predictor;
- the endpoint is NF-kB dynamics rather than later `Tnf-mCherry` slope;
- effective independent biological N is unresolved;
- ID-prefix semantics are unresolved;
- cell bootstrap, cell permutation, and prefix exclusion are descriptive sensitivity only.

Therefore:

```text
DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED
REPLICATION_STATUS_HOLD
```

The result does not establish independent replication, conceptual triangulation, or generalization.

## Original Supplementary Table 4 diagnostic

The publisher workbook contains 362 tested genes.

### `Nfkbia` result

| Metric | Value |
|---|---:|
| Rank by linear-model p-value | **1** |
| Linear-model p-value | **0.0002735** |
| Linear-model FDR | **0.0996** |
| R² | **0.5977** |
| Coefficient | **−0.1239** |
| Bootstrap p-value | **0.01198** |
| Bootstrap FDR | **0.6056** |

Multiplicity summary:

| Threshold | LM FDR genes | Bootstrap FDR genes |
|---:|---:|---:|
| ≤ 0.05 | 0 | 0 |
| ≤ 0.10 | 1 | 0 |
| ≤ 0.20 | 1 | 0 |

## Updated interpretation

```text
TOP_DISCOVERY_CANDIDATE_NOT_STABLE_UNIQUE_DRIVER
```

Supported with limits:

- `Nfkbia` is the top nominal linear-model feature in the original ranking;
- its fitted relationship with later `Tnf-mCherry` slope is negative;
- it is the only feature with linear-model FDR at or below 0.10 in the workbook.

Not supported:

- no gene reaches bootstrap FDR at or below 0.20;
- the workbook does not establish a uniquely stable predictor;
- the workbook is not external replication;
- the workbook does not establish causality or generalization to independent units.

Winner's-curse risk remains high because feature selection and effect estimation use the same small target sample, biological independence is unresolved, and no direct external temporal replication candidate is available.

## Highest-information next action

Continue public-data surveillance while retaining a non-operational partner-laboratory evidence brief that states:

- the frozen target;
- the competing model families;
- the biological-unit requirement;
- the required temporal and identity linkage;
- evidence needed to distinguish shared state from direct action;
- claims that remain prohibited.

## Safety boundary

This report is computational and documentary only. It does not authorize biological manipulation, human experimentation, treatment, or clinical decisions.
