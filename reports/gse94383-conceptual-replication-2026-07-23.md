# GSE94383 descriptive pathway-context report

## Supersession notice

This report supersedes the earlier `CONCEPTUAL_SIGNAL_SUPPORTED` interpretation.

The numerical within-table association is unchanged. The evidence level is corrected because the analysed cells cannot be treated as independently sampled biological units while their biological grouping and ID-prefix semantics remain unresolved.

## Result

The separate public experiment **GSE94383** was examined as descriptive pathway context for the GSE141064 observation linking `Nfkbia` and a later inflammatory-response phenotype.

The datasets are not temporally equivalent:

- GSE141064 asks whether a basal transcriptomic state is associated with a later `Tnf-mCherry` response;
- GSE94383 records LPS-induced NF-kB dynamics and then measures the transcriptome in the same cell.

GSE94383 therefore provides a within-dataset view of pathway coupling. It is not direct replication, independent biological validation, or inferential conceptual triangulation of the original predictor claim.

## Evidence binding

- Repository: `safal207/Kairos-Gate-for-X-Cell`
- Hardening PR: `#46`
- Workflow: `BioEvidence P0 Scientific Inference Boundary`
- Analysis script: `scripts/analyze_gse94383_conceptual_replication.py`
- Analysis-script SHA-256: `746241698bbeec960512c3301c9564547705b225eea18b8d667498ed3bdd9edc`

The workflow checks out the exact `pull_request.head.sha`, verifies the checkout identity, and emits a separate machine-readable receipt. This committed report deliberately does not embed its own commit SHA, because changing that value would itself create another commit and a self-referential provenance loop.

Publisher files remain bound by SHA-256:

```text
single_cell_dynamics.csv
c43d0b54ed4b245b1690e9675630682c0843cda63f14a3e51dbf13b8f87c070e

single_cell_transcriptomes.csv
e264565c72f06ed98ee10914c0350486dd2daa2460cd19ec8071d756bf982200
```

## Data-integrity checks

- Dynamics rows: **823**
- Transcriptome rows: **823**
- Exact cell-ID sets match: **yes**
- Duplicate cell IDs: **0**
- Complete cell observations: **823**
- NF-kB trajectory columns: **62**
- ID prefixes: **10**
- Effective independent biological N: **unresolved**

Harvest-time structure:

| Harvest time | Cell observations | Available trajectory points |
|---:|---:|---:|
| 0 | 186 | 1 |
| 75 | 145 | 17 |
| 150 | 368 | 32 |
| 300 | 124 | 62 |

Time-zero cells have no preceding stimulated trajectory and do not independently identify a dynamic association within that stratum.

## Descriptive primary endpoint

**Question:** Within the matched table, is post-LPS `Nfkbia` expression directionally associated with recent preceding same-cell NF-kB activity after stratification by harvest time?

Method:

- rank observations within harvest time;
- descriptive Spearman association;
- 2,000 cell-level stratified bootstrap resamples;
- 5,000 cell-level stratified permutations;
- leave-one-ID-prefix-out technical sensitivity.

The last three items are **within-table sensitivity summaries only**. They are not independent-unit confidence intervals or hypothesis tests.

| Metric | Result | Permitted interpretation |
|---|---:|---|
| Spearman rho | **0.178** | weak positive association in the observed table |
| Cell-level bootstrap interval | **0.110 to 0.243** | descriptive cell-resampling sensitivity only |
| Cell-level permutation score | **0.0002** | non-inferential while biological N is unresolved |
| Leave-one-prefix-out rho range | **0.153 to 0.200** | technical prefix sensitivity only |

The positive direction was retained in every leave-one-prefix-out run. This does not establish that prefixes are biological replicates or that the signal generalizes to new biological material.

## Secondary context

Mean prior NF-kB activity also had a positive within-table association with post-LPS `Nfkbia` expression:

- rho: **0.235**;
- cell-level bootstrap interval: **0.169 to 0.298**, descriptive only.

The calculated attenuation metric had rho approximately `-0.178`, but it is effectively the complement of recent activity after per-cell trajectory normalization. It is therefore **not independent confirmatory evidence**.

## Corrected verdict

```text
DESCRIPTIVE_WITHIN_DATASET_SIGNAL_OBSERVED
```

The verdict is based only on the observed descriptive direction. Neither the 823-cell count, the cell-level bootstrap interval, the cell-level permutation score, nor ID-prefix exclusion may promote the result to independent biological support.

The result does **not** establish:

- direct replication of the GSE141064 basal predictor claim;
- conceptual pathway triangulation at an independent biological evidence level;
- independent biological replication from 823 cells;
- generalization beyond the observed table;
- causal action of `Nfkbia` on the later response;
- tissue, clinical, or therapeutic effects.

## Next valid action

1. Resolve the biological and technical meaning of GSE94383 ID prefixes and source grouping.
2. Use cluster- or block-level inference only after a source-backed independent unit is identified.
3. Continue searching for a dataset containing a **pre-stimulation transcriptome linked to a later TNF-promoter phenotype**.
4. Keep the current result as descriptive pathway context only.

## Safety boundary

This report is computational and documentary only. It does not authorize physical biological work or provide operational experimental instructions.
