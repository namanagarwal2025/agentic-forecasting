# Agentic Forecasting Bootcamp Workplan

This is the single planning source of truth for the Agentic Forecasting Bootcamp. It defines what we intend to build for cohort 1, what we will demo, what we will leave as participant extension work, and how the remaining work is sequenced.

Participant-facing setup and usage instructions live in the repository `README.md` files. Historical planning notes, older charters, and previous backlog documents have been retired in favor of this workplan.

> **Status (June 2026): winding down.** The four reference experiments targeted for cohort 1 — Getting Started, Food Price, Energy/Oil, and BoC Rate Decisions — are complete, and the S&P 500 numerical comparison is the one experiment still in active development. The detailed build-out work items have been consolidated into [Completed](#completed), a short list of [Outstanding work for cohort 1](#outstanding-work-for-cohort-1), and a [Participant Project Ideas](#participant-project-ideas-future-work) menu. As development closes out, this section of the document doubles as the extension menu participants can pick from during Build Days.

## Program Goal

The bootcamp should give participants a stable environment, a small set of realistic forecasting tasks, and reference implementations that demonstrate how conventional forecasting, LLM processes, and agentic forecasting systems can be compared or explored.

The priority is readiness for cohort 1. A second cohort may happen, but all planning decisions should be made against the cohort 1 dates.

## Key Dates

| Date       | Milestone                      | Required state                                                                                                                                                                                                 |
| ---------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| May 21     | Information session            | Energy/oil 2026 case study is demo-ready as a storytelling and pitch artifact. It should show a univariate forecast, a futures-aware or multivariate forecast, and an agentic/news-grounded scenario analysis. |
| June 18    | Technical readiness checkpoint | Environment, core package APIs, S&P 500 reference slice, and agent/code-execution integration plan are stable enough for onboarding preparation.                                                               |
| June 25    | Technical onboarding begins    | Participants can sync the environment, populate approved data caches, run current reference notebooks, and understand the extension menu.                                                                      |
| July 8-9   | Learn Days                     | Repository, environment, and reference implementations are polished. Ethan-owned lecture tasks are tracked but not planned in detail here.                                                                     |
| August 4-6 | Build Days                     | Participants define and run experiments, extend methods, add data sources within approved scope, and customize agentic forecasters from the stable base.                                                       |

## Scope

### Forecasting Taxonomy

Keep three concepts separate throughout planning and implementation:

- **Task / output modality:** what is being predicted. Continuous forecasts predict future values or distributions for a time series. Discrete-event forecasts predict the probability of a clearly resolved event and are evaluated with binary scoring rules such as Brier score.
- **Forecasting method:** how the prediction is produced. Numerical forecasters, LLM Processes, and agentic forecasters are method families that can be applied to continuous tasks, discrete-event tasks, or reframed versions of either.
- **Interaction mode:** how the system is used. Track 1 produces standardized `Prediction` objects for evaluation. Track 2 supports interactive analysis, scenario exploration, monitoring, and Q&A without head-to-head scoring.

Discrete-event forecasting is not a peer category to LLMPs or agentic forecasters. It is an output modality. A time series task can often be reframed as a discrete-event question, and time series models can often provide point-in-time forecasts, features, or probabilities that benchmark or support discrete-event predictors.

### Formal Reference Experiments

These are the experiments we plan to make runnable, documented, and suitable for cohort 1 participants.

| Experiment                  | Role                                                                                             | Dataset(s)                         | Owner     | Status                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Getting Started             | Smallest continuous forecasting walkthrough using CPI gasoline.                                  | StatCan                            | —         | **Complete.** h=1 (1-month ahead); backtest 2000–2025; eval Jan 2025–Mar 2026.                                                        |
| Food Price Forecasting      | CFPR-style multivariate CPI task and clean model selection case study comparing baselines & LLMPs.| StatCan; optional FRED extensions  | Ethan     | **Complete.** Baselines and LLMPs integrated. Mini specs for fast iteration. No protected historical eval (leakage). |
| Financial Markets - S&P 500 | Deep numerical-methods comparison; first formal financial-markets Track 1 template.              | yfinance; optional FRED covariates | Behnoosh  | **In progress.** Net-new reference implementation.                                                                                     |
| Energy/Oil                  | Daily WTI forecasting with proper eval; sponsor-facing context-driven case.                      | yfinance                           | Ethan     | **Complete.** Stateless capability track (NB01–04: Prophet → LLMP → news-grounded → code-executing) plus an adaptive-agent track — self-directed study on 2025 data (NB05) and protected before/after eval on 2026 (NB06). See [adaptive-agent-notebook-design.md](adaptive-agent-notebook-design.md). |
| BoC Rate Decisions          | Sole discrete-event reference experiment: 3-way cut/hold/hike direction (RPS) as the primary task; binary cut framing (Brier) kept as a compact reference. Validation surface for `CategoricalForecast` and `BinaryForecast`. | StatCan, FRED, public BoC material | Ethan     | **Complete.** Discrete harness (payload_type, ordered categories, Brier + RPS, origin_dates) in core; data layer, four predictors per framing, three notebooks, protected 2025-26 direction eval spec, cutoff-aware press-release ingestion, and a Langfuse-native reasoning-alignment evaluator (NB03). Extensions: press releases as predictor context, live forecasting. |

### Energy/Oil 2026 Case Study

Energy/oil is the strongest sponsor-facing story for the May 21 information session and the flagship interactive Forecasting Analyst Agent demo.

The motivating scenario is early-2026 energy price volatility driven by war in the Persian Gulf. The demo should feel like a realistic sponsor use case: a logistics, transportation, manufacturing, or finance team wants to anticipate oil, fuel, or related energy-price risk at a useful daily or weekly horizon.

The case study should demonstrate the bootcamp thesis:

1. A univariate forecast is transparent and useful, but blind to regime-breaking context.
2. A futures-aware or multivariate forecast gives market-informed conventional methods a fair chance.
3. An agentic forecaster can retrieve contemporaneous news, reason through scenarios, run code, and explain how assumptions change the forecast.

The interactive Track 2 example can support questions such as: "Analyze what has happened with energy prices in 2026 so far. Then show me two forecasts: one where the Strait of Hormuz stays closed for another month and one where it reopens tomorrow."

**May 21 demo:** complete and delivered. The information-session notebooks are archived in `playground/energy_case_study/`; the formal reference lives in `implementations/energy_oil_forecasting/`.

**Status (Ethan):** Complete. Reference rebuilt with decomposed helper modules (`prophet_baseline.py`, `viz.py`, `tasks.py`, `analysis.py`), a four-notebook stateless capability curriculum (NB01–04), and an adaptive-agent track (NB05 self-directed study → NB06 protected before/after eval) that showcases a forecaster which learns a strategy from data.

### Participant Extension Ideas

None of these are required for cohort 1 readiness; they are collected, alongside the deferred build-out items, in [Participant Project Ideas](#participant-project-ideas-future-work) below so Build Days has a single menu to pick from.

## Architecture Decisions To Preserve

Repository layout as implemented today:

```text
aieng-forecasting/aieng/forecasting/
  data/          # adapters, cutoff enforcement, series storage
  evaluation/    # backtest, eval, artifacts, scoring
  methods/       # reusable Predictor implementations
                   # (baselines, numerical, llm_processes, agentic)

implementations/<use-case>/
  README.md, notebooks, helper modules, task-specific agents
  specs/         # (target layout) YAML BacktestSpec / EvalSpec co-located with experiment

playground/      # pre-reference demos and exploration (not cohort reference experiments)
```

Additional principles:

- `aieng-forecasting` owns stable infrastructure: data service, cutoff enforcement, evaluation interfaces, prediction payloads, artifact storage, and reusable agent backbone.
- `aieng.forecasting.methods` owns reusable concrete `Predictor` implementations.
- `implementations/<use-case>/` owns notebooks, task-specific configuration, prompts, experiment READMEs, and (target) co-located specs.
- Darts is the primary numerical forecasting library.
- Pydantic structured outputs and strong, mypy-compliant typing are the default for core interfaces.
- StatCan, FRED, and yfinance are the reference data sources.
- Continuous and discrete-event forecasts are output modalities; numerical forecasters, LLMPs, and agentic forecasters are method families.
- Track 1 uses standardized `Prediction` outputs and comparable evaluation across applicable methods and output modalities.
- Track 2 is a capability showcase for scenario analysis, monitoring, conversational analysis, and reasoning. It is not scored head-to-head in this bootcamp.
- Code, notebooks, specs, and documentation should remain aligned; READMEs are part of the product.

New reference experiments should co-locate YAML specs under `implementations/<use-case>/specs/`.

## Agent Ownership And Modes

Franklin's agent-related scope was a short infrastructure task: get a configurable Dockerized E2B sandbox running for a basic Google ADK agent. E2B template build and root README setup exist; a dedicated handoff note for Ali is still TBD.

Ali owns the broader agentic forecasting architecture, including the Context Retrieval Agent, the Analyst Agent, agent skills, prompts, tool contracts, and experiment-specific configurations. Ali is also refining the LLMP implementation (PR incoming).

Ethan owns energy/oil reference promotion and the BoC rate-decision reference build.

The agent architecture should support two modes:

- Track 1 prediction mode: configured primarily to emit standardized `Prediction` objects through the repository evaluation interfaces.
- Track 2 interactive analyst mode: configured for conversation, scenario analysis, deployment, evidence gathering, and code execution. Its interaction surface may differ substantially from Track 1 because it is not evaluated head-to-head.

The likely decomposition is:

- Context Retrieval Agent: Gemini-backed specialist for Google Search grounding, news retrieval, and source-aware context gathering.
- Analyst Agent: provider-flexible reasoning and code-execution agent that can use repository skills, call conventional forecasting routines, delegate retrieval tasks, and synthesize forecasts or analyses.

**LLM routing (open):** Vector offers a shared proxy (`proxy.vectorinstitute.ai`) that does not support the Gemini-native search and code-exec features our agents use. Plan: keep those on direct Gemini sub-agents; use the proxy for LLMP if we adopt it. See [`planning-docs/vector-llm-proxy.md`](vector-llm-proxy.md).

## Work Items

The cohort 1 build-out is essentially complete. What remains is consolidated below: a record of what shipped, the short list of work still open for cohort 1, and a menu of extensions framed as participant projects. (The original item-by-item A–K breakdown lived here during the build; it has been folded into these three lists now that most of it is done.)

### Completed

- **Documentation & repo hygiene** — workplan is the single planning source of truth; retired docs redirect here; READMEs, notebook markdown, YAML comments, and docstrings match on-disk reality; specs co-located under `implementations/<use-case>/specs/`.
- **Getting Started, Food Price, Energy/Oil, and BoC reference experiments** — all runnable and documented; see the [reference-experiments table](#formal-reference-experiments) for per-experiment scope.
- **Energy/oil promotion + adaptive agent** — promoted out of `playground/`; standard `Predictor`/eval wiring (`energy_oil_backtest.yaml`, `energy_oil_eval.yaml`); 4-notebook stateless curriculum plus the NB05/06 adaptive-agent track (`AdaptiveSkillStore`-backed strategy state, `build_skill_tools()`, `curriculum.py`, 2025-train / 2026-eval split).
- **BoC discrete-event harness** — `payload_type` (continuous/binary/categorical) with ordered categories, Brier + unnormalized-RPS dispatch in `backtest()`/`evaluate()`, explicit `origin_dates`; binary + categorical LLMP and frequency predictors; the analyst agent; cutoff-aware press-release ingestion (`PressReleaseStore`) and a Langfuse-native reasoning-alignment evaluator (NB03).
- **LLMP** — `ContinuousLLMPredictor` merged and integrated in food CPI; binary/categorical variants added for BoC.
- **Track 1 food CPI agent baseline** — `AgentPredictor` + food-specific agent in `implementations/food_price_forecasting/analyst_agent/`; v1 runs without ADK skills (rationale in `docs/adk-skills-guide.md`).
- **May 21 energy/oil information session** — delivered; notebooks archived in `playground/energy_case_study/`.

### Outstanding work for cohort 1

- **S&P 500 reference (Behnoosh)** — the one reference experiment still in active development. Define target/horizons/anti-leakage rules, add specs under `implementations/sp500_forecasting/specs/`, build the deep numerical-methods comparison notebook, and document it as the reusable financial-markets template. Reusable yfinance ingestion already exists in `aieng.forecasting.data`.
- **Live testing infrastructure (Ethan + Ali)** — record predictions from reference methods (energy first, expandable), persist predictions and reasoning traces, and resolve them as horizons mature. A true prospective Track 1 test, distinct from Track 2 scoring. Daily energy data makes this most valuable when started early — the sooner predictions begin, the more horizons resolve before Build Days.
- **Environment readiness** — the E2B template and root README setup path exist and minimum participant setup is documented; remaining are Franklin's E2B handoff note for Ali, and a live `adk web` / one-predict smoke check against google-adk 2.0.0 (CI is green, but agent tests are mostly mocked).
- **Learn Days content (Ethan, July 8–9)** — intro to time series forecasting, agentic/LLM forecasting overview, LLM Processes, and ForecastBench framing. Tracked lightly; not planned in detail here.

### Participant Project Ideas (future work)

Extensions deliberately left for participants — each builds on a complete reference experiment and has a clear seam in the code. None block cohort 1 readiness; together they are the Build Days menu.

**Deepen a reference experiment**

- **BoC live forecasting** — extend `meeting_schedule.yaml` with the Bank's published future dates and forecast each announcement the day before it happens: genuinely out-of-sample, and the honest test that backtest leakage precludes. Needs annual calendar maintenance.
- **Reports as predictor context** — wire cutoff-filtered documents into the *forecast* prompt: BoC press releases / MPRs through the LLMP `user_prompt_suffix` or the `build_boc_news_config` retrieval seam, and the analogous food-CPI CFPR wiring (extraction already exists; mirror BoC's `PressReleaseStore`). Measure the lift over the quantitative-only baseline.
- **Memory-augmented agent** — an agent that learns from its own resolved prediction errors over time; a generalization of the energy adaptive agent across use cases. Exploratory.

**Agent & analyst depth**

- ADK skills reintroduction (see `docs/adk-skills-guide.md` for the design rules learned the hard way), richer E2B code-execution configs, prompt/context-formatting optimization, and Track 2 interactive analyst configurations per use case.

**Broaden coverage**

- Transpose the S&P 500 Track 1 template to additional energy commodities, or to other liquid assets / equities / indices.
- Add richer FRED covariates for food, energy, or financial markets.
- Reframe a continuous target as a binary or categorical question (the BoC harness shows the pattern).
- Add time-series foundation models or additional numerical methods once a reference experiment has one strong baseline.
- Explore ForecastBench, by request or as Learn Days discussion material.

**Core-library follow-up**

- `resolution_fn` on `ForecastingTask` is still a placeholder; the derived-event-series approach avoids needing dispatch today, but spread/level-target framings will eventually force it.

## Explicit Non-Goals For Cohort 1

- No NYISO, IESO, or grid-operator reference build.
- No ForecastBench reference experiment unless requested or time permitting.
- No live scored evaluation for open-ended conversational or scenario agents (Track 2).
- No model fine-tuning or custom training runs.
- No broad method zoo before each reference experiment has one strong, runnable baseline.
- No public live benchmark or Metaculus-style production integration.
- No duplicate spec locations (one `specs/` directory per use case).

Live testing of Track 1 predictors (the live-testing infrastructure under [Outstanding work](#outstanding-work-for-cohort-1)) **is in scope** and distinct from Track 2 scoring.

## Risk Watchlist

- **Vector LLM proxy vs Gemini-native agent features** — proxy cannot replace Google Search or Gemini in-model code exec; keep those on direct Gemini sub-agents. LLMP-on-proxy is viable (OpenAI models preferred). See [`planning-docs/vector-llm-proxy.md`](vector-llm-proxy.md).
- **google-adk 2.0.0** — merged May 20, 2026; CI green but agent smoke tests are mostly mocked. Run live `adk web` / one predict call before next agent feature work.
- **Spec co-location** — energy and BoC ship co-located specs; ensure the S&P 500 experiment follows the same `implementations/<use-case>/specs/` convention.
- **LLM leakage** — historical backtest scores for LLMP and agentic predictors are upper bounds, not clean benchmarks. Live testing is the honest evaluation path; for BoC, the reasoning-alignment evaluator (NB03) is the complementary process check where scores are least trustworthy.
- **Live testing timeline** — start energy predictions ASAP to maximize resolved horizons before Build Days (August 4-6).

## Documentation Maintenance

When planning or architectural decisions change, update this file first. Then update the relevant README files if setup instructions, repo layout, experiment scope, or participant-facing guidance changed.

Historical notes in `planning-docs/archive/` and `planning-docs/project-charter-final.md` are useful for archaeology but are not binding. This workplan and the READMEs are the maintained documentation set for cohort 1 readiness.
