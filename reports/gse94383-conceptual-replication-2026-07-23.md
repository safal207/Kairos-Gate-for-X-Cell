# GSE94383 conceptual replication report

## Result

An independent public dataset, **GSE94383**, was tested as a conceptual replication candidate for the GSE141064 observation linking `Nfkbia` and a later inflammatory-response phenotype.

The datasets are not temporally equivalent:

- GSE141064 asks whether a basal transcriptomic state is associated with a later `Tnf-mCherry` response;
- GSE94383 records LPS-induced NF-kB dynamics and then measures the transcriptome in the same cell.

The GSE94383 analysis therefore tests pathway coupling, not direct replication of the original predictor claim.

## Reproducibility identity

- Pull request: `#23`
- Head SHA analysed: `112ea2eafd29efa56a20a40cba696c9f657dbd52`
- Workflow run: `29998853791`
- Evidence artifact: `8560131039`
- Contract and live-analysis jobs: `success`

Publisher checksums were verified before analysis:

```text
single_cell_dynamics.csv
MD5    8be1e148d47762fd148584469a6179a6
SHA256 c43d0b54ed4b245b1690e9675630682c0843cda63f14a3e51dbf13b8f87c070e

single_cell_transcriptomes.csv
MD5    60a8bc62e5c49692fce8c79fdf0bf530
SHA256 e264565c72f06ed98ee10914c0350486dd2daa2460cd19ec8071d756bf982200
```

## Data-integrity checks

- Dynamics rows: **823**
- Transcriptome rows: **823**
- Exact cell-ID sets match: **yes**
- Duplicate cell IDs: **0**
- Complete matched cells: **823**
- NF-kB trajectory columns: **62**
- ID prefixes: **10**

Harvest-time structure:

| Harvest time | Cells | Available trajectory points |
|---:|---:|---:|
| 0 | 186 | 1 |
| 75 | 145 | 17 |
| 150 | 368 | 32 |
| 300 | 124 | 62 |

Time-zero cells have no preceding stimulated trajectory and therefore do not independently identify the dynamic association within that stratum.

## Frozen primary endpoint

**Question:** Is post-LPS `Nfkbia` expression positively associated with recent preceding same-cell NF-kB activity after stratification by harvest time?

Method:

- rank observations within harvest time;
- Spearman association;
- 2,000 stratified bootstrap resamples;
- 5,000 stratified permutations;
- leave-one-ID-prefix-out technical sensitivity.

| Metric | Result |
|---|---:|
| Spearman rho | **0.178** |
| Bootstrap 95% CI | **0.110 to 0.243** |
| Stratified permutation p | **0.0002** |
| Leave-one-prefix-out rho range | **0.153 to 0.200** |

The prespecified positive direction was retained in every leave-one-prefix-out run.

## Secondary context

Mean prior NF-kB activity was also positively associated with post-LPS `Nfkbia` expression:

- rho: **0.235**
- bootstrap 95% CI: **0.169 to 0.298**

The calculated attenuation metric had rho approximately `-0.178`, but it is effectively the complement of recent activity after per-cell trajectory normalization. It is therefore **not independent confirmatory evidence**.

## Verdict

```text
CONCEPTUAL_SIGNAL_SUPPORTED
```

The independent experiment supports a weak but stable same-cell coupling between NF-kB activity and post-LPS `Nfkbia` expression.

It does **not** establish:

- direct replication of the GSE141064 basal predictor claim;
- independent biological replication from 823 individual cells;
- causal action of `Nfkbia` on the later response;
- tissue, clinical, or therapeutic effects.

## Next valid action

1. Resolve the biological and technical meaning of GSE94383 ID prefixes.
2. Keep GSE94383 as conceptual pathway triangulation.
3. Continue searching for an independent dataset containing a **pre-stimulation transcriptome linked to a later TNF-promoter phenotype**.
4. If no suitable public dataset exists, prepare a non-operational validation brief for an authorized partner laboratory.

## Safety boundary

This report is computational and documentary only. It does not authorize physical biological work or provide operational experimental instructions.
