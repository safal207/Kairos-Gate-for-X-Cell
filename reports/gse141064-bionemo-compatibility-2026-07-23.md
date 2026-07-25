# GSE141064 BioNeMo compatibility report

Date: 2026-07-23  
Scope: computational model selection and evidence governance only

## Frozen scientific question

Can basal `Nfkbia` or a broader pre-LPS state predict the later `Tnf-mCherry` response of the same cell?

## Model decisions

| Tool or model | Role | Current verdict | Reason |
|---|---|---|---|
| NVIDIA BioNeMo Agent Toolkit | Agent orchestration | `ACCEPT_WITH_LIMITS` | It can expose documented callable scientific tools, but orchestration alone adds no biological evidence. |
| Geneformer-V2-104M | Human single-cell representation | `SPECIES_COMPATIBILITY_HOLD` | GSE141064 is `Mus musculus`; the documented checkpoint is trained on human single cells. No validated RAW264.7 transfer contract is available. |
| Evo 2 NIM 2.1.0 | DNA sequence model | `QUESTION_NOT_APPLICABLE` | The frozen question concerns basal RNA state and later phenotype, not a DNA-sequence hypothesis. |
| ESM-2 | Protein representation | `QUESTION_NOT_APPLICABLE` | No protein-level bridge or outcome is frozen. |
| AMPLIFY | Protein representation | `QUESTION_NOT_APPLICABLE` | No protein-level bridge or outcome is frozen. |

## Geneformer mouse decision

The input and model share the single-cell modality, but modality agreement is not enough.

```text
single-cell RNA modality compatible
            +
human training domain vs mouse RAW264.7
            +
unvalidated ortholog/token transfer
            +
unresolved biological-unit independence
            =
SPECIES_COMPATIBILITY_HOLD
```

Ortholog mapping may be explored only after a separate transfer-validation plan is frozen. Mapping mouse genes to human identifiers does not make mouse cell states human and does not establish preserved embedding geometry, predictive calibration, or biological meaning.

## Evidence boundary

Allowed now:

- model and input compatibility documentation;
- registry and runtime discovery;
- metadata-only passport demonstration;
- search for a compatible human longitudinal dataset;
- planning a cross-species sensitivity analysis without treating it as validation.

Blocked now:

- Geneformer-derived evidence promotion for GSE141064;
- claims that embeddings validate `Nfkbia` prediction;
- causal identification;
- tissue, clinical, or therapeutic interpretation;
- physical biological execution authorization.

## Highest-information next actions

1. Find an independent human monocyte/macrophage dataset with pre-state RNA and linked later inflammatory phenotype.
2. Resolve training and benchmark overlap for any chosen dataset.
3. Compare candidate-only, broader-state, technical and combined models on independent biological units.
4. Treat any mouse-to-human transfer as a separate validation problem with explicit information-loss and calibration tests.

## Safety status

```text
COMPUTATIONAL_DOCUMENTARY_ONLY
PHYSICAL_BIOLOGY_NOT_AUTHORIZED
CLINICAL_USE_NOT_AUTHORIZED
```
