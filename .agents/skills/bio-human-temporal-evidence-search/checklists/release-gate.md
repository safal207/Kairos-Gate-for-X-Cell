# Release gate: human temporal evidence search v0.2

Release only when every item passes.

## Search integrity

- [ ] Search date is explicit.
- [ ] Repositories and primary-source URLs are recorded.
- [ ] Queries are frozen and reproducible.
- [ ] Recent and historical candidate classes are represented.
- [ ] Excluded candidates retain the exact reason for exclusion.

## Direct-replication integrity

- [ ] No candidate is marked direct without pre-state-before-transition evidence.
- [ ] No candidate is marked direct without a later phenotype.
- [ ] No candidate is marked direct without same-cell or defensible longitudinal identity.
- [ ] Biological units are explicit and not inferred from cells, wells, plates, chips, prefixes, libraries, or runs.
- [ ] Technical lineage is sufficient to separate collection and processing effects.
- [ ] Public data support a frozen analysis plan.

## Human-domain integrity

- [ ] Human-domain references are not relabelled as direct replication.
- [ ] Donor-level longitudinal studies remain donor-level.
- [ ] Post-stimulation single-cell datasets remain post-response evidence.
- [ ] Foundation-model compatibility does not upgrade biological evidence level.

## GSE94383 prefix integrity

- [ ] Prefixes are not used as biological replicates.
- [ ] Exact unresolved semantics remain visible.
- [ ] Prefix sensitivity is described as technical/condition sensitivity only.

## Fail-closed tests

- [ ] Valid search record is accepted.
- [ ] A candidate falsely promoted to direct without same-cell linkage is blocked.
- [ ] A global `FOUND` verdict without an eligible candidate is blocked.
- [ ] A biological claim based on a technical prefix is blocked.

## Safety

- [ ] No physical protocol is included.
- [ ] No treatment or clinical claim is made.
- [ ] Partner-laboratory requirements remain non-operational.