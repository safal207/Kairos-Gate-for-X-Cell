# Model Card Template

> Complete this document for each trained predictive model. The current repository does not yet contain a validated biological model.

## Model identity

- Name:
- Version:
- Release date:
- Code commit:
- Training protocol version:
- Dataset identifiers and versions:
- License:
- Contact:

## Intended use

Describe the narrow research question, supported organisms, cell types, perturbations, horizons, and required input quality.

## Out-of-scope and prohibited use

- clinical diagnosis, treatment, or patient-level decisions;
- experiment authorization;
- claims of rejuvenation, longevity, or therapeutic efficacy;
- extrapolation to untested species, tissues, cell types, doses, or perturbations;
- interpreting `CANDIDATE_WINDOW` as biological safety.

## Inputs and outputs

Document every input field, whether it is measured or inferred, its units, confidence, timestamp, and provenance. Define output semantics and uncertainty.

## Training and evaluation

- architecture and initialization;
- objective and optimization;
- train/validation/test split strategy;
- leakage controls;
- random seeds;
- baseline model;
- phase ablation;
- phase shuffle control;
- held-out metrics;
- calibration metrics.

## Stratified evaluation

Report performance by, where available:

- cell type and donor;
- perturbation and dose;
- biological phase;
- batch and replicate;
- time horizon;
- in-distribution versus out-of-distribution status.

Do not report only an aggregate average when a subgroup has materially worse behavior.

## Limitations and failure modes

Describe distribution shift, missingness, phase-inference error, confounding, proxy use, uncertainty, and known cases of confident error.

## Causal boundary

Improved held-out prediction demonstrates predictive usefulness only. Causal timing requires controlled or appropriately designed quasi-experimental evidence.

## Safety and governance

State the human review requirements, evidence retention, model-change process, and the fact that technical validation does not authorize wet-lab, animal, human, or clinical work.