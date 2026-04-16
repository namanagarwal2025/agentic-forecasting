"""Tests for :class:`FREDAdapter` disk-cache behaviour (no live network calls)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from aieng.forecasting.data.adapters.fred import FREDAdapter


def _raw_fred_series() -> pd.Series:
    """Minimal FRED-shaped Series with a DatetimeIndex and float values."""
    idx = pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01"])
    return pd.Series([100.0, 101.5, 99.2], index=idx, name="VALUE")


def _fred_cls_returning(raw: pd.Series) -> MagicMock:
    """MagicMock that, when called like ``Fred(api_key=...)``, returns a mock with ``get_series``."""
    instance = MagicMock()
    instance.get_series.return_value = raw
    return MagicMock(return_value=instance)


def test_fetch_without_cache_dir_always_hits_api() -> None:
    """``cache_dir=None`` disables caching — every fetch calls the API."""
    fake = _fred_cls_returning(_raw_fred_series())
    with patch("fredapi.Fred", fake):
        adapter = FREDAdapter("EXCAUS", api_key="fake-key", cache_dir=None)
        df1 = adapter.fetch()
        df2 = adapter.fetch()

    assert fake.return_value.get_series.call_count == 2
    assert list(df1.columns) == ["timestamp", "value", "released_at"]
    assert len(df1) == 3
    pd.testing.assert_frame_equal(df1, df2)


def test_fetch_writes_cache_then_reads_it(tmp_path: Path) -> None:
    """First fetch hits API and writes parquet; second fetch reads parquet only."""
    cache_dir = tmp_path / "fred"
    fake = _fred_cls_returning(_raw_fred_series())

    with patch("fredapi.Fred", fake):
        adapter = FREDAdapter("EXCAUS", api_key="fake-key", cache_dir=cache_dir)
        df1 = adapter.fetch()

    assert fake.return_value.get_series.call_count == 1
    cache_file = cache_dir / "EXCAUS.parquet"
    assert cache_file.exists()

    # Second fetch must NOT hit the API. Prove it by patching Fred to blow up.
    exploding = MagicMock(side_effect=AssertionError("fredapi.Fred must not be called"))
    with patch("fredapi.Fred", exploding):
        adapter2 = FREDAdapter("EXCAUS", api_key=None, cache_dir=cache_dir)
        df2 = adapter2.fetch()

    pd.testing.assert_frame_equal(df1, df2)


def test_refresh_forces_fetch_and_overwrites_cache(tmp_path: Path) -> None:
    """``refresh=True`` hits the API even when a cache exists."""
    cache_dir = tmp_path / "fred"
    cache_dir.mkdir()
    # Seed a stale cache with different values.
    stale = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2019-01-01"]),
            "value": [0.0],
            "released_at": pd.to_datetime(["2019-01-01"]),
        }
    )
    stale.to_parquet(cache_dir / "EXCAUS.parquet", index=False)

    fake = _fred_cls_returning(_raw_fred_series())
    with patch("fredapi.Fred", fake):
        adapter = FREDAdapter(
            "EXCAUS", api_key="fake-key", cache_dir=cache_dir, refresh=True,
        )
        df = adapter.fetch()

    assert fake.return_value.get_series.call_count == 1
    assert len(df) == 3
    written = pd.read_parquet(cache_dir / "EXCAUS.parquet")
    assert len(written) == 3


def test_missing_api_key_without_cache_raises(tmp_path: Path) -> None:
    """No cache file AND no API key -> ValueError on fetch()."""
    cache_dir = tmp_path / "fred-empty"
    with patch.dict("os.environ", {}, clear=True):
        adapter = FREDAdapter("EXCAUS", api_key=None, cache_dir=cache_dir)
        with pytest.raises(ValueError, match="FRED API key not provided"):
            adapter.fetch()


def test_populated_cache_works_without_api_key(tmp_path: Path) -> None:
    """A fully-populated cache can be read with no API key present."""
    cache_dir = tmp_path / "fred"
    cache_dir.mkdir()
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2021-01-01", "2021-02-01"]),
            "value": [50.0, 51.0],
            "released_at": pd.to_datetime(["2021-01-01", "2021-02-01"]),
        }
    )
    df.to_parquet(cache_dir / "CPIFABSL.parquet", index=False)

    with patch.dict("os.environ", {}, clear=True):
        adapter = FREDAdapter("CPIFABSL", api_key=None, cache_dir=cache_dir)
        result = adapter.fetch()

    assert len(result) == 2
    assert result["value"].tolist() == [50.0, 51.0]
