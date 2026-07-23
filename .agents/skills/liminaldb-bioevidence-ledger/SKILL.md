---
name: liminaldb-bioevidence-ledger
description: Export one BioEvidence OS computational transition into a replayable LiminalDB trustworthy-transition chain without upgrading runtime readiness into model inference or scientific evidence.
version: 0.1.1
---

# LiminalDB BioEvidence Ledger

Use this skill when a computational biology workflow must preserve the exact evidence and decision history of a runtime attempt, model execution, validation, or HOLD decision.

## Purpose

The skill maps one BioEvidence OS transition onto the merged LiminalDB trustworthy-transition profile:

```text
authorization
  -> observation(s)
  -> response_integrity
  -> causal_audit
  -> continuity_snapshot
```

LiminalDB persists and replays supplied records. It does not issue authorization, execute Geneformer, validate biological truth, calculate causal validity, or decide that work may continue.

## Exact compatibility pin

- repository: `safal207/LiminalDB`
- commit: `ae51ac3a9d765492ba13e65ae3f7e8a09fa3191d`
- event schema: `liminaldb.trustworthy-transition-event.v0.1`
- profile: `org.liminaldb.trustworthy-transition-ledger.v0.1`

Any pin change requires a fresh compatibility run and a new bridge decision. Do not silently follow `main`.

## Runtime-preflight interpretation

The transition action in v0.1 is `GENEFORMER_RUNTIME_PREFLIGHT`.

A successful preflight may establish only that:

- the selected source revision is reachable;
- required Python modules can be imported;
- the environment and hardware were observed;
- the selected checkpoint path and expected input contract were documented.

It does not establish that:

- Geneformer inference executed;
- embeddings were generated;
- the checkpoint is scientifically compatible;
- Geneformer adds value beyond the frozen PCA baseline;
- same-cell future-response prediction exists;
- `NFKBIA` is causal, unique, clinical, or therapeutic.

## Required records

### Authorization

Must permit computational preflight only and explicitly deny:

- physical biological work;
- treatment or clinical decisions;
- production LiminalDB writes;
- model-inference claims without an exact checkpoint execution receipt;
- external submission or merge authority.

### Observations

At minimum preserve:

1. the frozen GSE184241 donor-held-out benchmark identity and exact artifact digest;
2. the runtime-preflight environment, source revision, checkpoint target, import status, hardware status, and execution flags.

### Response integrity

Must bind the exact sorted set of all observation references. It may be `VERIFIED` only when the stored payload digests match the exported payloads.

### Causal audit

Must keep `causal_validity=NOT_EVALUATED` for runtime preflight. It must explicitly block same-cell, causal, clinical, and incremental-value claims.

### Continuity snapshot

Must carry all independent dimensions:

- authority;
- execution;
- response integrity;
- causal validity;
- continuity posture.

For a completed preflight with no inference, the default is:

```text
VALID
OBSERVED_EXECUTED
VERIFIED
NOT_EVALUATED
REPORT_ONLY
```

`OBSERVED_EXECUTED` refers only to the preflight action. The payload must still state `model_inference_executed=false` and `embedding_generated=false`.

## Supersession

`links.authorization_ref` always identifies the authorization governing the **current** record and current transition. It must never point to an authorization from an earlier transition merely to express ancestry.

Transition ancestry is carried separately in the required top-level `supersession` envelope:

```text
relation: ROOT | SUPERSEDES
predecessor_transition_id: string | null
predecessor_authorization_ref: sha256 reference | null
```

The current preflight bundle is a `ROOT`, so both predecessor fields are null. A later checkpoint execution or incremental-value transition must:

1. create its own new authorization;
2. bind every new record to that new authorization through `links.authorization_ref`;
3. set `supersession.relation=SUPERSEDES`;
4. identify the earlier transition and its authorization only through the predecessor fields;
5. explain in its authorization and causal-audit payloads which new evidence changes the prior HOLD or preflight decision.

Later transitions must not rewrite the earlier WAL history.

## Storage boundary

- GitHub Actions uses a temporary ledger root.
- WAL, snapshot, projection receipt, and exported bundle are artifacts.
- No live or production LiminalDB node is contacted.
- Heavy count matrices, AnnData files, checkpoints, and embeddings remain in object/artifact storage; the ledger stores exact references and digests only.

## Fail-closed conditions

Block the bundle when any of the following is true:

- LiminalDB repo or commit does not match the exact pin;
- record order differs from the required chain;
- record references or payload digests are not lowercase SHA-256 references;
- response integrity omits an observation;
- continuity snapshot lacks an independent dimension;
- `side_effect_committed` is true;
- preflight is described as model inference;
- embeddings are claimed without an exact artifact digest;
- causal, same-cell, clinical, treatment, therapeutic, physical-experiment, merge, deployment, or production-write authority is granted;
- a root transition supplies predecessor fields;
- a superseding transition omits either predecessor field;
- a current record points `links.authorization_ref` at the predecessor authorization instead of its own current authorization.

## Release gate

A passing release requires:

1. deterministic Python export;
2. static schema validation;
3. negative fixture rejection;
4. Rust compilation against the exact LiminalDB pin;
5. temporary WAL append of the full chain;
6. snapshot creation;
7. reopen and full replay;
8. projection equality and exact final dimensions;
9. retained exact-head artifacts.
