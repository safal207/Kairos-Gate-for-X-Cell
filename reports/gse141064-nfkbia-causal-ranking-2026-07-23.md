# GSE141064 `Nfkbia` causal-hypothesis ranking

## Question

Does basal `Nfkbia` expression directly influence the later LPS-induced `Tnf-mCherry` response, or does the observed association arise from a broader cellular state, technical structure, marker behavior, a small context-specific effect, or sampling noise?

## Evidence imported without weakening

- Batch 8_8 contains 17 labelled cells.
- Exact biological independence is not established.
- Plate labels are technical library-preparation structures.
- Per-cell collection day and extraction round were not retained.
- Imaging-session equivalence remains incompletely resolved.
- GSE94383 independently supports weak same-cell coupling between prior NF-kB activity and post-LPS `Nfkbia` expression.
- GSE94383 is conceptual pathway triangulation, not direct temporal replication.
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

## Ranking

| Rank | Score | Hypothesis | Current status | Why it is here |
|---:|---:|---|---|---|
| 1 | 53 | Shared upstream cellular state | Supported explanation | Fits the target temporal order, has pathway-level support from GSE94383, and explains covariance without requiring direct action. |
| 2 | 46 | Direct `Nfkbia` negative-feedback effect | Not identified | Mechanistically coherent and temporally possible, but has no identifying intervention, established experimental unit, or direct external replication. |
| 3 | 44 | State marker only | Plausible | `Nfkbia` may summarize inflammatory readiness without being load-bearing for the later response. Its component scores dominate the small-effect hypothesis on temporal fit and falsifiability. |
| 4 | 41 | Small context-specific real effect | Plausible | Conceptual post-stimulation coupling is compatible with a modest effect, but it does not establish a small pre-state-to-later-phenotype effect in the frozen target claim. |
| 5 | 32 | Technical confounding | Plausible | Collection day, extraction round, and imaging structure are incompletely known and may explain or amplify the 17-cell result. |
| 6 | 19 | Chance or overfitting | Weakened | The target dataset is extremely small, but independent pathway triangulation makes a pure arbitrary-feature explanation less likely. |

## Why rank 1 is not a winner

A top rank means **highest current inquiry priority**, not causal identification.

The causal-identification gate currently fails because:

- biological experimental units are not established;
- no intervention or equivalent identifying design is present;
- major confounders are not separable;
- direct independent validation is absent;
- the strongest external dataset has a different temporal structure.

## Highest-information comparisons

### Shared upstream state versus direct `Nfkbia` effect

A broader-state explanation is favored if a frozen multigene baseline-state model absorbs the `Nfkbia` association. A direct-effect explanation requires `Nfkbia`-specific evidence beyond that broader state and an identifying design.

### Direct effect versus marker only

Marker-only status is favored if `Nfkbia` becomes redundant after state adjustment. Direct action requires specific evidence that cannot be reproduced by comparable state markers.

### Biological state versus technical confounding

A biological explanation is strengthened if the association reproduces across independent biological collections with explicit technical lineage and balanced batch structure. Disappearance after technical adjustment favors confounding.

### Small real effect versus chance

Repeated modest same-direction estimates under frozen analysis favor a small real effect. Unstable, null, or directionally inconsistent estimates favor chance or overfitting.

## Verdict

```text
RANKED_NOT_IDENTIFIED
```

Supported with limits:

- an exploratory association in the observed GSE141064 cells;
- independent conceptual coupling of NF-kB activity and post-LPS `Nfkbia` expression in GSE94383;
- deterministic prioritization of competing explanations.

Not established or blocked:

- out-of-sample prediction;
- direct causal action of basal `Nfkbia`;
- generalization to independent biological units;
- tissue-level effects;
- clinical or therapeutic relevance.

## Next valid action

Find an independent dataset containing pre-stimulation transcriptomes linked to later inflammatory phenotypes, then run a frozen comparison of:

1. `Nfkbia`-only prediction;
2. broader baseline-state prediction;
3. explicit technical-confounder models.

If no suitable public dataset exists, prepare a non-operational evidence brief for an authorized partner laboratory. The brief should specify the competing hypotheses and required distinguishing evidence without including physical experimental procedures.

## Safety boundary

This ranking is computational and documentary only. It does not authorize biological manipulation, human experimentation, treatment, or clinical decisions.
