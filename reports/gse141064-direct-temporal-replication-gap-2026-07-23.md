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

## What can still be done now

The original study can be re-examined diagnostically, but not used as its own external validation.

The next diagnostic artifact is Supplementary Table 4, which contains the original transcriptome-wide linear-model ranking for the rate of Tnf-mCherry fluorescence increase. The pipeline will:

- download the publisher workbook;
- preserve its checksum and structure;
- locate the `Nfkbia` entry;
- record columns and model outputs;
- avoid interpreting the supplement as independent biological replication;
- use it to design sensitivity analyses around feature-ranking and winner's-curse risk.

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
