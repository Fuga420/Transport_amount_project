"""Prophet fixed-split forecasting helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.forecasting.forecast_utils import make_forecast_frame


def _import_prophet():
    try:
        from prophet import Prophet
    except ImportError as exc:
        raise ImportError(
            "The 'prophet' package is required for Prophet forecasts. "
            "Install it with: python -m pip install prophet"
        ) from exc
    return Prophet


def _with_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.index, pd.DatetimeIndex):
        out = df.copy()
    elif "date" in df.columns:
        out = df.copy()
        out["date"] = pd.to_datetime(out["date"])
        out = out.set_index("date")
    elif "label" in df.columns:
        out = df.copy()
        out["label"] = pd.to_datetime(out["label"])
        out = out.set_index("label")
    else:
        raise ValueError("df must have a DatetimeIndex, 'date' column, or 'label' column.")

    out = out.sort_index()
    out.index = pd.to_datetime(out.index).to_period("M").to_timestamp()
    return out


def prepare_prophet_frame(df: pd.DataFrame, target_col: str = "y") -> pd.DataFrame:
    """Convert a monthly DataFrame to Prophet's ds/y input format."""
    data = _with_datetime_index(df)
    if target_col not in data.columns:
        raise ValueError(f"target_col '{target_col}' does not exist in df.")

    frame = pd.DataFrame(
        {
            "ds": data.index,
            "y": data[target_col].astype(float).to_numpy(),
        }
    )
    return frame


def fit_prophet(
    train_df: pd.DataFrame,
    target_col: str = "y",
    yearly_seasonality: bool | int | str = True,
):
    """Fit Prophet on the log-scale target without holidays or regressors."""
    Prophet = _import_prophet()
    train = prepare_prophet_frame(train_df, target_col=target_col)

    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(train)
    return model


def forecast_prophet(
    model,
    test_df: pd.DataFrame,
    split: str,
    spec_name: str = "prophet_no_regressors",
) -> pd.DataFrame:
    """Forecast Prophet and return the common original-scale forecast frame."""
    test = _with_datetime_index(test_df)
    if "number_parcels" not in test.columns:
        raise ValueError("test_df must contain 'number_parcels'.")

    future = pd.DataFrame({"ds": test.index})
    forecast = model.predict(future)
    y_pred = np.exp(forecast["yhat"].to_numpy(dtype=float))

    history_dates = pd.to_datetime(model.history["ds"])
    cutoff = history_dates.max()

    return make_forecast_frame(
        dates=test.index,
        y_true=test["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model="prophet",
        split=split,
        forecast_type="unconditional",
        spec_name=spec_name,
        target_col="number_parcels",
        target_scale="original",
        cutoff=cutoff,
        horizons=list(range(1, len(test) + 1)),
    )
