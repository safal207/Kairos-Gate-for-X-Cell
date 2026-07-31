# TRACE → Kairos → CML → ProofPath → LiminalDB bridge v0.1

## Purpose

This bridge turns the bounded TRACE evidence package from PR #55 into a deterministic transition-network receipt using the Kairos Transition Graph Engine from PR #57.

```text
pinned TRACE package
  -> exact file identity
  -> semantic package validation
  -> derived transition graph
  -> Kairos analysis
  -> CML causal-memory projection
  -> ProofPath evidence-path projection
  -> LiminalDB ledger projection
```

The bridge does not merge the two source branches and does not copy the TRACE package into the integration branch. CI retrieves six files from exact commit:

```text
31959a573724d0fd7ef1ac620a47d46355797b2f
```

Each file is bound to its expected Git blob SHA. CI also computes a SHA-256 digest for the portable receipt.

## Consumed package files

- claim map;
- causal-transition map;
- disposition;
- source manifest;
- reproducibility contract;
- phase-compatibility decision.

A missing file, changed byte, schema mismatch, `case_id` substitution, claim-status promotion, authority escalation, or removal of a required blocker produces `BLOCK`.

## Derivation boundary

The transition graph is built from package semantics by code. The bridge does not treat a committed graph snapshot as the scientific authority.

Required package invariants include:

- C1–C12 remain present with their reviewed statuses;
- C7 remains a rejected direct-observation claim;
- C8 remains taxonomically unresolved;
- C9 remains a rejected universal-individual claim;
- C10 remains a rejected adaptive-causality overclaim;
- C11 and C12 remain not established;
- B1–B7 remain visible reproduction blockers;
- historical divergence or admixture time is not relabelled as a cellular phase;
- no candidate cellular window is unlocked.

## Kairos output

Expected result:

```text
ACCEPT_WITH_LIMITS
```

Required retained gap:

```text
modern genomes
  -> annotation enrichment
  -/-> expression change
  -/-> cellular effect
  -/-> organism phenotype
  -/-> fitness advantage
```

The missing path remains `CAUSAL_GAP`; enrichment is not promoted into adaptive benefit.

## CML projection

The CML projection uses the `cml-memory-pack-v1` shape and preserves:

- the observed package import;
- the computational-inference boundary;
- the adaptive causal gap;
- the proposed independent-reproduction action;
- the lesson to retain rejected and unresolved claims.

CML records why a conclusion is bounded. It does not certify scientific truth or grant execution authority.

## ProofPath projection

ProofPath receives one evidence path per C1–C12 claim.

```text
SUPPORTED_*  -> ACCEPT_WITH_LIMITS
REJECTED_*   -> BLOCK
UNRESOLVED / NOT_ESTABLISHED -> HOLD
```

The overall decision remains:

```text
HOLD
execution_allowed = false
```

The projection includes a deterministic hash-chained audit sequence:

```text
authorization
-> package observation
-> graph derivation
-> claim boundary
-> HOLD decision
```

## LiminalDB projection

The output targets profile:

```text
org.liminaldb.trustworthy-transition-ledger.v0.1
```

Records:

```text
authorization
-> observation
-> response_integrity
-> causal_audit
-> continuity_snapshot
```

Current conformance label:

```text
DOCUMENTARY_PROJECTION_NOT_RUST_REPLAY
```

This wording is deliberate. The bridge validates a deterministic event and parent chain locally, but does not claim that the receipt has already been replayed by the LiminalDB Rust implementation.

LiminalDB remains an audit and continuity layer:

```text
source_verdict = ACCEPT_WITH_LIMITS
adds_scientific_verdict = false
continuity_posture = REPORT_ONLY
side_effect_committed = false
```

## Run locally

Place the six exact PR #55 files in one directory using their original basenames, then run:

```bash
python scripts/derive_trace_ecosystem_receipt.py \
  --manifest manifests/trace-evidence-package-pr55.v0.1.json \
  --source-dir /path/to/trace-package \
  --output trace-ecosystem-receipt.json \
  --enforce
```

The CLI verifies Git blob identity before parsing JSON.

## Authority boundary

Every output remains:

```text
RESEARCH_ONLY
scientific_truth_authorized = false
causal_authorization = false
experiment_authorization = false
clinical_authorization = false
ancestry_identity_authorization = false
deployment_authorization = false
merge_authorization = false
```

The bridge contains no biological sequence, wet-lab protocol, treatment guidance, experiment plan, or ancestry-identity authorization.
