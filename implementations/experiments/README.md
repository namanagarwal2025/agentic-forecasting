# implementations/experiments

This directory contains **use-case experiments** — notebooks, reference specs,
and task configuration for each forecasting use case in the bootcamp. Each
subdirectory is a self-contained use case with its own `README.md` and learning
path.

This directory is **not** a Python package. Nothing here is imported by other
code. All files are run or opened directly (Jupyter notebooks, Python scripts).

---

## Directory layout

```
experiments/
├── economic_forecasting/    # Canada CPI backtesting (StatCan)
│   ├── README.md            # learning path for this use case
│   ├── cpi_data_exploration.ipynb
│   └── cpi_backtest_demo.ipynb
│
├── cfpr/                    # Canada's Food Price Report (planned)
├── boc_rate_decisions/      # Bank of Canada rate decisions (planned)
└── ...
```

---

## What belongs here

- Jupyter notebooks exploring data and demonstrating methods on a specific task
- `ForecastingTask` definitions and reference spec YAMLs specific to a use case
- Task-specific predictor configuration (e.g. prompts tuned for a particular
  dataset or question)

## What does NOT belong here

- Reusable predictor implementations — those live in
  `implementations/methods/` and are imported from there
- Core infrastructure — that lives in `aieng-forecasting`

---

## Adding a new use case

1. Create `experiments/<use-case>/`
2. Add a `README.md` with a learning path (see `economic_forecasting/README.md`
   as a template)
3. Add a data population script to `scripts/` if a new data source is needed
4. Define a `ForecastingTask` and add a reference `BacktestSpec` YAML to
   `reference_specs/`
5. Write a demo notebook that walks through the task end-to-end

The second use case should take significantly less effort than the first — the
adapter pattern, task definition, spec structure, and notebook scaffolding are
all established.
