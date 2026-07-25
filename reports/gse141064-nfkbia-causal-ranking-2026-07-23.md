# GSE141064 `Nfkbia` causal-hypothesis ranking

## Question

Does basal `Nfkbia` expression directly influence the later LPS-induced `Tnf-mCherry` response, or does the observed association arise from a broader cellular state, technical structure, marker behavior, a small context-specific effect, or sampling noise?

## Evidence imported without weakening

- Batch 8_8 contains 17 labelled cells.
- Exact biological independence is not established.
- Plate labels are technical library-preparation structures.
- Per-cell collection day and extraction round were not retained.
- Imaging-session equivalence remains incompletely resolved.
- GSE94383 shows a weak positive direction within its matched cell table, but its independent biological unit and ID-prefix semantics are unresolved.
- GSE94383 cell-level bootstrap, permutation, and prefix-exclusion outputs are descriptive sensitivity only.
- GSE94383 does not satisfy independent validation or direct temporal replication.
- No identifying intervention isolates a direct `Nfkbia` effect.

## Ranking formula

Inquiry priority is computed deterministically as:

```text
max(0,
  2*temporal_fit
+ 3*experimental_unit_fit
+ 2*cross_dataset_support
+ 3*confounder_resilience
+ 5*mechanistic_coherence
+ 5*intervention_support
+ 1*falsifiability
+ 4*effect_relevance
- 2*uncertainty_penalty)
```

The formula prioritizes what is most useful to investigate. It is not a probability of truth or causal identification.

## Corrected ranking

Cross-dataset support scores were reduced because GSE94383 cannot provide independent-unit inference while effective biological N is unresolved.

| Rank | Score | Hypothesis | Current status | Why it is here |
|---:|---:|---|---|---|
| 1 | 49 | Shared upstream cellular state | Supported explanation | Fits the target temporal order and explains covariance without requiring direct action; external evidence remains descriptive only. |
| 2 | 44 | Direct `Nfkbia` negative-feedback effect | Not identified | Mechanistically coherent and temporally possible, but lacks an identifying design, established experimental units, and accepted external validation. |
| 3 | 40 | State marker only | Plausible | `Nfkbia` may summarize inflammatory readiness without being load-bearing for the later response. |
| 4 | 37 | Small context-specific real effect | Plausible | A modest effect remains possible, but neither target nor external evidence estimates it on independent biological units. |
| 5 | 30 | Technical confounding | Plausible | Collection, extraction, imaging, and grouping structure may explain or amplify the 17-cell result. |
| 6 | 17 | Chance or overfitting | Plausible | Very small effective sample size and flexible analysis remain serious alternatives; GSE94383 does not independently weaken them. |

## Why rank 1 is not a winner

A top rank means **highest current inquiry priority**, not causal identification.

The causal-identification gate fails because:

- biological experimental units are not established;
- no intervention or equivalent identifying design is present;
- major confounders are not separable;
- accepted independent validation is absent;
- no direct temporally compatible external dataset is available.

## Highest-information comparisons

### Shared upstream state versus direct `Nfkbia` effect

A broader-state explanation is favored if a frozen multigene baseline-state model absorbs the `Nfkbia` association. A direct-effect explanation requires `Nfkbia`-specific evidence beyond that broader state and an identifying design.

### Direct effect versus marker only

Marker-only status is favored if `Nfkbia` becomes redundant after state adjustment. Direct action requires specific evidence that cannot be reproduced by comparable state markers.

### Biological state versus technical confounding

A biological explanation is strengthened if the association reproduces across independent biological collections with explicit technical lineage and balanced batch structure. Disappearance after technical adjustment favors confounding.

### Small real effect versus chance

Repeated modest same-direction estimates with biological-unit uncertainty favor a small real effect. Unstable, null, or directionally inconsistent estimates favor chance or overfitting.

## Verdict

```text
RANKED_NOT_IDENTIFIED
```

Supported with limits:

- an exploratory association in the observed GSE141064 cells;
- deterministic prioritization of competing explanations;
- descriptive pathway context within the GSE94383 table.

Not established or blocked:

- independent replication or conceptual triangulation from GSE94383;
- out-of-sample prediction;
- direct causal action of basal `Nfkbia`;
- generalization to independent biological units;
- tissue-level effects;
- clinical or therapeutic relevance.

## Next valid action

Find a dataset containing pre-stimulation transcriptomes linked to later inflammatory phenotypes with a source-backed independent unit, then run a frozen comparison of:

1. `Nfkbia`-only prediction;
2. broader baseline-state prediction;
3. explicit technical-confounder models.

If no suitable public dataset exists, retain the ranking as a bounded question set and prepare a non-operational evidence brief for an authorized partner laboratory.

## Safety boundary

This ranking is computational and documentary only. It does not authorize biological manipulation, human experimentation, treatment, or clinical decisions.
