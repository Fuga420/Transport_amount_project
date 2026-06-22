"""Prophet fixed-split forecasting helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features import add_period_dummies
from src.forecasting.forecast_specs import get_forecast_spec
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


def prepare_prophet_regressors_from_spec(df: pd.DataFrame, spec_name: str) -> pd.DataFrame:
    """Create Prophet regressor columns from a forecast spec."""
    data = _with_datetime_index(df)
    spec = get_forecast_spec(spec_name)
    periods = spec.get("exog_periods", {})

    if not periods:
        return pd.DataFrame(index=data.index)

    data = add_period_dummies(data, periods)
    return data[list(periods.keys())].astype(float)


def select_nonconstant_regressors(
    regressors_train: pd.DataFrame,
    regressors_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Drop regressors that are constant in the training period."""
    train = regressors_train.copy()
    test = regressors_test.copy()

    if list(train.columns) != list(test.columns):
        test = test.reindex(columns=train.columns)

    keep_cols = [
        col
        for col in train.columns
        if train[col].notna().any() and train[col].nunique(dropna=True) > 1
    ]

    return train[keep_cols].astype(float), test[keep_cols].astype(float), keep_cols


def _prepare_prophet_frame_with_regressors(
    df: pd.DataFrame,
    regressors: pd.DataFrame,
    target_col: str = "y",
) -> pd.DataFrame:
    data = _with_datetime_index(df)
    frame = prepare_prophet_frame(data, target_col=target_col)
    regressor_data = regressors.reindex(data.index).astype(float)

    for col in regressor_data.columns:
        frame[col] = regressor_data[col].to_numpy(dtype=float)

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


def fit_prophet_with_regressors(
    train_df: pd.DataFrame,
    regressors_train: pd.DataFrame,
    target_col: str = "y",
    yearly_seasonality: bool | int | str = True,
):
    """Fit Prophet on the log-scale target with known regressors."""
    Prophet = _import_prophet()
    train = _prepare_prophet_frame_with_regressors(
        train_df,
        regressors_train,
        target_col=target_col,
    )
    regressor_cols = list(regressors_train.columns)

    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=False,
        daily_seasonality=False,
        uncertainty_samples=0,
    )
    for col in regressor_cols:
        model.add_regressor(col)

    model.fit(train)
    model.forecast_regressor_columns = regressor_cols
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


def forecast_prophet_with_regressors(
    model,
    test_df: pd.DataFrame,
    regressors_test: pd.DataFrame,
    split: str,
    spec_name: str = "baseline_m4",
) -> pd.DataFrame:
    """Conditionally forecast Prophet with known test-period regressors."""
    test = _with_datetime_index(test_df)
    if "number_parcels" not in test.columns:
        raise ValueError("test_df must contain 'number_parcels'.")

    regressor_cols = list(getattr(model, "forecast_regressor_columns", list(regressors_test.columns)))
    future = pd.DataFrame({"ds": test.index})
    regressor_data = regressors_test.reindex(test.index).reindex(columns=regressor_cols).astype(float)
    for col in regressor_cols:
        future[col] = regressor_data[col].to_numpy(dtype=float)

    forecast = model.predict(future)
    y_pred = np.exp(forecast["yhat"].to_numpy(dtype=float))

    history_dates = pd.to_datetime(model.history["ds"])
    cutoff = history_dates.max()

    return make_forecast_frame(
        dates=test.index,
        y_true=test["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model="prophet_regressors",
        split=split,
        forecast_type="conditional",
        spec_name=spec_name,
        target_col="number_parcels",
        target_scale="original",
        cutoff=cutoff,
        horizons=list(range(1, len(test) + 1)),
    )
