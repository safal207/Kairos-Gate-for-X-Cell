# GSE141064 direct temporal replication gap

## Frozen target

The target evidence structure is:

```text
basal pre-LPS transcriptome
        ↓ same cell
LPS transition
        ↓
later Tnf-promoter response dynamics
```

The candidate dataset must be biologically independent of GSE141064 and support a frozen comparison of:

1. an `Nfkbia`-only model;
2. a broader baseline-state model;
3. a technical-confounder model.

## Search result

No independent public dataset identified in the searched GEO, SRA, BioProject, PubMed, PubMed Central, EMBL-EBI, publisher-supplement, and related-record surfaces simultaneously provides:

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
| GSE94383 | Conceptual replication | Same-cell NF-kB dynamics are linked to RNA measured after LPS; molecular timing differs from the frozen basal predictor claim. |
| GSE162992 | Conceptual / hold | Macrophage NF-kB and stimulated transcriptomics are relevant, but the required pre-state-to-later-TNF same-cell linkage is not established. |
| GSE65528 | Cross-sectional support | Expression and fluorescent infection phenotype are measured after exposure. |
| GSE65529 | Cross-sectional support | Expression is linked to LPS-bead internalization after exposure, not to a basal predictor. |
| GSE161125 | Cross-sectional support | Transcriptional and secretion programs are related, but one-to-one pre-state-to-later-response mapping is absent. |
| Raman2RNA | Method transfer only | Nondestructive transcriptome inference may be useful in future designs, but the published biology and endpoint do not replicate this claim. |

## Original Supplementary Table 4 diagnostic

The publisher workbook was downloaded and probed on exact head `47cb2907533d644a1771e1b3ff928efee884c3be` in workflow run `30002737163`.

Source identity:

- file: `41586_2022_5046_MOESM7_ESM.xlsx`;
- SHA-256: `ffb1f233d7cd0c40d79086d92f3cf335fc6cbf0de14f64538bf063974784e925`;
- sheet: `slope`;
- tested genes: **362**.

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

The second-ranked gene was `Slc12a4` with R² `0.4511`; the R² gap from `Nfkbia` was approximately `0.1465`.

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

Supported:

- `Nfkbia` is the top nominal linear-model feature in the original ranking;
- its fitted relationship with later Tnf-mCherry slope is negative;
- it is the only feature with linear-model FDR at or below 0.10 in the workbook.

Not supported:

- no gene reaches bootstrap FDR at or below 0.20;
- the workbook does not establish a uniquely stable predictor under resampling and multiplicity correction;
- the workbook is not external replication;
- the workbook does not establish a direct causal effect or generalization to independent biological units.

Winner's-curse risk remains high because feature selection and effect estimation use the same small target sample, biological independence is unresolved, and no direct external temporal replication candidate is available.

Persistent machine-readable record:

- [`gse141064-supplementary-table4-probe-2026-07-23.json`](gse141064-supplementary-table4-probe-2026-07-23.json)

## Highest-information next action

Continue public-data surveillance while preparing a non-operational partner-laboratory evidence brief that states:

- the frozen target;
- the three competing model families;
- the biological-unit requirement;
- the required temporal and identity linkage;
- the evidence needed to distinguish shared state from a direct `Nfkbia` effect;
- the claims that remain prohibited.

## Safety boundary

This report is computational and documentary only. It does not authorize biological manipulation, human experimentation, treatment, or clinical decisions.
