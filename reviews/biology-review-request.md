# External Biology Review Request — BioEvidence OS v0.1

## Review purpose

Please review whether the biological interpretations and boundaries in PR #23 are scientifically defensible for the GSE141064 / GSE94383 case.

This is a computational and documentary review. No physical biological work is requested or authorized.

## Primary review questions

1. Is the distinction between biological and technical units stated correctly?
2. Is it appropriate to treat plate, library, sequencing run, read, and image frame as technical rather than biological replication here?
3. Is GSE94383 correctly classified as conceptual pathway evidence rather than direct temporal replication?
4. Are the shared-state, direct-effect, marker-only, technical-confounding, small-effect, and instability hypotheses biologically plausible and sufficiently distinct?
5. Does the current interpretation of `Nfkbia` avoid overstating a unique driver role?
6. Are important biological alternatives or context dependencies missing?
7. Are the proposed partner-laboratory evidence requirements biologically coherent without becoming an operational protocol?
8. Are any tissue, clinical, therapeutic, or translational implications stated too strongly?

## Current bounded conclusions

- exploratory association: supported with limits;
- independent conceptual pathway coupling: supported;
- direct temporal replication: absent;
- direct causal effect: not identified;
- tissue, clinical, and therapeutic claims: blocked;
- partner evidence package: ready for scientific review only;
- physical execution: not authorized.

## Requested response format

```text
Reviewer expertise:
Overall verdict: ACCEPT / ACCEPT_WITH_CHANGES / HOLD / BLOCK
P0 biological errors:
P1 required corrections:
P2 improvements:
Missing biological alternatives:
Claims that are too strong:
Claims that are too weak or unnecessarily blocked:
Partner-handoff concerns:
Recommended next evidence action:
```

## Evidence entry points

- `README.md`
- `docs/architecture.md`
- `RELEASE_NOTES_v0.1.md`
- `examples/gse141064.experimental-unit-audit.json`
- `examples/gse141064.provenance-confounder-graph.json`
- `examples/gse141064.independent-replication-search.json`
- `examples/gse141064.nfkbia-causal-hypotheses.json`
- `examples/gse141064.temporal-replication-gate.json`
- `examples/gse141064.nfkbia-partner-lab-handoff.json`
- `reports/gse94383-conceptual-replication-2026-07-23.md`
- `reports/gse141064-nfkbia-causal-ranking-2026-07-23.md`
- `reports/gse141064-direct-temporal-replication-gap-2026-07-23.md`
- `reports/gse141064-nfkbia-partner-lab-handoff-2026-07-23.md`

## Non-claims

This project does not claim that `Nfkbia` is a validated therapeutic target, that causality has been established, or that any biological intervention should be performed.
