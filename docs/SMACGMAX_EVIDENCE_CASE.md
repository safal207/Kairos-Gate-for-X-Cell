# smACGmax 2026 evidence case

## Purpose

This case evaluates the 2026 `smACGmax` report as a bounded Kairos Gate evidence case. It asks whether the public article package supports:

1. an auditable perturbation-to-allele-to-phenotype transition record; and
2. a valid phase-conditioned comparison based on a measurable variable recorded before intervention.

The current answer is:

```text
KAIROS_PARTIAL_NO_PREINTERVENTION_PHASE
```

This is a provisional research classification. It is not experiment authorization, clinical advice, a safety conclusion, or an independent replication.

## Primary source

- DOI: `10.1038/s41467-026-76020-6`
- Published: `2026-07-27`
- Current publisher status at audit time: unedited early-access manuscript
- Publisher package: article, supplementary information, five supplementary spreadsheets, reporting summary, transparent peer review, and source data

Publisher-hosted binary files are not committed. The repository records source URLs, roles, retrieval state, and later cryptographic digests.

## Current evidence boundary

The public article abstract and peer-review record support a structured chain:

```text
cell context
+ smACGmax construct
+ guide and sequence context
+ dose / duration
-> single-, double- and triple-edit allele distribution
-> selection
-> enriched population
-> survival or splicing phenotype
```

However, the inspected sources do not yet establish a valid biological phase measured before editing. Collection time, guide identity, sequence context, or post-selection state cannot substitute for a Kairos phase variable.

## Important claim corrections

- `up to 41%` is a maximum and must not be reported as the typical rate.
- The peer-review response reports a 0.3-28% range and 5.5% mean for triple alleles across 71 HBEGF sites; this still requires source-data recalculation.
- Guanine editing retains an NGR-context preference.
- Priority claims were removed after parallel triple-editor reports appeared.
- The paper was reframed from universal saturation to high-diversity combinatorial mutagenesis.
- Enrichment after toxin selection is not automatically a one-allele causal proof without allele-to-phenotype linkage.

## Files

- `source-manifest.v0.1.json` — publisher source package and retrieval status
- `claim-map.v0.1.json` — atomic claims, limitations and verification levels
- `causal-transition-map.v0.1.json` — intervention, selection and confounder graph
- `phase-compatibility.v0.1.json` — Kairos phase admission decision
- `disposition.v0.1.json` — machine-readable provisional result

## Reproducing the source inventory

Run in a network-enabled environment:

```bash
python scripts/audit_smacgmax_sources.py \
  --manifest evidence/smacgmax-2026/source-manifest.v0.1.json \
  --output evidence/smacgmax-2026/source-digests.local.json
```

The generated digest file is local evidence and should be reviewed before commit. Publisher binaries remain outside the repository.

## Update rule

The primary status may change only when exact evidence demonstrates:

- a supported phase variable;
- measurement before intervention;
- auditable sample linkage;
- source-backed replicate semantics; and
- a leakage-resistant comparison contract.

A positive predictive result would establish predictive usefulness only, not causal timing, therapeutic value, biological safety, or clinical validity.
