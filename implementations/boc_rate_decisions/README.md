# BoC Rate Decisions

Predicts the **probability of a Bank of Canada rate cut at the next fixed
announcement date** — the repository's reference implementation for
**discrete event prediction**. Where every other use case forecasts a
continuous trajectory and scores it with CRPS, this one resolves a 0/1
outcome on an irregular meeting calendar and scores probabilities with the
**Brier score**.

It is the validation surface for the binary half of the evaluation harness:
`ForecastingTask.payload_type == "binary"`, `BinaryForecast` payloads,
Brier dispatch in `backtest()`/`evaluate()`, and explicit `origin_dates` on
specs. If this is your first session with the repo, start at
`implementations/getting_started/`; come here when you want to see the same
harness applied to a problem that is not a time series.

> See `planning-docs/bootcamp-workplan.md` for current cohort 1 scope. This
> is workplan item E, the sole binary/discrete-event reference experiment.

---

## Prediction task

**Question:** will the Bank of Canada LOWER its target for the overnight
rate at the fixed announcement date occurring one day after the forecast
origin? Outcome is 1 for a decrease of any size; holds and hikes are both 0.

- **Target series:** `boc_rate_cut_event` — derived 0/1 series, one
  observation per fixed announcement date (8 per year), `released_at` = the
  announcement date itself.
- **Origins:** `announcement_date − 1 day`, listed explicitly in the specs
  via `origin_dates` (the meeting calendar is irregular; a stride cannot
  produce it).
- **Horizon:** 1 day — the forecast date lands exactly on the announcement,
  and cutoff enforcement excludes the decision itself.
- **Metric:** Brier score \((p - y)^2\), with the Brier *skill* score
  against the historical base rate as the headline comparison. With ~12%
  cuts, the base rate alone scores ≈ 0.10 — the bar every model must clear.
- **Why cuts (not hikes or any-change):** cuts are the question sponsors and
  markets actually ask, the class imbalance is pedagogically honest, and the
  2015 / 2020 / 2024-25 easing cycles give the backtest three distinct
  regimes to detect.

**Excluded by design:** unscheduled (emergency) announcements — there has
been exactly one since 2009 (March 27, 2020). It is recorded in the
calendar file and used for validation, but no forecast origin targets it.

---

## Data

| Ingredient | Source | Notes |
|---|---|---|
| Daily target for the overnight rate | StatCan 10-10-0139-01 (`StatCanAdapter`, `release_lag_days=1`) | The raw policy path |
| Fixed announcement dates 2009–2026 | `meeting_schedule.yaml` (committed, curated) | Required to observe *holds*; sourced from the Bank's announcement archive, validated against the rate series |
| `boc_rate_cut_event` | `BoCRateCutEventAdapter` (use-case adapter) | Joins calendar + daily rate; robust to the 2021 effective-date regime change |
| 2-year GoC benchmark yield | StatCan 10-10-0139-01 | Market-implied policy expectations — the strongest single covariate |
| CPI all-items | StatCan 18-10-0004-11 | The Bank targets 2% CPI inflation |
| Unemployment rate | FRED `LRUNTTTTCAM156S` | Labour-market pressure |

Populate the cache once (`FRED_API_KEY` in `.env` needed for the
unemployment covariate; the script degrades gracefully without it):

```bash
uv run python scripts/fetch_boc.py
```

**Cutoff discipline.** Monthly adapters carry *approximate* `released_at`
stamps that are optimistic by roughly one month (the lag is measured from
the month-start timestamp; StatCan publishes ~3 weeks after the month
ends). All predictors in this use case therefore drop the newest visible
reference month of any monthly covariate — see
`predictors/logistic_baseline.py::build_feature_row`, which both the
logistic model and the agent prompt builder share. Notebook 01 demonstrates
the full chain at a real origin.

**Maintenance:** extend `meeting_schedule.yaml` each year when the Bank
publishes its next calendar (provenance notes are in the file header), and
re-run `scripts/fetch_boc.py --refresh` to pick up new announcements.

