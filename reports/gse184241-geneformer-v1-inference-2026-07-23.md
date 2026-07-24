# GSE184241 Geneformer V1 inference and superseding evidence ledger

**Date:** 2026-07-23  
**Execution status:** `GENEFORMER_INFERENCE_COMPLETED_REPORT_ONLY`  
**Compatibility verdict:** `HOLD_TRAINING_OVERLAP`  
**Scope:** frozen public-data CPU inference, donor-held-out descriptive comparison, and temporary LiminalDB replay only

## Question

Can the exact public `Geneformer-V1-10M` checkpoint produce deterministic cell embeddings for the frozen GSE184241 input contract, and do those embeddings improve the existing leakage-safe donor-held-out comparison?

This workflow evaluates post-response LPS-versus-RPMI state discrimination in different cells. It is not same-cell future-response prediction and does not directly replicate the Live-seq temporal claim.

## Frozen result

```text
GENEFORMER_INFERENCE_COMPLETED_REPORT_ONLY
HOLD_TRAINING_OVERLAP
EMBEDDINGS_GENERATED_1710_BY_256
DESCRIPTIVE_COMPARISON_COMPLETED
INCREMENTAL_VALUE_NOT_ESTABLISHED
RECOVERED_REPORT_ONLY
```

Geneformer embeddings were highly informative, but the frozen train-donor-only PCA baseline remained slightly stronger on all four macro metrics.

## Exact implementation evidence source

```text
Kairos Gate implementation head:
c9d99c40a464df55addd4b044d6e9c1c6f39d5fa

Geneformer workflow run:
30044044341

Exact-head artifact:
8578592391

Artifact archive digest:
sha256:819f5d08c69c1d84bd8def7ddf3a9c0c2d1485d369f10d05096b6e7729758049
```

This report is added by a later documentation commit. The final unchanged PR-head workflow identifiers are therefore maintained in PR #41 metadata after the final rerun rather than self-referentially embedded as this file's own commit SHA.

## Exact input identity

```text
accession: GSE184241
organism: Homo sapiens
raw matrix: 23,895 genes × 1,710 cells
retained cells: 1,710
independent donors: 3
same-cell longitudinal identity: false

counts SHA-256:
8e2482438215dc48ead81fa97a10a57ddf11633c83384dd3b11fbe39cb60830d

barcode workbook SHA-256:
806c5b2ecb11cb4ec7a66d42608fddfb920722cbc53b23a9c000085391bb47dd

cell-order SHA-256:
80635c36b2853b94676f2f4c90419f077a297a7d81f6a93d7a6aa34fe76197df

cell-identity set SHA-256:
9eae3e5793704ed478a80fb77d2d8257b4712d534ace4e50d7258a1e05b093ea
```

The independent identity diagnostic observed 1,710 count-matrix IDs and 1,710 workbook IDs with no missing values in either direction.

## Exact model identity

```text
repository: ctheodoris/Geneformer
revision: 04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5
checkpoint: Geneformer-V1-10M
max positions: 2048
hidden size: 256
hidden layers: 6
embedding layer: second-to-last
pooling: mean over non-padding gene tokens
special tokens: none
```

Exact asset identities:

| Asset | Size | SHA-256 |
|---|---:|---|
| `Geneformer-V1-10M/config.json` | 565 B | `9cf69ca3bdb0215c4188b54c451b6f02adfe68b8f66011a57d0f32845133fd4b` |
| `Geneformer-V1-10M/model.safetensors` | 41,183,536 B | `a5e33a757431643b3697de7ef6127950cdc49e06e58d4266b3a3ab191b683f14` |
| `ensembl_mapping_dict_gc30M.pkl` | 584,125 B | `eac0fb0b3007267871b6305ac0003ceba19d4f28d85686cb9067ecf142787869` |
| `gene_median_dictionary_gc30M.pkl` | 940,965 B | `b3b589bb5ec75040d05fc44dd6bf0184cf87f3c362cf158d196a6ed3b7fe5f39` |
| `gene_name_id_dict_gc30M.pkl` | 1,117,117 B | `55e67962e79c0039a6c32d43c5c99f38e51964bbcfa32f736150ee1e285c438c` |
| `token_dictionary_gc30M.pkl` | 788,424 B | `ab9dc40973fa5224d77b793e2fd114cacf3d08423ed9c4c49caf0ba9c7f218f1` |

