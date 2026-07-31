# TRACE archaic introgression 2026 evidence case

## Purpose

This case evaluates the 2026 TRACE study as a bounded computational-evidence package. TRACE stands for `TRacking Archaic Contributions via ARG Estimation` and uses features of ancestral recombination graphs inferred from present-day genomes to identify candidate archaic ancestry segments.

The current provisional result is:

```text
KAIROS_PARTIAL_COMPUTATIONAL_INFERENCE
NO_DIRECT_ARCHAIC_GENOME
FUNCTIONAL_ADAPTATION_UNRESOLVED
PROCESSED_DATA_PENDING
```

This is a research classification. It is not proof that remains or DNA from either unknown lineage were recovered, not a species assignment, not an ancestry-test interpretation, and not biological, experimental, medical, or clinical authorization.

## Primary sources

- Science DOI: `10.1126/science.aef8874`
- Preprint DOI: `10.64898/2026.03.03.709416`
- Preprint title: `Recovering signatures of archaic introgression using ancestral recombination graphs`
- Science online publication: `2026-07-30`
- TRACE code: `YulinZhang9806/trace`
- Manuscript analysis pipelines: `YulinZhang9806/trace_paper`

## What is supported

The public paper, preprint, institutional release, and code support the following bounded chain:

```text
present-day phased genomes
+ genomic masks and recombination maps
+ inferred ancestral recombination graphs
+ user-selected focal timescale
-> branch-length and haplotype-length features
-> hidden Markov model posterior
-> thresholded candidate introgressed segments
-> population and known-archaic overlap analyses
-> model-based ghost and super-archaic ancestry hypotheses
```

TRACE is designed to work without a sequenced genome from the unknown archaic source and without an assumed unadmixed modern-human outgroup. The authors report simulation validation and recovery of known Neanderthal and Denisovan signals under the tested settings.

## Main evidence boundary

The two unknown lineages are inferred latent sources. They are not directly observed ancient individuals.

The available evidence does not by itself establish:

- the taxonomic identity of either source population;
- that the ghost lineage was a single biologically homogeneous population;
- that every living person carries identical archaic segments or the same percentage;
- exact divergence or admixture dates independent of demographic and ARG assumptions;
- that enrichment near immunity or metabolic annotations caused an adaptive advantage;
- that all reported segments will survive independent reproduction with alternative ARG methods, masks, maps, thresholds, and demographic models.

## Important claim corrections

- `Detected in all sampled population groups` must not be rewritten as `the same segment exists in every person`.
- `About 0.5-1% per individual` is an author-reported estimate, not a universal constant.
- A lineage divergence estimate is not a fossil identification or species name.
- Super-archaic contribution in modern humans is inferred through Denisovan-associated regions; it is not direct sequencing of a 1.8-million-year-old genome.
- Functional enrichment is association-level evidence. Adaptive benefit requires variant-level functional and evolutionary validation.
- Recovery of known Neanderthal and Denisovan signals is a positive control, not complete proof that every newly inferred source model is uniquely identified.

## Kairos compatibility

This is an external computational-method evidence case, not a phase-conditioned cellular-transition case. It contains historical times and inferred admixture intervals, but no supported pre-intervention cellular phase variable. It therefore cannot unlock a `CANDIDATE_WINDOW` classification.

Kairos contributes by enforcing provenance, temporal ordering, model-boundary visibility, alternative-explanation checks, reproducibility gates, and fail-closed claim handling.

## Reproducibility blockers

At audit time, the TRACE package and manuscript pipelines are public, but the TRACE README marks processed data as under development. Full reproduction remains pending until the exact input datasets, masks, inferred ARGs or deterministic reconstruction instructions, parameter sets, environment lock, and expected output checksums are available and executed independently.

## Files

- `source-manifest.v0.1.json` — versioned source inventory and code pins
- `claim-map.v0.1.json` — atomic supported, inferred, unresolved, and rejected claims
- `causal-transition-map.v0.1.json` — inference chain, controls, confounders, and non-causal boundaries
- `phase-compatibility.v0.1.json` — Kairos domain and phase decision
- `reproducibility-contract.v0.1.json` — fail-closed reproduction requirements
- `disposition.v0.1.json` — machine-readable provisional result

## Update rule

The disposition may be strengthened only when exact evidence demonstrates one or more of the following:

- independent reproduction from pinned inputs and code;
- robustness across alternative ARG inference methods and demographic scenarios;
- calibrated false-discovery behavior on held-out simulations and known truth sets;
- stable segment calls under masks, maps, thresholds, and sample-composition perturbations;
- direct ancient DNA, proteins, or fossils that constrain source identity;
- variant-level functional evidence separating enrichment from adaptive causality.

No future update may silently convert computational ancestry inference into direct observation.
