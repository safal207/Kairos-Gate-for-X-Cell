# TIP → Kairos Handoff v0.1

## Purpose

This profile transfers a justified research-transition proposal from Transition Intelligence Protocol (TIP) into Kairos Gate for phase-window assessment.

```text
IFP: starting state is sufficiently known
        ↓
TIP: transition proposal is justified and evidence-bounded
        ↓
Kairos: supported pre-intervention phase is assessed
        ↓
research-only classification
```

This is an interoperability profile, not a merger of the protocols.

## Version anchors

- TIP repository: <https://github.com/safal207/transition-intelligence-protocol>
- Example TIP commit: <https://github.com/safal207/transition-intelligence-protocol/commit/ac3013061996fd51821c1cfcad1664035912c299>
- Kairos repository: <https://github.com/safal207/Kairos-Gate-for-X-Cell>
- Handoff schema: `tip.kairos.handoff.v0.1`
- Target transition schema: `kairos.transition.v0.1`

Every real handoff must reference the exact TIP commit that produced it. The example commit is an anchor for the canonical synthetic fixture, not a permanent latest-version alias.

## TIP export fields

TIP provides:

- exact starting-state reference;
- tension;
- candidate cause;
- proposed transition;
- smallest justified research step;
- one or more evidence references;
- producer, timestamp, and content digest;
- exact repository commit reference.

## Kairos request fields

The receiving request adds:

- target Kairos schema;
- narrow research question;
- supported phase variables;
- forecast horizon.

Kairos later evaluates the full transition record, including phase evidence, identity preservation, toxicity or stress, reversibility, evidence quality, and timing confidence.

## Authority boundary

Every handoff must contain:

```json
{
  "classification": "RESEARCH_ONLY",
  "execution_authorized": false,
  "clinical_authorized": false,
  "merge_authorized": false
}
```

TIP does not authorize Kairos classification. Kairos classification does not authorize wet-lab, animal, human, clinical, deployment, approval, or merge actions.

## Validation

The public schema is mirrored inside the installed package and checked for equality in regression tests.

```bash
python -m pip install -e .
python -m unittest tests.test_handoff -v
```

Canonical example:

- `examples/tip-kairos-handoff.json`

Negative fixtures:

- `testdata/tip-kairos-negative-fixtures.json`

The negative cases remove starting state, cause, evidence, or provenance and must fail closed.