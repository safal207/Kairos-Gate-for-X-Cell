# TRACE → LiminalDB Rust replay v0.1

This stacked integration converts the pinned TRACE ecosystem receipt into five strict trustworthy-transition events, appends them to a temporary LiminalDB WAL, writes a digest-bound snapshot, closes the ledger, reopens it, and requires snapshot-assisted recovery to equal full WAL replay.

```text
authorization
→ observation
→ response_integrity
→ causal_audit
→ continuity_snapshot
```

The replay is pinned to LiminalDB commit `b8cf0528187c6d3fac3b28dbb9e90f1a2fb740e7` and profile `org.liminaldb.trustworthy-transition-ledger.v0.1`.

Expected result:

```text
RUST_REPLAY_RECOVERED_REPORT_ONLY
projection_equal_after_reopen: true
final_side_effect_committed: false
adds_scientific_verdict: false
```

The Rust replay proves storage, hash-chain, snapshot and recovery behavior only. It does not prove the TRACE scientific interpretation, establish causality, authorize experiments, permit clinical use, write to production storage, deploy software, or authorize merge.