## Tokenization evidence

Raw counts reached Geneformer tokenization without feature selection.

```text
input genes: 23,895
mapped canonical V1 genes: 18,914
unmapped symbols: 2,882
mapped but absent from V1 vocabulary: 2,099
duplicate canonical groups: 0
cells tokenized: 1,710
sequence length minimum: 294
sequence length median: 1,972.5
sequence length maximum: 2,048
cells truncated to 2,048: 792
maximum detected V1 genes before truncation: 10,444
normalization target sum: 10,000
```

```text
canonical gene-order SHA-256:
7da118eda5a663478a6c8476c661be229e23db8a17d1f9d852223190a5d23459

token artifact SHA-256:
5c92d7c513b76522486ddc09196804e0833757917c0849946c6823e841e1f73b
```

The retained token artifact has shape `1,710 × 2,048`, dtype `int32`, and carries the exact cell order and per-cell token lengths.

## Embedding evidence

```text
shape: 1,710 × 256
dtype: float32
all values finite: true
batch size: 4
device: CPU
hidden-state index: -2
pooling: mean_nonpadding_gene_tokens

embedding artifact SHA-256:
cc50d2eed1efa21de26c131d476ec2027dbfda9a6bd38d0e898673259df4e4aa
```

Two independent execution paths were compared:

1. full `BertForMaskedLM` forward, including the unused MLM vocabulary head;
2. base BERT encoder forward with the vocabulary head skipped.

They produced:

```text
input token IDs exact equal: true
token lengths exact equal: true
cell order exact equal: true
embedding arrays exact equal: true
maximum absolute embedding difference: 0.0
all donor-fold metrics exact equal: true
```

The encoder-only path reduced observed inference time on the hosted CPU runner from approximately 755 seconds to approximately 400 seconds without changing one embedding value.

## Donor-held-out results

Each fold trains on two donors and tests on the third donor. Scaling and the fixed logistic probe are fit on training donors only.

### Geneformer fold metrics

| Held-out donor | AUROC | Average precision | Balanced accuracy | Log loss |
|---|---:|---:|---:|---:|
| Donor1 | 0.995088 | 0.981797 | 0.984211 | 0.100892 |
| Donor2 | 0.999249 | 0.999300 | 0.989474 | 0.032191 |
| Donor3 | 0.999791 | 0.999798 | 0.994737 | 0.027415 |
| **Macro mean** | **0.998042** | **0.993632** | **0.989474** | **0.053499** |

### Frozen baseline comparison

| Model | AUROC | Average precision | Balanced accuracy | Log loss |
|---|---:|---:|---:|---:|
| `NFKBIA_only` | 0.809806 | 0.805284 | 0.753216 | 0.548004 |
| `inflammatory_panel` | 0.998941 | 0.998080 | 0.991228 | 0.030848 |
| `PCA_state` | 0.999237 | 0.998775 | 0.999415 | 0.020702 |
| `Geneformer_V1_embedding` | 0.998042 | 0.993632 | 0.989474 | 0.053499 |

Geneformer minus PCA-state descriptive differences:

```text
AUROC:             -0.001194
average precision: -0.005143
balanced accuracy: -0.009942
log loss:          +0.032797
```

For log loss, lower is better. The positive difference is therefore also unfavorable to Geneformer.

## Scientific interpretation

The evidence supports:

- exact checkpoint execution on all 1,710 retained cells;
- deterministic tokenization and deterministic `1,710 × 256` embeddings;
- strong donor-held-out discrimination of LPS versus RPMI response states;
- substantial improvement over the `NFKBIA`-only baseline;
- a result close to, but not better than, the frozen inflammatory-panel and PCA-state baselines.

