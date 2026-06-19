"""Naive baseline forecasting methods."""

from __future__ import annotations

import pandas as pd

from src.forecasting.forecast_utils import make_forecast_frame


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
    return out


def naive_forecast(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str = "number_parcels",
    model: str = "naive",
    split: str = "unknown",
    forecast_type: str = "unconditional",
    spec_name: str = "unknown",
    target_scale: str = "original",
) -> pd.DataFrame:
    """Forecast all test months with the last observed training value."""
    train = _with_datetime_index(train_df)
    test = _with_datetime_index(test_df)

    if target_col not in train.columns or target_col not in test.columns:
        raise ValueError(f"target_col '{target_col}' must exist in train_df and test_df.")
    if train.empty:
        raise ValueError("train_df must not be empty.")

    last_value = float(train[target_col].iloc[-1])
    y_pred = [last_value] * len(test)

    return make_forecast_frame(
        dates=test.index,
        y_true=test[target_col].to_numpy(dtype=float),
        y_pred=y_pred,
        model=model,
        split=split,
        forecast_type=forecast_type,
        spec_name=spec_name,
        target_col=target_col,
        target_scale=target_scale,
        cutoff=train.index.max(),
        horizons=list(range(1, len(test) + 1)),
    )


def seasonal_naive_forecast(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str = "number_parcels",
    seasonality: int = 12,
    model: str = "seasonal_naive",
    split: str = "unknown",
    forecast_type: str = "unconditional",
    spec_name: str = "unknown",
    target_scale: str = "original",
) -> pd.DataFrame:
    """Monthly seasonal naive forecast using recursive generated predictions.

    For horizons beyond 12 months, the required previous-year value may fall
    inside the test period. In that case this function uses the forecast that
    was generated for that month, not the observed test value.
    """
    if seasonality <= 0:
        raise ValueError("seasonality must be a positive integer.")

    train = _with_datetime_index(train_df)
    test = _with_datetime_index(test_df)

    if target_col not in train.columns or target_col not in test.columns:
        raise ValueError(f"target_col '{target_col}' must exist in train_df and test_df.")
    if len(train) < seasonality:
        raise ValueError("train_df must contain at least seasonality observations.")

    history = {date: float(value) for date, value in train[target_col].items()}
    predictions: list[float] = []

    for date in test.index:
        source_date = date - pd.DateOffset(months=seasonality)
        source_date = source_date.to_period("M").to_timestamp()
        if source_date not in history:
            raise ValueError(
                f"Cannot create seasonal naive forecast for {date:%Y-%m-%d}; "
                f"missing source month {source_date:%Y-%m-%d}."
            )

        pred = history[source_date]
        predictions.append(pred)
        history[date] = pred

    return make_forecast_frame(
        dates=test.index,
        y_true=test[target_col].to_numpy(dtype=float),
        y_pred=predictions,
        model=model,
        split=split,
        forecast_type=forecast_type,
        spec_name=spec_name,
        target_col=target_col,
        target_scale=target_scale,
        cutoff=train.index.max(),
        horizons=list(range(1, len(test) + 1)),
    )