---

## Predictors

| Group | Predictor | Information set |
|---|---|---|
| Floor baseline | `HistoricalFrequencyPredictor` (core package) | Past outcomes only — the constant base rate |
| Conventional | `predictors/logistic_baseline.py` | Fit-at-origin logistic regression on four leak-safe macro features (yield spread, rate momentum, inflation gap, unemployment momentum) |
| LLMP | `predictors/llmp_binary.py` → `BinaryProbabilityLLMPredictor` | Outcome history + BoC context block; one structured call, direct probability elicitation |
| Agentic | `analyst_agent/` → `AgentPredictor` + `DiscreteAgentForecastOutput` | Rate path + outcome history + **the same macro features as the logistic model** |

The agent/logistic pairing is deliberate: identical indicators, so the
comparison isolates *conventional fitting* vs *LLM reasoning*. The agent
also emits `reasoning` and `key_signals` per meeting — the input for the
planned reasoning-alignment evaluator (see roadmap below).

> **Leakage note:** frontier LLMs have seen news coverage of every
> historical BoC decision, and for a binary outcome a single recalled bit is
> the whole answer. Backtest Brier scores for the LLMP and agent are upper
> bounds on live skill; the conventional rows are the honest backtest
> comparison, and the protected 2025–2026 eval is the fairer LLM test.

---

## Reference specs

```
specs/
├── boc_rate_cut_backtest.yaml   # 120 origins, 2010–2024 (three easing cycles)
├── boc_rate_cut_eval.yaml       # 12 origins, Jan 2025 – Jun 2026, max_runs: 5
└── boc_rate_cut_smoke.yaml      # 3 origins in 2024 (one hold, two cuts) — dev loop
```

Notebook 02 selects between smoke and full via `EXPERIMENT_CONFIG`.

---

## Module layout

```
implementations/boc_rate_decisions/
├── meeting_schedule.yaml  # curated BoC announcement calendar (source-cited)
├── data.py                # build_boc_service(); event derivation + validation
├── predictors/            # logistic baseline; binary-LLMP recipe
├── analyst_agent/         # AgentConfig factories + prompt builder + predictor factory
├── analysis.py            # Brier leaderboard, calibration bins, rationales table
├── plots.py               # decision timeline, reliability curve, rate-path chart
├── specs/                 # backtest / eval / smoke YAML
├── 01_boc_data_exploration.ipynb   # framing, event derivation, cutoff walkthrough
└── 02_boc_rate_cut_experiment.ipynb # the experiment: 4 predictors, Brier, calibration
```

Tests live under `implementations/tests/boc_rate_decisions/` (event
derivation semantics; feature leak-safety).

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `01_boc_data_exploration.ipynb` | Problem framing (event vs time series), policy-rate history with decision markers, event derivation + schedule validation, class imbalance and the \(r(1-r)\) Brier floor, cutoff discipline at a real origin. |
| `02_boc_rate_cut_experiment.ipynb` | **Main experiment.** Smoke/full config switch, cached backtests for all four predictors, Brier leaderboard with skill scores, decision timeline, reliability curve, agent-reasoning inspection, budget-gated protected eval. |

---

## Roadmap — deferred components

Each has an explicit seam in the code:

1. **BoC communications as context** (Track 2 dependency, Ali): press
   releases and Monetary Policy Reports feed
   `BinaryProbabilityLLMPredictorConfig.user_prompt_suffix` and the
   `build_boc_news_config` retrieval sub-agent. Documents must be filtered
   by `released_at` exactly like series data.
2. **Reasoning-alignment evaluation**: an LLM evaluator comparing the
   agent's per-meeting `reasoning`/`key_signals` against the Bank's
   published rationale — a process metric to complement Brier, most
   valuable precisely where backtest scores are least trustworthy.
3. **Live forecasting**: extend the calendar with the Bank's published
   future dates and forecast each announcement the day before it happens —
   eight genuinely out-of-sample observations per year.
