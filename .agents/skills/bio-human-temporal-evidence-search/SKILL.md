# bio-human-temporal-evidence-search

## Purpose

Find and classify public human monocyte/macrophage evidence for the frozen question:

```text
pre-stimulation molecular state
        ↓ same cell or defensible longitudinal biological unit
inflammatory transition
        ↓
later response phenotype
```

The skill must preserve the difference between human-domain relevance and direct temporal replication.

## Non-negotiable direct-candidate gates

A `DIRECT_TEMPORAL_CANDIDATE` requires all of the following:

1. `Homo sapiens` monocytes or macrophages.
2. Molecular pre-state measured before the inflammatory transition.
3. Later response phenotype measured after the transition.
4. Same-cell identity, retained lineage, or a defensible longitudinal biological unit that supports the frozen claim.
5. Independent biological units explicitly identified.
6. Collection, stimulation, imaging, library, batch, and run lineage sufficient to separate technical effects.
7. Public data sufficient for a frozen analysis plan.

No criterion may be weakened to manufacture an accepted candidate.

## Candidate classes

- `DIRECT_TEMPORAL_CANDIDATE`
- `DONOR_LEVEL_TEMPORAL_SUPPORT`
- `SINGLE_CELL_POST_RESPONSE_SUPPORT`
- `HUMAN_DOMAIN_REFERENCE`
- `METHOD_TRANSFER_ONLY`
- `CROSS_SECTIONAL_SUPPORT`
- `EXCLUDE`

## Required global verdicts

- `HUMAN_DIRECT_REPLICATION_FOUND`
- `HUMAN_DIRECT_REPLICATION_GAP`

## Interpretation rules

- Repeated sampling from the same donor is longitudinal donor-level evidence, not same-cell evidence.
- Single-cell RNA measured only after stimulation is post-response support, not a baseline predictor.
- Separate aliquots from one donor do not establish same-cell linkage.
- An accession, plate, chip, field, well, library, run, or cell-ID prefix is not a biological replicate unless an authoritative source establishes that meaning.
- A human dataset can be suitable for foundation-model compatibility testing while remaining ineligible for direct biological replication.
- A model embedding cannot repair missing temporal identity or experimental-unit metadata.

## GSE94383 prefix rule

The GSE94383 cell-ID prefixes may be used for technical sensitivity analysis, but not as biological groups. GEO documents a separate condition/ID mapping and partitions cells by stimulation/time samples; no authoritative source located in this search establishes the prefixes as independent biological units. The safe status is:

```text
TECHNICAL_OR_CONDITION_PREFIX
EXACT_SUBFIELD_MAPPING_UNRESOLVED
NOT_A_BIOLOGICAL_REPLICATE
```

## Required output

Produce:

- search date and repositories;
- frozen queries;
- candidate registry;
- per-candidate gate results;
- explicit exclusions;
- global verdict;
- refreshed partner-laboratory evidence requirement;
- claim boundary and safety boundary.

## Safety boundary

This skill is computational and documentary only. It does not provide experimental procedures, authorize physical biological work, or support clinical decisions.