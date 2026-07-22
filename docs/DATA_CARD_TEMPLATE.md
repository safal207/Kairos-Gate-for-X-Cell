# Data Card Template

> Complete this document for each dataset used in training, evaluation, or evidence generation.

## Dataset identity

- Dataset ID:
- Version:
- Persistent identifier or source URL:
- License and redistribution terms:
- Maintainer:
- Created or accessed date:
- Content digest:

## Provenance class

Mark each relevant field as:

- `measured`;
- `inferred`;
- `synthetic`;
- `unavailable`.

State explicitly whether biological phase was directly measured, inferred from expression, assigned by protocol, or generated synthetically.

## Biological scope

- organism;
- tissue or cell context;
- donor or line information;
- perturbation type, target, dose, and duration;
- collection timepoints;
- phase measurement or inference method;
- response measurements;
- batch and replicate identifiers.

## Collection and processing

Document acquisition, inclusion and exclusion rules, quality control, normalization, feature selection, transformations, imputation, and any post-intervention fields removed from baseline features.

## Splits and leakage controls

- train/validation/test identifiers;
- held-out replicate, perturbation, or cell context;
- duplicate and near-duplicate checks;
- confirmation that post-intervention data do not enter pre-intervention phase features.

## Missingness and bias

Describe missing fields, class imbalance, donor and batch imbalance, selection effects, measurement error, phase-inference uncertainty, and known underrepresented groups.

## Intended use

Define the exact benchmark or research question for which the dataset is suitable.

## Prohibited interpretations

- synthetic data are not biological observations;
- inferred phase is not equivalent to direct measurement;
- absence of a toxicity signal is not proof of safety;
- predictive association is not causal evidence;
- the dataset does not authorize experiments or clinical decisions.

## Changes from prior version

List row, field, preprocessing, annotation, license, and split changes. A materially changed dataset receives a new version and digest.