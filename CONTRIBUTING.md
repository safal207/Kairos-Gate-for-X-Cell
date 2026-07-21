# Contributing

Kairos Gate welcomes narrow, reproducible research contributions.

## Good contribution shapes

- metadata feasibility analysis;
- phase-conditioned benchmark design;
- leakage-resistant evaluation;
- schema or validator improvements;
- negative tests;
- uncertainty and calibration methods;
- corrections to unsupported or overstated claims.

## Required for a scientific claim

1. Define the variable and measurement method.
2. State the causal or predictive hypothesis.
3. Describe controls and confounders.
4. Provide a falsification condition.
5. Record provenance and limitations.
6. Avoid therapeutic or safety claims not supported by evidence.

## Development

```bash
python -m unittest discover -s tests -v
python -m kairos_gate examples/phase-conditioned-transition.json
```

Every new semantic rule should include at least one negative regression test.
