# Kairos Transition Graph Engine v0.1

## Purpose

Kairos Transition Graph Engine evaluates **paths between states** rather than treating a scientific statement as one indivisible claim.

```text
state
  -> proposed transition
  -> intermediate mechanisms
  -> observed evidence
  -> competing explanations
  -> bounded claim
```

The engine answers:

1. Are all states, transitions, and evidence objects explicitly identified?
2. Can the transition occur inside the declared time windows?
3. Which required intermediate mechanisms remain unobserved?
4. Does the claim exceed the strongest admissible evidence?
5. Which candidate path has stronger documented support?

It does not answer whether a biological theory is finally true.

## Contracts

The v0.1 data model contains three strict Draft 2020-12 contracts:

- `kairos-state-node.schema.json` — a bounded state and its time window;
- `kairos-transition-edge.schema.json` — a proposed state change, mechanism, alternatives, and claim level;
- `kairos-evidence-object.schema.json` — source, status, strength, independence, provenance, and causal-design boundary.

Public schemas in `schemas/` and packaged runtime copies in `kairos_gate/schemas/` must remain semantically identical.

## Graph layers

### State graph

A state is a versioned object with a type, label, bounded time window, uncertainty, evidence references, properties, and research-only authority.

### Transition graph

A transition connects two distinct states and records:

- mechanism;
- transition time window;
- evidence status;
- declared confidence;
- required and observed intermediates;
- competing explanations;
- bounded claim level.

### Evidence graph

Evidence is not a free-text citation. Each evidence object records:

- kind and source;
- status;
- strength;
- independence;
- whether the design can support causal inference;
- claim scope;
- byte-level provenance status.

### Temporal graph

Time uses a monotonic numeric axis. `start <= end` is mandatory. A transition must overlap both its source and target state windows on the same unit axis.

A temporal conflict produces `BLOCK`.

### Causal-gap graph

Every transition may declare required intermediate mechanisms. The engine compares them with observed intermediates and returns the missing set.

A causal gap does not automatically invalidate an association-level claim. It prevents silent promotion to mechanism or causality.

### Claim firewall

Claim levels are ordered:

```text
hypothesis < association < mechanism < causal < authorization
```

Default evidence ceilings are:

```text
missing or contradicted       -> hypothesis
computational inference       -> association
author-reported result        -> association
direct observation            -> mechanism ceiling
independently replicated      -> mechanism ceiling
explicit causal design        -> causal ceiling
authorization                 -> always blocked
```

Independent replication alone is not automatically causal. A causal claim requires an evidence object explicitly marked as a causal design.

## Ranking semantics

`rank_transitions` produces an evidence-support score in `[0, 1]` using a published deterministic formula:

```text
0.45 * mean evidence support
+ 0.30 * transition-status support
+ 0.25 * declared confidence
+ bounded independence bonus
- contradiction penalty
```

The result is a **ranking score**, not a probability that the transition is true.

The engine never emits a percentage of scientific truth.

## Verdicts

```text
ACCEPT_WITH_LIMITS
BLOCK
```

`BLOCK` currently applies when:

- state or evidence references are missing;
- IDs are duplicated;
- a self-transition is declared;
- time windows are invalid or incompatible;
- a claim exceeds its admissible evidence level;
- graph structure is malformed.

Causal gaps are returned explicitly even when the graph remains `ACCEPT_WITH_LIMITS`.

## TRACE reference case

`examples/trace-transition-network.v0.1.json` represents five bounded transitions:

```text
unresolved super-archaic source
  -> Denisovan population

unresolved ghost source
  -> sapiens ancestors

Denisovan population
  -> sapiens ancestors

sapiens ancestors
  -> observed modern genomes

modern genomes
  -> functional-annotation enrichment signal
```

The first two paths remain computational inferences. The model contains no direct genome from either unresolved source population and no taxonomic assignment.

The functional-enrichment transition is association-level. Required bridges from genomic annotation to expression, cellular effect, organism phenotype, and fitness advantage remain unobserved. Therefore adaptive causality is not admitted.

Run:

```bash
python scripts/analyze_transition_network.py \
  examples/trace-transition-network.v0.1.json \
  --enforce
```

Expected verdict:

```text
ACCEPT_WITH_LIMITS
```

Expected unresolved result:

```text
CAUSAL_GAP
```

## Ecosystem integration

### Causal Memory Layer

CML can preserve each accepted state, transition, evidence reference, contradiction, and supersession as a causal-memory record.

### ProofPath

ProofPath can bind a transition claim to the exact evidence path used to admit or block it.

### LiminalDB

LiminalDB can persist transition-network analyses as append-only events and prove replay-equivalent recovery without converting persistence into scientific approval.

### Transition Intelligence Protocol

TIP proposes the next candidate transition. Kairos verifies whether the timing, evidence path, and claim scope justify admitting it as a bounded research candidate.

## Safety and authority

Every v0.1 result is research-only.

The engine does not authorize:

- wet-lab work;
- genetic modification;
- animal or human experimentation;
- clinical decisions;
- treatment or diagnosis;
- deployment;
- merge.

`ACCEPT_WITH_LIMITS` means only that the declared graph is structurally and semantically admissible under the current research contract.

## v0.2 candidates

1. Path enumeration between selected start and target states.
2. Counterfactual removal of an edge or assumption.
3. Sensitivity analysis over evidence weights.
4. Explicit supersession and graph-diff contracts.
5. LiminalDB append/replay receipts.
6. CML and ProofPath interoperability records.
7. Independent-method comparison for the TRACE case.
