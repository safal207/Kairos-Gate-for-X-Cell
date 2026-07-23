# GSE184241 Geneformer runtime preflight in LiminalDB

**Date:** 2026-07-23  
**Status:** `RECOVERED_REPORT_ONLY`  
**Scope:** computational runtime preflight and temporary evidence-ledger rehearsal only

## Question

Can BioEvidence OS preserve a Geneformer runtime attempt as a durable, replayable evidence chain without silently upgrading environment readiness into model inference, biological evidence, causal validity, or execution authority?

## Frozen result

```text
PREFLIGHT_READY_CPU_ONLY
MODEL_INFERENCE_NOT_EXECUTED
EMBEDDING_NOT_GENERATED
CAUSAL_VALIDITY_NOT_EVALUATED
RECOVERED_REPORT_ONLY
```

The runner could import the pinned runtime dependencies, resolve the public Geneformer repository revision, and confirm the presence of the `Geneformer-V1-10M` checkpoint directory in repository metadata.

No checkpoint weights were downloaded. The Geneformer package was not installed from a pinned source revision. No GSE184241 cell was tokenized. No model inference or embedding generation occurred. Incremental value over the frozen PCA baseline was not tested.

## Exact compatibility pins

### Kairos Gate source

```text
head: d1f872144984f46bcbb0d97e9280d2ef21e2a2b9
```

### LiminalDB

```text
repository: safal207/LiminalDB
commit: ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d
event schema: liminaldb.trustworthy-transition-event.v0.1
ledger profile: org.liminaldb.trustworthy-transition-ledger.v0.1
```

The selected LiminalDB commit contains the merged trustworthy-transition ledger, signed-checkpoint, and crash-consistency stack.

### Geneformer source observation

```text
repository: ctheodoris/Geneformer
requested revision: main
resolved revision: 04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5
target directory: Geneformer-V1-10M
target directory present: true
```

This is a source-metadata observation. It is not a downloaded-checkpoint digest or a Model Evidence Passport.

## Runtime observation

Pinned modules imported successfully:

| Module | Version |
|---|---|
| torch | `2.7.1+cpu` |
| transformers | `4.52.4` |
| datasets | `3.6.0` |
| anndata | `0.11.4` |
| huggingface_hub | `0.32.4` |

Hardware observation:

```text
CUDA available: false
CUDA device count: 0
nvidia-smi: absent
```

The preflight action itself therefore executed successfully on CPU, while all model-execution flags remained false.

## LiminalDB transition

The exporter produced one transition with six records:

```text
authorization
  -> GSE184241 benchmark observation
  -> Geneformer runtime-preflight observation
  -> response integrity
  -> causal audit
  -> continuity snapshot
```

The authorization permits only computational environment and public-source readiness checks. It explicitly denies physical biological work, production LiminalDB writes, model-inference claims without execution evidence, external submission, deployment, and merge authority.

The response-integrity record binds the exact sorted set of both observation references. The causal-audit record keeps causal validity unevaluated and blocks same-cell, causal, clinical, and incremental-value interpretations.

Final independent dimensions:

```text
authority: VALID
execution: OBSERVED_EXECUTED
response_integrity: VERIFIED
causal_validity: NOT_EVALUATED
continuity_posture: REPORT_ONLY
side_effect_committed: false
```

`OBSERVED_EXECUTED` refers only to the runtime-preflight action. It does not refer to Geneformer inference.

## Actual WAL, snapshot, and replay proof

The CI job checked out the exact LiminalDB commit, compiled the Rust bridge against the real `liminal-store` API, appended all six events to a temporary dedicated ledger root, wrote a digest-bound snapshot, closed the ledger, reopened it, and required snapshot-assisted replay to equal full WAL replay.

Replay receipt:

```text
transition_id: gse184241-geneformer-runtime-preflight-v0-1
subject_id: GSE184241
events before reopen: 6
events after reopen: 6
snapshot event count: 6
projection count: 1
projection equal after reopen: true
final side effect committed: false
verdict: RECOVERED_REPORT_ONLY
```

Cryptographic references:

```text
bundle SHA-256:
sha256:a6dd229ffaa5a13fab248da8717048fb73add77d476425327a6b8349d0ec99a1

snapshot digest:
sha256:cef6afc271fd96ef13a8d359f913d2301593ce6eb1daefc54cb532e301654b54

final semantic event hash:
sha256:d2f749e935c5afa49c58d98d78ec60bb973c1ef3c1f38082eb1f1fbd0acd28b1

replay receipt file SHA-256:
9dd336538150b83c408e7c1d6305aa225dd8745d62167165b60f37804b5aba69
```

No live or production LiminalDB node was contacted. The temporary WAL and snapshot were retained only as GitHub Actions evidence.

## Fail-closed misuse test

A deterministic negative fixture attempted to change the accepted preflight into:

- completed model inference;
- generated embeddings;
- established incremental value;
- valid causal evidence;
- production memory write;
- continuation of a side effect.

The Python bridge validator rejected the modified bundle before it reached the Rust ledger.

This matters because durable storage must preserve supplied meaning; it must not make an invalid scientific or authorization claim acceptable merely by storing it reliably.

## Evidence artifacts

First successful run on the implementation head:

```text
workflow run: 30021401706
bridge input artifact: 8569423972
bridge input archive digest:
sha256:f391844959937aea141c7d33d2eb6119b75e7112983882ccc09e7218e19611cf

LiminalDB replay artifact: 8569443384
replay archive digest:
sha256:00fa5825aad3c6e5318ca15209edee9e4e2fe69228130b568d871f89ec91a38f
```

The artifacts expire on 2026-08-22.

## Allowed interpretation

The evidence supports:

- the selected CPU runtime dependencies imported;
- the public Geneformer source revision and target directory were observable;
- BioEvidence OS exported a deterministic six-record evidence chain;
- the exact pinned LiminalDB implementation durably appended, snapshotted, reopened, and replayed that chain in a temporary ledger;
- the final projection remained report-only and committed no side effect.

## Blocked interpretation

The evidence does not support:

- a successful Geneformer checkpoint download;
- a pinned Geneformer package installation;
- GSE184241 tokenization;
- Geneformer inference or embeddings;
- improvement over `NFKBIA`, inflammatory-panel, or PCA baselines;
- same-cell future-response prediction;
- an `NFKBIA`-specific causal effect;
- clinical, diagnostic, treatment, or therapeutic utility;
- physical biological execution;
- production LiminalDB persistence or external anti-rollback receipt for this transition.

## Required superseding transition

A future inference run must not edit this preflight memory. It must create a new authorization epoch that explicitly supersedes the current authorization and supplies:

1. exact Geneformer source and checkpoint revisions;
2. package, container, and dependency digests;
3. GSE184241 input conversion, cell-order, token, and AnnData hashes;
4. checkpoint download and load receipt;
5. actual inference and embedding artifact SHA-256 values;
6. hardware, parameters, seeds, and runtime measurements;
7. training-overlap assessment;
8. the same frozen donor folds;
9. a Model Evidence Passport;
10. an incremental-value decision against the existing PCA-state ceiling.

Until then, the durable current state remains:

```text
RUNTIME_PREFLIGHT_RECORDED
MODEL_INFERENCE_NOT_EXECUTED
REPORT_ONLY
```
