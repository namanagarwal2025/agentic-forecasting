"""Naive last-value predictor — the floor baseline for any continuous forecasting task.

``LastValuePredictor`` predicts that the next observation will equal the most
recently observed value, with no uncertainty spread (all quantiles equal the
point forecast). It is task-agnostic and applies to any ``ForecastingTask``
with a continuous series target.

Use this as:

1. **A performance floor.** Run it first on any new task. Every other predictor
   should beat it. If yours doesn't, something is wrong with your model.

2. **A readable reference implementation.** The code is annotated step-by-step
   to show exactly how to satisfy the ``Predictor`` ABC — what fields are
   required, how to compute ``forecast_date``, and how to construct a
   ``Prediction``. Copy the structure and replace the forecast logic.

Usage::

    from methods.naive import LastValuePredictor
    from aieng.forecasting.evaluation import backtest, BacktestSpec

    result = backtest(predictor=LastValuePredictor(), spec=spec, data_service=svc)
    print(f"Naive mean CRPS: {result.mean_crps:.4f}")  # your model must beat this
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from aieng.forecasting.data.context import ForecastContext
from aieng.forecasting.evaluation.prediction import (
    STANDARD_QUANTILES,
    ContinuousForecast,
    Prediction,
)
from aieng.forecasting.evaluation.predictor import Predictor
from aieng.forecasting.evaluation.task import ForecastingTask


class LastValuePredictor(Predictor):
    """Naive baseline: forecast the most recently observed value at all quantiles.

    All quantile levels receive the same value as the point forecast, producing
    a degenerate distribution with zero spread. This gives the worst possible
    calibration score — a well-calibrated model should spread its quantiles to
    reflect genuine uncertainty.

    Parameters
    ----------
    None
    """

    # ------------------------------------------------------------------
    # Step 1: give your predictor a stable string ID.
    # This appears in BacktestResult and every Prediction record,
    # so changing it mid-experiment will break comparisons.
    # ------------------------------------------------------------------
    @property
    def predictor_id(self) -> str:
        """Return a stable identifier for this predictor."""
        return "last_value_naive"

    # ------------------------------------------------------------------
    # Step 2: implement predict().
    #
    # Arguments:
    #   task    — ForecastingTask: defines the problem (target series,
    #             horizon, frequency). Read-only; do not modify it.
    #   context — ForecastContext: your data access object. All series
    #             returned by context.get_series() are already filtered
    #             to context.as_of — you cannot accidentally access
    #             future data.
    #
    # Return:
    #   A fully constructed Prediction object (see below).
    # ------------------------------------------------------------------
    def predict(self, task: ForecastingTask, context: ForecastContext) -> Prediction:
        """Produce a last-value naive forecast for the given task and context."""
        # ------------------------------------------------------------------
        # Step 3: fetch the target series.
        # Returns a DataFrame with columns: timestamp, value, released_at.
        # Rows are already cut off at context.as_of.
        # ------------------------------------------------------------------
        series_df = context.get_series(task.target_series_id)

        # ------------------------------------------------------------------
        # Step 4: produce a forecast.
        # Replace everything below with your model logic.
        # Here we just take the last observed value as the point forecast.
        # ------------------------------------------------------------------
        last_value = float(series_df["value"].iloc[-1])

        # ------------------------------------------------------------------
        # Step 5: build the ContinuousForecast payload.
        # point_forecast: your central estimate (typically median).
        # quantiles: a dict mapping quantile level → forecast value.
        #   STANDARD_QUANTILES = [0.05, 0.10, ..., 0.90, 0.95]
        #   The evaluation engine uses these to compute CRPS.
        #   A naive predictor with no uncertainty puts the same value
        #   at every quantile — real models spread them out.
        # ------------------------------------------------------------------
        payload = ContinuousForecast(
            point_forecast=last_value,
            quantiles=dict.fromkeys(STANDARD_QUANTILES, last_value),
        )

        # ------------------------------------------------------------------
        # Step 6: compute the forecast date.
        # This is the future timestamp being predicted:
        #   context.as_of + task.horizon steps at task.frequency.
        # The harness uses this to look up the ground-truth observation
        # when scoring.
        # ------------------------------------------------------------------
        forecast_date: datetime = (
            pd.Timestamp(context.as_of) + pd.tseries.frequencies.to_offset(task.frequency) * task.horizon
        ).to_pydatetime()

        # ------------------------------------------------------------------
        # Step 7: wrap everything in a Prediction and return it.
        # All fields except metadata are required.
        # Use metadata to attach side-channel data (model stats, sources,
        # trace IDs, etc.) — the harness ignores it but passes it through.
        # ------------------------------------------------------------------
        return Prediction(
            predictor_id=self.predictor_id,
            task_id=task.task_id,
            issued_at=datetime.now(tz=timezone.utc).replace(tzinfo=None),
            as_of=context.as_of,
            forecast_date=forecast_date,
            payload=payload,
        )
