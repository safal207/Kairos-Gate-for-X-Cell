---
name: gse184241-geneformer-v1-inference
description: Execute or fail closed on an exact Geneformer V1 10M CPU inference over frozen GSE184241 raw counts, compare fixed cell embeddings on donor-held-out folds, issue a Model Evidence Passport, and persist a superseding report-only LiminalDB transition.
version: 0.1.0
---

# GSE184241 Geneformer V1 Inference

Use this skill only for the bounded public GSE184241 post-response state-discrimination task.

## Frozen scientific question

Does a fixed `Geneformer-V1-10M` cell embedding provide a useful descriptive donor-held-out representation for distinguishing LPS from RPMI cells compared with the existing frozen baselines?

This is **not** same-cell future-response prediction and does not directly replicate the Live-seq temporal claim.

## Exact sources

- GSE184241 raw processed count matrix and barcode workbook from GEO.
- Geneformer repository: `ctheodoris/Geneformer`.
- exact revision: `04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5`.
- checkpoint: `Geneformer-V1-10M`.
- V1 30M median, token, gene-name and Ensembl-mapping dictionaries.
- frozen comparison artifact: `examples/gse184241.donor-held-out-benchmark.json`.

Any source, checkpoint, dictionary, input digest, cell identity or fold drift is a HOLD.

## Input and tokenization contract

- preserve the exact 1,710 nonzero-library cells and exact cell order;
- biological generalization unit is donor, not cell;
- use raw counts before any feature selection;
- map gene symbols to canonical V1 Ensembl IDs through the pinned dictionaries;
- sum duplicate mapped genes;
- normalize each detected gene by `raw_count / n_counts * 10000 / gene_median`;
- rank detected genes descending with a stable sort;
- truncate at V1 input size 2048;
- add no CLS or EOS tokens;
- retain token lengths and exact token artifact digest.

PCA, variable-gene selection and scaling from the baseline are comparators only. They must not alter Geneformer input.

## Inference contract

- load only local files downloaded at the exact pinned revision;
- require max positions 2048, hidden size 256 and six hidden layers;
- run deterministic evaluation-only CPU inference;
- use the second-to-last hidden state;
- mean-pool only non-padding gene tokens;
- bind embeddings to exact cell order;
- preserve checkpoint, dictionary, token and embedding file hashes.

## Benchmark contract

- use the same three leave-one-donor-out folds as the frozen benchmark;
- train scaling and a fixed logistic probe on training donors only;
- do not use cell-random splits or tune hyperparameters on held-out donors;
- compare metrics with prevalence, visit, `NFKBIA`, inflammatory-panel and train-donor-only PCA baselines;
- treat all metric differences as descriptive because only three donors exist.

## Model Evidence Passport

Every completed or held attempt must emit a passport compatible with `model-evidence-passport.schema.json` and preserve:

- exact run and code identity;
- model and checkpoint identity;
- input and output digests;
- execution parameters, seeds, hardware and software;
- transformations;
- training-overlap status and limitations;
- causal and clinical boundaries;
- physical-biology and clinical-use denials.

A completed inference remains `HOLD_TRAINING_OVERLAP` unless overlap is independently excluded by evidence stronger than public metadata.

## Superseding LiminalDB transition

The inference transition is a new authorization epoch.

```text
relation: SUPERSEDES
predecessor_transition_id: gse184241-geneformer-runtime-preflight-v0-1
predecessor_authorization_ref: sha256:550df034e0eceb773ef69d2de8a9fbb9bb48b092a2b6bdee8a53988764eb0665
```

`links.authorization_ref` on every new record must point only to the new inference authorization. The predecessor authorization is ancestry, not current authority.

The seven-record chain is:

```text
authorization
  -> frozen benchmark observation
  -> model/input/token observation
  -> inference/passport observation
  -> response integrity
  -> causal audit
  -> continuity snapshot
```

## Allowed outcomes

```text
GENEFORMER_INFERENCE_COMPLETED_REPORT_ONLY
HOLD_INPUT_CONTRACT
HOLD_CHECKPOINT_IDENTITY
HOLD_TOKENIZATION
HOLD_RUNTIME_RESOURCE
HOLD_TRAINING_OVERLAP
BLOCK_AUTHORITY_OR_CLAIM_ESCALATION
```

Expected HOLD states are valid durable results. Do not turn missing execution into a completed inference claim.

## Claim boundary

Even when checkpoint execution and embedding generation complete, block:

- established incremental value;
- same-cell future-response prediction;
- `NFKBIA`-specific causality;
- direct temporal replication;
- clinical, diagnostic, treatment or therapeutic utility;
- physical biological execution;
- production LiminalDB write;
- deployment, external submission or merge authority.

## Storage boundary

Counts, checkpoint files, tokens and embeddings remain workflow artifacts or object storage. The LiminalDB bridge stores digest-bound references in a temporary ledger only.
