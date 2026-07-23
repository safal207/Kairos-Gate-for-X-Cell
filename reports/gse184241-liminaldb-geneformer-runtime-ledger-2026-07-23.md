# GSE184241 Geneformer runtime preflight in LiminalDB

**Date:** 2026-07-23  
**Status:** `RECOVERED_REPORT_ONLY`  
**Scope:** computational runtime preflight and temporary evidence-ledger rehearsal only

## Question

Can BioEvidence OS preserve a Geneformer runtime attempt as a durable, replayable evidence chain without silently upgrading environment readiness into model inference, biological evidence, causal validity, inherited authority, or execution permission?

## Frozen result

```text
PREFLIGHT_READY_CPU_ONLY
MODEL_INFERENCE_NOT_EXECUTED
EMBEDDING_NOT_GENERATED
CAUSAL_VALIDITY_NOT_EVALUATED
SUPERSESSION_RELATION_ROOT
RECOVERED_REPORT_ONLY
```

The runner imported the pinned runtime dependencies, resolved the public Geneformer repository revision, and confirmed that repository metadata contains the `Geneformer-V1-10M` directory.

No checkpoint weights were downloaded. The Geneformer package was not installed from a pinned source revision. No GSE184241 cell was tokenized. No model inference or embedding generation occurred. Incremental value over the frozen PCA baseline was not tested.

## Exact compatibility pins

### Review-fix validation source

```text
Kairos Gate implementation head:
925f2f6b35f9076c32bc4d6f1ff692c0e3b9fdb5
```

This checked-in report is necessarily created by a later documentation commit. The final unchanged PR-head workflow and artifact identifiers are therefore maintained in PR #38 metadata after the last rerun rather than self-referentially embedded as this file's own commit SHA.

### LiminalDB

```text
repository: safal207/LiminalDB
commit: ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d
event schema: liminaldb.trustworthy-transition-event.v0.1
ledger profile: org.liminaldb.trustworthy-transition-ledger.v0.1
```

The selected LiminalDB commit contains the merged trustworthy-transition ledger, signed-checkpoint, and crash-consistency stack.

### Immutable CI dependencies

```text
actions/checkout:
08eba0b27e820071cde6df949e0beb9ba4906955

actions/setup-python:
a26af69be951a213d495a4c3e4e4022e16d87065

actions/upload-artifact:
ea165f8d65b6e75b540449e92b4886f43607fa02

actions/download-artifact:
d3f86a106a0bac45b974a628896c90dbdf5c8093
```

The Rust adapter is compiled with `cargo run --locked`, so the pinned LiminalDB lockfile cannot be silently regenerated during evidence production.

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

The preflight action itself executed successfully on CPU, while every model-execution flag remained false.

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

The donor benchmark file is an explicit workflow trigger. A benchmark-only change therefore cannot bypass regeneration and validation of the ledger evidence chain.

### Current authority versus predecessor ancestry

The accepted preflight is a root transition:

```text
supersession.relation: ROOT
supersession.predecessor_transition_id: null
supersession.predecessor_authorization_ref: null
```

`links.authorization_ref` identifies only the authorization governing the current chain. It is not used to carry predecessor ancestry.

A later real inference must create its own authorization and use a separate top-level envelope:

```text
supersession.relation: SUPERSEDES
supersession.predecessor_transition_id: <earlier transition>
supersession.predecessor_authorization_ref: <earlier authorization>
```

All records in that later chain must still point `links.authorization_ref` to the new current authorization. Earlier WAL history must not be rewritten.

## Final independent dimensions

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

The workflow checked out the exact LiminalDB commit, compiled the Rust bridge against the real `liminal-store` API using the existing lockfile, appended all six events to a temporary dedicated ledger root, wrote a digest-bound snapshot, closed the ledger, reopened it, and required snapshot-assisted replay to equal full WAL replay.

Replay receipt:

```text
transition_id: gse184241-geneformer-runtime-preflight-v0-1
subject_id: GSE184241
supersession_relation: ROOT
predecessor_transition_id: null
predecessor_authorization_ref: null
events before reopen: 6
events after reopen: 6
snapshot event count: 6
projection count: 1
projection equal after reopen: true
final side effect committed: false
verdict: RECOVERED_REPORT_ONLY
```

Cryptographic references from the review-fix validation run:

```text
bundle SHA-256:
sha256:cbeb00ec78c28f70cabe596c992f4cc8a42f953c6d40489ec4d2588109ef8992

snapshot digest:
sha256:e95901f3fdcc2d21996b40c905b412534531f323422f434ad2649a57c6edc1e2

final semantic event hash:
sha256:aada09b14b641b7f436a9da9ec9f61573de6b2e93b9c0a7c3ca4bf7bc7325e2f

replay receipt file SHA-256:
bf59819215ab5156d8e56cd72e0d44815839c87a16077f126017508805a4f8ee
```

No live or production LiminalDB node was contacted. The temporary WAL and snapshot were retained only as GitHub Actions evidence.

## Fail-closed misuse test

A deterministic negative fixture attempted to:

- relabel the root preflight as `SUPERSEDES`;
- inject a predecessor transition and predecessor authorization;
- use that predecessor authorization as the current benchmark-observation authority;
- claim completed model inference and generated embeddings;
- claim incremental value and valid causal evidence;
- grant production persistence and side-effect continuation.

The validator rejected the modified bundle before it reached the Rust ledger. It produced 16 independent errors, including:

```text
runtime preflight must be a ROOT transition with null predecessor fields
record 1 must not use predecessor authorization as current authority
benchmark observation must reference only current authorization
runtime preflight cannot establish causal validity
continuity posture does not match preflight execution
storage boundary production_write must be false
```

This matters because durable storage must preserve supplied meaning; it must not make an invalid scientific or authorization claim acceptable merely by storing it reliably.

## Review-fix validation evidence

```text
LiminalDB workflow run:
30038320780

Inherited BioEvidence workflow run:
30038320257

Bridge-input artifact:
8576193685
archive digest:
sha256:af171668b95273f2717989d7e7987977959cedb05600b6d94a0157bd4dfbc644

LiminalDB replay artifact:
8576212176
archive digest:
sha256:8ccc81956cdc0e79ea903147b84bc88e765025d56cba82e283fd2f86f8c1c6e5
```

The artifacts expire on 2026-08-22.

## Allowed interpretation

The evidence supports:

- the selected CPU runtime dependencies imported;
- the public Geneformer source revision and target directory were observable;
- BioEvidence OS exported a deterministic root evidence chain;
- predecessor ancestry was kept separate from current authorization;
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

A future inference run must not edit this preflight memory. It must create a new authorization and a separate `SUPERSEDES` envelope identifying the prior transition and prior authorization. It must also supply:

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
