"""Utilities for forecast output frames."""

from __future__ import annotations

import numpy as np
import pandas as pd


COMMON_FORECAST_COLUMNS = [
    "date",
    "cutoff",
    "horizon",
    "y_true",
    "y_pred",
    "model",
    "split",
    "forecast_type",
    "spec_name",
    "target_col",
    "target_scale",
]


def _month_horizon(dates: pd.Series, cutoff: pd.Timestamp) -> list[int]:
    date_periods = dates.dt.to_period("M")
    cutoff_period = cutoff.to_period("M")
    return [int(period.ordinal - cutoff_period.ordinal) for period in date_periods]


def make_forecast_frame(
    dates: object,
    y_true: object,
    y_pred: object,
    model: str,
    split: str,
    forecast_type: str,
    spec_name: str,
    target_col: str = "number_parcels",
    target_scale: str = "original",
    cutoff: object | None = None,
    horizons: object | None = None,
) -> pd.DataFrame:
    """Create the common forecast output frame."""
    date_series = pd.Series(pd.to_datetime(dates), name="date")
    n_rows = len(date_series)

    true_values = np.asarray(y_true, dtype=float)
    pred_values = np.asarray(y_pred, dtype=float)

    if len(true_values) != n_rows or len(pred_values) != n_rows:
        raise ValueError("dates, y_true, and y_pred must have the same length.")

    cutoff_value = pd.NaT if cutoff is None else pd.Timestamp(cutoff)

    if horizons is None:
        if cutoff is None:
            horizon_values = list(range(1, n_rows + 1))
        else:
            horizon_values = _month_horizon(date_series, cutoff_value)
    else:
        horizon_values = [int(value) for value in horizons]
        if len(horizon_values) != n_rows:
            raise ValueError("horizons must have the same length as dates.")

    frame = pd.DataFrame(
        {
            "date": date_series,
            "cutoff": cutoff_value,
            "horizon": horizon_values,
            "y_true": true_values,
            "y_pred": pred_values,
            "model": model,
            "split": split,
            "forecast_type": forecast_type,
            "spec_name": spec_name,
            "target_col": target_col,
            "target_scale": target_scale,
        }
    )

    return frame[COMMON_FORECAST_COLUMNS]

