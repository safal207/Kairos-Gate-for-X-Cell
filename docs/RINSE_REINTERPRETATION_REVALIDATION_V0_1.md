# RINSE reinterpretation revalidation v0.1

## Purpose

This layer closes the return path from RINSE into Kairos Gate.

```text
TRACE evidence
  -> Kairos analysis
  -> LiminalDB replay
  -> RINSE reinterpretation
  -> Kairos revalidation
```

The return path evaluates whether a revised interpretation is structurally and
evidentially admissible. It does not treat the reinterpretation as scientific
proof or permission to act.

## Pinned RINSE source

The manifest fixes:

- repository `safal207/rinse`;
- PR `#23`;
- commit `1ecdf2d704f120d15b8ee458573043bbef4e717b`;
- exact Git blob SHAs for the RINSE adapter, reflection engine, source receipt,
  and package declaration;
- successful workflow run and artifact identifiers;
- artifact, loop-file, and upstream-verification SHA-256 values;
- loop, source receipt, reflection graph, and interpretation semantic digests.

The Kairos workflow checks out this exact RINSE commit and regenerates the loop.
It does not rely only on a copied JSON file or an expiring Actions artifact.

## Two distinct transitions

### 1. Interpretation supersession

```text
adaptive-benefit overclaim
  -> association with unresolved adaptive causality
```

This transition is accepted with limits because:

- the predecessor remains preserved;
- the `SUPERSEDES` relation is explicit;
- the active RINSE record is evidence-bound;
- the candidate remains non-executable;
- the claim level is association, not causal.

### 2. Association to adaptive causality

```text
association
  -> adaptive causality established
```

This transition remains incomplete. Kairos requires four intermediates:

- expression change;
- cellular effect;
- organism phenotype;
- fitness advantage.

No one of these is marked observed, so the transition produces one `CAUSAL_GAP`
containing all four missing intermediates.

## Expected result

```text
Kairos verdict: ACCEPT_WITH_LIMITS
reinterpretation transition: ACCEPT_WITH_LIMITS
adaptive causality: HOLD_MISSING_EVIDENCE
execution: HOLD
deployment: NOT_AUTHORIZED
merge: NOT_AUTHORIZED
```

An attempted promotion of the second transition to claim level `causal` is
blocked by the existing Kairos claim firewall.

## Authority boundary

```text
classification: RESEARCH_ONLY
scientific_truth_authorized: false
causal_authorization: false
execution_authorized: false
deployment_authorized: false
merge_authorized: false
```

## CLI

```bash
python -m kairos_gate.rinse_reinterpretation_bridge \
  --manifest manifests/rinse-trace-loop-pr23.v0.1.json \
  --loop examples/rinse-trace-loop.v0.1.json \
  --output /tmp/kairos-rinse-revalidation.json
```

The CLI first checks the byte-level SHA-256 of the loop file, then validates all
semantic digests and graph relationships, and finally runs the transition engine.
Malformed or changed input returns `BLOCK:` and exit code `2` without a traceback.

## CI proof

The exact-head workflow:

1. checks out the Kairos PR head;
2. runs the full test suite;
3. checks out the pinned RINSE repository and commit;
4. verifies every RINSE Git blob pin;
5. regenerates the RINSE loop and compares it byte-for-byte with the pinned copy;
6. runs Kairos revalidation twice and compares output bytes;
7. enforces the exact causal gap and all authority boundaries;
8. proves loop and manifest tampering block;
9. uploads an exact-head revalidation artifact.

This demonstrates a closed, auditable reflection cycle. It does not authorize
scientific claims, biological work, production deployment, or merge.
