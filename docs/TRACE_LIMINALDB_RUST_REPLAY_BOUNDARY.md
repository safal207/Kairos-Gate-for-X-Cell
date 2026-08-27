# Authority boundary

The TRACE LiminalDB Rust replay validates only durable storage and deterministic recovery of an already-bounded research receipt.

Allowed conclusion:

```text
The five-event report-only transition chain was appended to a temporary WAL,
snapshotted, reopened, and recovered without projection drift.
```

Forbidden conclusions:

- the TRACE interpretation is scientifically true;
- the unknown ancestral population has been directly observed or taxonomically identified;
- adaptive benefit has been established;
- a physical experiment, clinical action, deployment, production write, or merge is authorized.

A successful replay cannot promote `ACCEPT_WITH_LIMITS` into causal validity. The final LiminalDB dimension remains `causal_validity = NOT_EVALUATED`, and continuity remains `REPORT_ONLY` with `side_effect_committed = false`.
