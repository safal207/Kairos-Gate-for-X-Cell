# GSE184241 donor-held-out response-state benchmark

Date: 2026-07-23  
Frozen analysis revision: `72efd29cc41c63cf9a4d54b3a1e947529b3a1b00`

## Verdict

```text
BROAD_RESPONSE_STATE_DOMINATES
NFKBIA_ONLY_IS_INFORMATIVE_BUT_NOT_UNIQUE
GENEFORMER_RUNTIME_HOLD
NOT_SAME_CELL_FUTURE_RESPONSE_VALIDATION
```

## Question actually tested

Can an expression representation distinguish `LPS` from `RPMI` in cells from a donor that was completely excluded from fitting?

This is a useful human-domain calibration and donor-transfer benchmark. It is not the original Live-seq question. GSE184241 measures different cells in each sample and does not connect a molecular pre-state in an individual cell to that same cell's later phenotype.

## Exact public inputs

| Artifact | SHA-256 |
|---|---|
| `GSE184241_combined_raw_counts.txt.gz` | `8e2482438215dc48ead81fa97a10a57ddf11633c83384dd3b11fbe39cb60830d` |
| `GSE184241_barcode_sequences.xlsx` | `806c5b2ecb11cb4ec7a66d42608fddfb920722cbc53b23a9c000085391bb47dd` |

The matrix contains **23,895 genes and 1,710 cells**. The barcode workbook contains exactly the same 1,710 `Sample_ID` values. No zero-library cell was dropped.

Frozen mappings:

- `Plate_15` → Donor1;
- `Plate_17` → Donor2;
- `Plate_18` → Donor3;
- `v1` → day 0;
- `v2` → 2 weeks;
- `v3` → 3 months;
- conditions: `LPS` and `RPMI`.

## Biological-unit and leakage contract

The biological grouping unit is the **donor**, not the cell.

Three folds were run:

1. Donor1 held out; Donor2 + Donor3 used for fitting;
2. Donor2 held out; Donor1 + Donor3 used for fitting;
3. Donor3 held out; Donor1 + Donor2 used for fitting.

Every fold contained 1,140 training cells and 570 held-out cells, with 285 LPS and 285 RPMI held-out cells.

Variance selection, scaling, PCA, and model fitting were performed using training donors only. No hyperparameter search was performed. A deliberately high-performing cell-random leakage fixture was rejected by the validator.

## Macro-average results

| Model | AUROC | Average precision | Balanced accuracy | Log loss |
|---|---:|---:|---:|---:|
| Prevalence | 0.5000 | 0.5000 | 0.5000 | 0.6931 |
| Visit metadata | 0.5000 | 0.5000 | 0.5000 | 0.6931 |
| `NFKBIA` only | **0.8098** | **0.8053** | **0.7532** | **0.5480** |
| Frozen inflammatory panel | **0.9989** | **0.9981** | **0.9912** | **0.0308** |
| Train-donor-only PCA state | **0.9992** | **0.9988** | **0.9994** | **0.0207** |
| Visit metadata + PCA state | **0.9992** | **0.9985** | **0.9994** | **0.0218** |

## Per-donor AUROC

| Held-out donor | `NFKBIA` only | Inflammatory panel | PCA state | Metadata + PCA |
|---|---:|---:|---:|---:|
| Donor1 | 0.7110 | 0.9971 | 0.9977 | 0.9975 |
| Donor2 | 0.8623 | 0.9999 | 1.0000 | 1.0000 |
| Donor3 | 0.8562 | 0.9998 | 1.0000 | 1.0000 |

## Interpretation

### 1. `NFKBIA` carries response-state information

`NFKBIA` alone separates LPS from RPMI above chance in every held-out donor. The effect is weaker for Donor1 and stronger for Donor2 and Donor3.

This supports only a descriptive statement: post-stimulation `NFKBIA` expression is associated with broad inflammatory response state across these three donors.

### 2. Broad state overwhelmingly outperforms the single gene

A fixed inflammatory panel and train-donor-only PCA nearly perfectly distinguish LPS from RPMI. Adding visit metadata to PCA does not improve the result.

The most defensible conclusion is therefore:

> The target is dominated by broad post-stimulation expression state; `NFKBIA` is an informative component, not a demonstrated unique driver.

This is consistent with the existing causal ranking in which shared upstream or broad cellular state is stronger than an identified `NFKBIA`-specific mechanism.

### 3. The task is intentionally easy and post-response

LPS versus RPMI classification asks whether the transcriptome contains the response to stimulation. Near-perfect broad-state discrimination is expected to be much easier than predicting a future response from a pre-stimulation state.

The high AUROC must not be presented as evidence that the original Live-seq forecasting problem is solved.

### 4. There are only three independent donors

The benchmark has 1,710 cells but only three biological grouping units. Cell-level metrics are useful for model behavior, but they do not create hundreds of independent human replications. Generalization beyond these donors remains uncertain.

## Geneformer status

```text
GENEFORMER_RUNTIME_HOLD
```

No Geneformer or BioNeMo inference was executed. No embedding was generated.

Before a foundation-model comparison is admissible, the project still requires:

- exact checkpoint and runtime/container;
- documented conversion of the official matrix to the required representation;
- exact cell-order binding before and after conversion;
- input and embedding SHA-256 values;
- parameters, seeds, hardware, and software;
- assessment of possible training-data overlap with GSE184241;
- a complete Model Evidence Passport;
- use of the identical frozen donor folds.

## Allowed claims

Supported with limits:

- LPS and RPMI post-response states are strongly separable in each held-out donor;
- `NFKBIA` alone is informative but substantially weaker than broad state;
- a fixed inflammatory panel and train-only PCA transfer strongly across these three donors;
- the dataset is structurally suitable for a future species-compatible Geneformer benchmark.

## Blocked claims

Not established:

- same-cell future-response prediction;
- prediction from a pre-stimulation state;
- `NFKBIA`-specific incremental value beyond broad state;
- an `NFKBIA` causal effect;
- independent validation beyond three donors;
- Geneformer improvement;
- clinical, diagnostic, treatment, or therapeutic relevance;
- authorization of physical biological work.

## Next valid comparison

Run a pass\-ported Geneformer embedding workflow on the exact same 1,710-cell identity set and the exact same donor folds, then compare:

```text
PCA_state
vs
Geneformer_embedding
vs
Geneformer_embedding + NFKBIA + visit metadata
```

The incremental comparison must be judged against the already near-ceiling PCA baseline. A high Geneformer score by itself would add little; the relevant question is whether it improves calibration, robustness, or held-out-donor performance without leakage and with transparent training-overlap risk.