The evidence does **not** establish incremental value for Geneformer over the frozen PCA-state ceiling. The observed comparison uses only three independent donors and remains descriptive.

Training overlap with GSE184241 or closely related data was not independently excluded. The Model Evidence Passport therefore remains:

```text
compatibility_verdict: HOLD_TRAINING_OVERLAP
training_overlap_status: unknown
execution_status: completed
```

## Model Evidence Passport

```text
input manifest SHA-256:
dc2a0b11c68358a65d8d62c56097de9660cd439d972a17967400b5a6d7147a52

Model Evidence Passport SHA-256:
e802f829e95f773a040ed2457497794aaef177a22016b14c0e6cab5396db6785

inference result SHA-256:
9c8c13390d533afe299d2f3677a48303369d5198217ad1e33ff783d52ce486bf
```

## Superseding LiminalDB transition

The inference creates a new authorization. It does not reuse the preflight-only authorization.

```text
relation: SUPERSEDES
predecessor transition:
gse184241-geneformer-runtime-preflight-v0-1

predecessor authorization:
sha256:550df034e0eceb773ef69d2de8a9fbb9bb48b092a2b6bdee8a53988764eb0665

new current authorization:
sha256:8bc51d6438534539870054de4f8e5f79d1c0895d99e671276fa323d9421203a4
```

Seven records were appended:

```text
authorization
-> frozen benchmark observation
-> model/input/token observation
-> inference/passport observation
-> response integrity
-> causal audit
-> continuity snapshot
```

Final independent dimensions:

```text
authority: VALID
execution: OBSERVED_EXECUTED
response_integrity: VERIFIED
causal_validity: NOT_EVALUATED
continuity_posture: REPORT_ONLY
side_effect_committed: false
```

## Authority-escalation negative test

The deterministic negative fixture attempted to:

- replace a current observation's authorization with the predecessor authorization;
- claim established incremental value;
- claim causal validity;
- grant production persistence;
- continue a side effect.

The validator returned `BLOCK` with nine independent errors, including predecessor-authority substitution, invalid causal dimensions, production-write escalation, and side-effect commitment.

## WAL, snapshot, and replay proof

The exact pinned LiminalDB implementation appended the seven records to a temporary WAL, wrote a digest-bound snapshot, closed the ledger, reopened it, and reproduced an identical projection.

```text
LiminalDB commit:
ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d

semantic bundle digest:
sha256:ba6e1052f1a099f9744200d2114625a234e58c561efab2b7f71e982db0fc4a43

exact bundle-file SHA-256:
a0529778f831f3b58d898553f5964c6c1c46a8a787efff938ee3d74739d1c41d

snapshot digest:
sha256:b10c94e18667d53d11125255b2e7010e99c5fd000986a5181ac255e3ae24aff3

final semantic event:
sha256:9076c755db752750a8c1f875a855f9724d79538e9fc3c772bce939e526c444b3

replay receipt file SHA-256:
9b688f4943b20974ca4d30ef4745bc366442bff8cca3d0c08d781852d719f558

events before reopen: 7
events after reopen: 7
snapshot event count: 7
projection count: 1
projection equal after reopen: true
verdict: RECOVERED_REPORT_ONLY
```

No live or production LiminalDB node was contacted.

## Claim boundary

Blocked regardless of metric performance:

- established incremental value;
- same-cell future-response prediction;
- direct temporal replication of Live-seq;
- an `NFKBIA`-specific causal effect;
- clinical, diagnostic, treatment, or therapeutic utility;
- physical biological execution;
- production LiminalDB persistence;
- external submission, deployment, or merge authority.

## Durable conclusion

```text
GENEFORMER_CHECKPOINT_EXECUTED
TOKENIZATION_AND_EMBEDDINGS_EXACTLY_REPRODUCED
FOUNDATION_MODEL_SIGNAL_STRONG
FROZEN_PCA_STATE_BASELINE_REMAINS_STRONGER
INCREMENTAL_VALUE_NOT_ESTABLISHED
TRAINING_OVERLAP_UNKNOWN
REPORT_ONLY
```
