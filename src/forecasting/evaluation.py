"""Forecast evaluation metrics and grouped evaluation."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_GROUP_COLS = ["model", "split", "forecast_type", "spec_name"]


def _clean_pair(y_true: object, y_pred: object) -> tuple[np.ndarray, np.ndarray]:
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(true) & np.isfinite(pred)
    return true[mask], pred[mask]


def rmse(y_true: object, y_pred: object) -> float:
    """Root mean squared error."""
    true, pred = _clean_pair(y_true, y_pred)
    if len(true) == 0:
        return float("nan")
    return float(np.sqrt(np.mean((true - pred) ** 2)))


def mae(y_true: object, y_pred: object) -> float:
    """Mean absolute error."""
    true, pred = _clean_pair(y_true, y_pred)
    if len(true) == 0:
        return float("nan")
    return float(np.mean(np.abs(true - pred)))


def mape(y_true: object, y_pred: object) -> float:
    """Mean absolute percentage error.

    Observations with zero actual values are excluded. Returns NaN if no
    usable denominator remains.
    """
    true, pred = _clean_pair(y_true, y_pred)
    mask = true != 0
    if not np.any(mask):
        return float("nan")
    return float(np.mean(np.abs((true[mask] - pred[mask]) / true[mask])) * 100)


def mase(y_true: object, y_pred: object, y_train: object, seasonality: int = 12) -> float:
    """Mean absolute scaled error using seasonal naive training error."""
    if seasonality <= 0:
        raise ValueError("seasonality must be a positive integer.")

    true, pred = _clean_pair(y_true, y_pred)
    train = np.asarray(y_train, dtype=float)
    train = train[np.isfinite(train)]

    if len(true) == 0 or len(train) <= seasonality:
        return float("nan")

    scale_errors = np.abs(train[seasonality:] - train[:-seasonality])
    if len(scale_errors) == 0:
        return float("nan")

    denominator = float(np.mean(scale_errors))
    if denominator == 0 or not np.isfinite(denominator):
        return float("nan")

    return float(np.mean(np.abs(true - pred)) / denominator)


def evaluate_forecasts(
    forecast_df: pd.DataFrame,
    y_train: object | None = None,
    group_cols: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Evaluate forecasts by group.

    By default, groups are model, split, forecast_type, and spec_name. Extra
    grouping columns such as cutoff or horizon can be passed through
    ``group_cols``.
    """
    required = {"y_true", "y_pred"}
    missing = required.difference(forecast_df.columns)
    if missing:
        raise ValueError(f"forecast_df is missing required columns: {sorted(missing)}")

    if group_cols is None:
        group_cols = DEFAULT_GROUP_COLS

    group_cols = [col for col in group_cols if col in forecast_df.columns]
    if not group_cols:
        grouped = [((), forecast_df)]
    else:
        grouped = forecast_df.groupby(group_cols, dropna=False)

    rows = []
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)

        row = {col: value for col, value in zip(group_cols, keys)}
        row.update(
            {
                "n": int(len(group)),
                "rmse": rmse(group["y_true"], group["y_pred"]),
                "mae": mae(group["y_true"], group["y_pred"]),
                "mape": mape(group["y_true"], group["y_pred"]),
                "mase": (
                    mase(group["y_true"], group["y_pred"], y_train)
                    if y_train is not None
                    else float("nan")
                ),
            }
        )
        rows.append(row)

    return pd.DataFrame(rows)

