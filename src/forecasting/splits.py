"""Train/test split helpers for forecasting evaluation."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


def _as_month_start(timestamp: object) -> pd.Timestamp:
    return pd.Timestamp(timestamp).to_period("M").to_timestamp()


def _with_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.index, pd.DatetimeIndex):
        out = df.copy()
    elif "date" in df.columns:
        out = df.copy()
        out["date"] = pd.to_datetime(out["date"])
        out = out.set_index("date")
    else:
        raise ValueError("df must have a DatetimeIndex or a 'date' column.")

    out = out.sort_index()
    out.index = pd.to_datetime(out.index).to_period("M").to_timestamp()

    if out.index.has_duplicates:
        duplicated = out.index[out.index.duplicated()].unique()
        raise ValueError(f"Monthly date index has duplicates: {list(duplicated)}")

    return out


def _require_date_range(df: pd.DataFrame, start: object, end: object) -> None:
    start_ts = _as_month_start(start)
    end_ts = _as_month_start(end)
    expected = pd.date_range(start_ts, end_ts, freq="MS")
    missing = expected.difference(df.index)
    if len(missing) > 0:
        missing_text = ", ".join(ts.strftime("%Y-%m-%d") for ts in missing[:5])
        suffix = "..." if len(missing) > 5 else ""
        raise ValueError(
            f"Requested monthly period {start_ts:%Y-%m-%d} to {end_ts:%Y-%m-%d} "
            f"is not fully available. Missing: {missing_text}{suffix}"
        )


def _make_fixed_split(
    df: pd.DataFrame,
    split_name: str,
    train_start: str,
    train_end: str,
    test_start: str,
    test_end: str,
) -> dict:
    data = _with_datetime_index(df)
    _require_date_range(data, train_start, train_end)
    _require_date_range(data, test_start, test_end)

    train_start_ts = _as_month_start(train_start)
    train_end_ts = _as_month_start(train_end)
    test_start_ts = _as_month_start(test_start)
    test_end_ts = _as_month_start(test_end)

    return {
        "split": split_name,
        "train_start": train_start_ts,
        "train_end": train_end_ts,
        "test_start": test_start_ts,
        "test_end": test_end_ts,
        "train": data.loc[train_start_ts:train_end_ts].copy(),
        "test": data.loc[test_start_ts:test_end_ts].copy(),
    }


def make_fixed_split_a(df: pd.DataFrame) -> dict:
    """Build fixed split A: train 2002-04 to 2019-12, test 2020-01 to 2021-12."""
    return _make_fixed_split(
        df=df,
        split_name="fixed_a",
        train_start="2002-04-01",
        train_end="2019-12-01",
        test_start="2020-01-01",
        test_end="2021-12-01",
    )


def make_fixed_split_b(df: pd.DataFrame) -> dict:
    """Build fixed split B: train 2002-04 to 2023-12, test 2024-01 to 2026-02."""
    return _make_fixed_split(
        df=df,
        split_name="fixed_b",
        train_start="2002-04-01",
        train_end="2023-12-01",
        test_start="2024-01-01",
        test_end="2026-02-01",
    )


def make_rolling_splits(
    df: pd.DataFrame,
    start_cutoff: object,
    end_cutoff: object,
    step_months: int,
    horizons: Iterable[int],
) -> list[dict]:
    """Build rolling-origin split records.

    Each record represents one cutoff and one horizon. Training data ends at
    the cutoff month. The test row is the target month at cutoff + horizon.
    """
    if step_months <= 0:
        raise ValueError("step_months must be a positive integer.")

    horizon_values = [int(h) for h in horizons]
    if not horizon_values or any(h <= 0 for h in horizon_values):
        raise ValueError("horizons must contain positive integers.")

    data = _with_datetime_index(df)
    start_cutoff_ts = _as_month_start(start_cutoff)
    end_cutoff_ts = _as_month_start(end_cutoff)

    if start_cutoff_ts > end_cutoff_ts:
        raise ValueError("start_cutoff must be earlier than or equal to end_cutoff.")

    cutoffs = pd.date_range(start_cutoff_ts, end_cutoff_ts, freq=pd.DateOffset(months=step_months))
    split_records: list[dict] = []

    for split_number, cutoff in enumerate(cutoffs, start=1):
        if cutoff not in data.index:
            raise ValueError(f"Cutoff month is not available in data: {cutoff:%Y-%m-%d}")

        train = data.loc[:cutoff].copy()
        if train.empty:
            raise ValueError(f"No training data available through cutoff {cutoff:%Y-%m-%d}.")

        for horizon in horizon_values:
            test_start = cutoff + pd.DateOffset(months=horizon)
            test_end = test_start
            if test_start not in data.index:
                raise ValueError(
                    f"Target month for cutoff {cutoff:%Y-%m-%d}, horizon {horizon} "
                    f"is not available: {test_start:%Y-%m-%d}"
                )

            split_records.append(
                {
                    "split": f"rolling_{split_number:03d}",
                    "cutoff": cutoff,
                    "horizon": horizon,
                    "train_start": train.index.min(),
                    "train_end": cutoff,
                    "test_start": test_start,
                    "test_end": test_end,
                    "train": train,
                    "test": data.loc[[test_start]].copy(),
                }
            )

    return split_records

