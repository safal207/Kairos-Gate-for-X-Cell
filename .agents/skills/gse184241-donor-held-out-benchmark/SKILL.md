# GSE184241 donor-held-out benchmark

## Purpose

Test human single-cell response-state representations on GSE184241 without treating cells as independent biological replication units and without misdescribing cross-sectional cells as a same-cell future-response design.

## Frozen scientific boundary

GSE184241 contains CD14 monocytes from three human donors, sampled at day 0, 2 weeks, and 3 months, under LPS and RPMI conditions. Different cells are measured in each sample.

Allowed question:

> Can a representation discriminate LPS versus RPMI response state in a donor that was entirely excluded from model fitting?

Blocked question:

> Can the pre-stimulation molecular state of an individual cell predict that same cell's later response?

## Biological split contract

The biological grouping unit is `donor`.

Required folds:

- train Donor2 + Donor3, test Donor1;
- train Donor1 + Donor3, test Donor2;
- train Donor1 + Donor2, test Donor3.

A cell-random split is prohibited.

The held-out donor must not contribute to:

- gene filtering or variance ranking;
- scaling parameters;
- PCA or other representation fitting;
- hyperparameter selection;
- calibration;
- threshold selection;
- feature selection;
- early stopping.

## Model families

The comparison floor is frozen before any Geneformer result is inspected:

1. training prevalence;
2. visit metadata only;
3. `NFKBIA` only;
4. fixed inflammatory-gene panel;
5. train-donor-only PCA expression state;
6. visit metadata plus PCA state;
7. Geneformer cell embeddings;
8. Geneformer plus `NFKBIA` and permitted metadata.

## Primary target

Binary discrimination of `LPS` versus `RPMI`.

Metrics must be reported separately for every held-out donor and macro-averaged across donors:

- AUROC;
- average precision;
- balanced accuracy at the frozen 0.5 threshold;
- log loss.

With three donors, results are descriptive and uncertainty is large. Cell count must not be used to imply three-independent-donor evidence is equivalent to hundreds of biological replicates.

## Geneformer execution gate

A Geneformer result is admissible only when all are present:

- exact provider and model/checkpoint;
- exact BioNeMo runtime or container;
- input-conversion artifact and hash;
- cell-order binding before and after conversion;
- embedding artifact and hash;
- parameters, seeds, hardware, and software;
- training-data overlap assessment;
- Model Evidence Passport;
- the same frozen donor folds used by baseline models.

Without those fields, use `GENEFORMER_RUNTIME_HOLD`.

## Claim boundary

May support, with limits:

- human-domain response-state representation;
- descriptive transfer to a held-out donor;
- incremental model-comparison evidence if the Geneformer gate passes.

Must not support:

- same-cell future-response prediction;
- an `NFKBIA`-specific biological effect beyond broader state;
- causal identification;
- clinical prediction;
- treatment or therapeutic claims;
- authorization of physical biological work.

## Fail-closed conditions

Return `BLOCK` when any of the following occurs:

- cell-random split is used;
- a held-out donor contributes to preprocessing or tuning;
- donor identity is missing or inferred after outcome inspection;
- model families or metrics are changed after results are seen;
- Geneformer is claimed without exact identity and passport evidence;
- response-state classification is described as same-cell prediction;
- causal, clinical, or therapeutic claims are authorized.
