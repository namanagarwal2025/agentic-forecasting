"""Tests for ``methods.darts_regression``.

Covers both predictors (:class:`DartsLinearRegressionPredictor`,
:class:`DartsLightGBMPredictor`) across two fits each: univariate and with a
pair of past covariates.  Each test asserts the three properties that matter
for evaluation compatibility:

1. A :class:`Prediction` is returned with the expected ``predictor_id`` and
   ``forecast_date``.
2. The payload carries all ``STANDARD_QUANTILES`` keys.
3. Quantiles are monotonically non-decreasing — i.e. the distribution is
   valid, not a degenerate point estimate.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import pytest
from aieng.forecasting.data import DataService, SeriesMetadata
from aieng.forecasting.data.adapters.base import BaseAdapter
from aieng.forecasting.evaluation.prediction import STANDARD_QUANTILES, Prediction
from aieng.forecasting.evaluation.task import ForecastingTask
from methods.darts_regression import (
    DartsLightGBMPredictor,
    DartsLinearRegressionPredictor,
)


HORIZON = 6
FREQUENCY = "MS"
AS_OF = datetime(2020, 12, 1)


class _InMemoryAdapter(BaseAdapter):
    """Adapter returning a supplied DataFrame unchanged."""

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df.copy()

    def fetch(self) -> pd.DataFrame:
        """Return the supplied DataFrame."""
        return self._df.copy()


def _seasonal_series(
    start: str = "2000-01-01",
    periods: int = 240,
    amplitude: float = 10.0,
    trend: float = 0.5,
    noise: float = 1.0,
    seed: int = 0,
) -> pd.DataFrame:
    """Generate a synthetic monthly series with trend + annual seasonality + noise."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, periods=periods, freq="MS")
    t = np.arange(periods, dtype=float)
    values = 100.0 + trend * t + amplitude * np.sin(2 * np.pi * t / 12) + rng.normal(0, noise, periods)
    return pd.DataFrame({"timestamp": dates, "value": values})


@pytest.fixture
def svc() -> DataService:
    """DataService populated with a target and two synthetic covariate series."""
    service = DataService()

    target_df = _seasonal_series(seed=1)
    service.register(
        "target",
        _InMemoryAdapter(target_df),
        SeriesMetadata(
            series_id="target",
            description="Synthetic target",
            source="test",
            units="index",
            frequency=FREQUENCY,
        ),
    )

    cov_a = _seasonal_series(amplitude=5.0, trend=0.1, seed=2)
    service.register(
        "cov_a",
        _InMemoryAdapter(cov_a),
        SeriesMetadata(
            series_id="cov_a",
            description="Synthetic covariate A",
            source="test",
            units="index",
            frequency=FREQUENCY,
        ),
    )

    cov_b = _seasonal_series(amplitude=2.0, trend=0.0, noise=0.5, seed=3)
    service.register(
        "cov_b",
        _InMemoryAdapter(cov_b),
        SeriesMetadata(
            series_id="cov_b",
            description="Synthetic covariate B",
            source="test",
            units="index",
            frequency=FREQUENCY,
        ),
    )

    return service


@pytest.fixture
def task() -> ForecastingTask:
    """Build the standard 6-month horizon task against the synthetic target."""
    return ForecastingTask(
        task_id="synthetic_6m",
        target_series_id="target",
        horizon=HORIZON,
        frequency=FREQUENCY,
        description="Synthetic 6-month forecast for unit tests.",
    )


def _assert_valid_prediction(
    pred: Prediction,
    expected_id: str,
    expected_as_of: datetime,
) -> None:
    """Assert shape, id, date, quantile coverage and monotonicity."""
    assert pred.predictor_id == expected_id
    assert pred.as_of == expected_as_of
    expected_fd = (pd.Timestamp(expected_as_of) + pd.DateOffset(months=HORIZON)).to_pydatetime()
    assert pred.forecast_date == expected_fd

    quantiles = pred.payload.quantiles
    for q in STANDARD_QUANTILES:
        assert q in quantiles

    levels = sorted(quantiles)
    values = [quantiles[q] for q in levels]
    assert all(a <= b + 1e-9 for a, b in zip(values, values[1:])), (
        f"Quantiles not monotonic: {list(zip(levels, values))}"
    )

    spread = quantiles[0.95] - quantiles[0.05]
    assert spread > 1e-6, "Predictive spread collapsed to a point — not probabilistic."


def test_linear_regression_univariate(svc: Any, task: Any) -> None:
    """LinearRegression predictor without covariates returns a valid distribution."""
    pred = DartsLinearRegressionPredictor(lags=12, num_samples=200).predict(
        task, svc.context(AS_OF)
    )
    _assert_valid_prediction(pred, "darts_linreg", AS_OF)
    assert pred.metadata["covariates"] == []


def test_linear_regression_with_covariates(svc: Any, task: Any) -> None:
    """LinearRegression predictor with past covariates returns a valid distribution."""
    pred = DartsLinearRegressionPredictor(
        lags=12,
        lags_past_covariates=12,
        covariate_series_ids=["cov_a", "cov_b"],
        num_samples=200,
    ).predict(task, svc.context(AS_OF))
    _assert_valid_prediction(pred, "darts_linreg_cov", AS_OF)
    assert pred.metadata["covariates"] == ["cov_a", "cov_b"]


def test_lightgbm_univariate(svc: Any, task: Any) -> None:
    """LightGBM predictor without covariates returns a valid distribution."""
    pred = DartsLightGBMPredictor(lags=12, num_samples=200).predict(
        task, svc.context(AS_OF)
    )
    _assert_valid_prediction(pred, "darts_lightgbm", AS_OF)
    assert pred.metadata["covariates"] == []


def test_lightgbm_with_covariates(svc: Any, task: Any) -> None:
    """LightGBM predictor with past covariates returns a valid distribution."""
    pred = DartsLightGBMPredictor(
        lags=12,
        lags_past_covariates=12,
        covariate_series_ids=["cov_a", "cov_b"],
        num_samples=200,
    ).predict(task, svc.context(AS_OF))
    _assert_valid_prediction(pred, "darts_lightgbm_cov", AS_OF)
    assert pred.metadata["covariates"] == ["cov_a", "cov_b"]
