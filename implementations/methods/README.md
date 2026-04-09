# implementations/methods

This directory contains **reference predictor implementations** — concrete
`Predictor` subclasses that serve as documented starting points for bootcamp
participants. Each method here is cross-cutting: it can be applied to any
forecasting task (CPI, CFPR, BoC, equities, etc.) without modification.

Because `aieng-implementations` is a uv workspace package, these modules are
importable directly in any experiment notebook or script:

```python
from methods.base_llmp import BaseLLMPredictor
from methods.darts_arima import DartsAutoARIMAPredictor
```

---

## What belongs here

- Concrete `Predictor` subclasses that are **not** tied to a specific use case
- Implementations that a participant would use as-is or as a copy-paste starting
  point across more than one experiment
- Well-documented, linted Python modules (not notebooks)

## What does NOT belong here

- Task-specific configuration (prompts tuned for CFPR, specs, task YAMLs) — those
  live in `experiments/<use-case>/`
- Notebooks or experiment scripts — those live in `experiments/<use-case>/`
- Infrastructure or ABCs — those live in `aieng-forecasting` (`aieng.forecasting`)

---

## Relationship to `aieng-forecasting`

```
aieng-forecasting    # stable infrastructure: Predictor ABC, evaluation
(aieng.forecasting)  # harness, data service, agent backbone

implementations/     # uv workspace package (aieng-implementations)
methods/             #   reference implementations: concrete Predictor
(methods)            #   subclasses using that infrastructure

experiments/         # use-case notebooks & configs — run directly,
                     # never imported
```

`aieng-forecasting` must not contain concrete predictor implementations.
`implementations/methods` must not contain task-specific configuration.

---

## Current contents

| Module | Class | Description |
|---|---|---|
| `naive.py` | `LastValuePredictor` | Last-value naive baseline. Predicts the most recently observed value at all quantiles. The floor every predictor must beat. Also the annotated reference implementation — read this to understand the `Predictor` interface. |
