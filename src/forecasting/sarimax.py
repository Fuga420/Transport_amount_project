"""SARIMA/SARIMAX fixed-split forecasting helpers."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.features import add_period_dummies
from src.forecasting.evaluation import mae, mape, mase, rmse
from src.forecasting.forecast_specs import get_forecast_spec
from src.forecasting.forecast_utils import make_forecast_frame


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


def _empty_exog(index: pd.Index) -> pd.DataFrame:
    return pd.DataFrame(index=index)


def prepare_exog_from_spec(df: pd.DataFrame, spec_name: str) -> pd.DataFrame:
    """Create SARIMAX exogenous variables from a forecast spec."""
    data = _with_datetime_index(df)
    spec = get_forecast_spec(spec_name)
    periods = spec.get("exog_periods", {})

    if not periods:
        return _empty_exog(data.index)

    data = add_period_dummies(data, periods)
    return data[list(periods.keys())].astype(float)


def select_nonconstant_exog(
    exog_train: pd.DataFrame,
    exog_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Drop exogenous variables that are constant in the training period."""
    train = exog_train.copy()
    test = exog_test.copy()

    if list(train.columns) != list(test.columns):
        test = test.reindex(columns=train.columns)

    keep_cols = [
        col
        for col in train.columns
        if train[col].notna().any() and train[col].nunique(dropna=True) > 1
    ]

    return train[keep_cols].astype(float), test[keep_cols].astype(float), keep_cols


def fit_sarima(
    train: pd.DataFrame,
    target_col: str = "y",
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal_order: tuple[int, int, int, int] = (1, 1, 1, 12),
):
    """Fit SARIMA on the log-scale target."""
    train_data = _with_datetime_index(train)
    if target_col not in train_data.columns:
        raise ValueError(f"target_col '{target_col}' does not exist in train.")

    model = SARIMAX(
        train_data[target_col].astype(float),
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)


def fit_sarimax(
    train: pd.DataFrame,
    exog_train: pd.DataFrame,
    target_col: str = "y",
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal_order: tuple[int, int, int, int] = (1, 1, 1, 12),
):
    """Fit SARIMAX on the log-scale target with selected exogenous variables."""
    train_data = _with_datetime_index(train)
    if target_col not in train_data.columns:
        raise ValueError(f"target_col '{target_col}' does not exist in train.")

    exog = exog_train.astype(float) if len(exog_train.columns) > 0 else None
    model = SARIMAX(
        train_data[target_col].astype(float),
        exog=exog,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)


def forecast_sarima(
    result,
    test: pd.DataFrame,
    split: str,
    spec_name: str = "none",
) -> pd.DataFrame:
    """Forecast SARIMA and return the common original-scale forecast frame."""
    test_data = _with_datetime_index(test)
    y_pred_log = result.get_forecast(steps=len(test_data)).predicted_mean
    y_pred = np.exp(np.asarray(y_pred_log, dtype=float))

    return make_forecast_frame(
        dates=test_data.index,
        y_true=test_data["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model="sarima",
        split=split,
        forecast_type="unconditional",
        spec_name=spec_name,
        target_col="number_parcels",
        target_scale="original",
        cutoff=result.model.data.dates[-1],
        horizons=list(range(1, len(test_data) + 1)),
    )


def forecast_sarimax(
    result,
    test: pd.DataFrame,
    exog_test: pd.DataFrame,
    split: str,
    spec_name: str = "baseline_m4",
) -> pd.DataFrame:
    """Conditionally forecast SARIMAX with known test-period exogenous variables."""
    test_data = _with_datetime_index(test)
    exog = exog_test.astype(float) if len(exog_test.columns) > 0 else None
    y_pred_log = result.get_forecast(steps=len(test_data), exog=exog).predicted_mean
    y_pred = np.exp(np.asarray(y_pred_log, dtype=float))

    return make_forecast_frame(
        dates=test_data.index,
        y_true=test_data["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model="sarimax",
        split=split,
        forecast_type="conditional",
        spec_name=spec_name,
        target_col="number_parcels",
        target_scale="original",
        cutoff=result.model.data.dates[-1],
        horizons=list(range(1, len(test_data) + 1)),
    )


def _empty_grid_row(
    model: str,
    split: str,
    order: tuple[int, int, int],
    seasonal_order: tuple[int, int, int, int],
    spec_name: str,
    used_exog_columns: list[str] | None = None,
) -> dict:
    return {
        "model": model,
        "split": split,
        "order": str(order),
        "seasonal_order": str(seasonal_order),
        "spec_name": spec_name,
        "used_exog_columns": ",".join(used_exog_columns or []),
        "converged": np.nan,
        "warnflag": np.nan,
        "log_likelihood": np.nan,
        "aic": np.nan,
        "bic": np.nan,
        "rmse": np.nan,
        "mae": np.nan,
        "mape": np.nan,
        "mase": np.nan,
        "status": "started",
        "error": "",
    }


def _add_fit_and_metric_values(row: dict, result, forecast_df: pd.DataFrame, train: pd.DataFrame) -> dict:
    retvals = getattr(result, "mle_retvals", {}) or {}
    row.update(
        {
            "converged": bool(retvals.get("converged", False)),
            "warnflag": retvals.get("warnflag"),
            "log_likelihood": float(result.llf),
            "aic": float(result.aic),
            "bic": float(result.bic),
            "rmse": rmse(forecast_df["y_true"], forecast_df["y_pred"]),
            "mae": mae(forecast_df["y_true"], forecast_df["y_pred"]),
            "mape": mape(forecast_df["y_true"], forecast_df["y_pred"]),
            "mase": mase(forecast_df["y_true"], forecast_df["y_pred"], train["number_parcels"]),
            "status": "success",
        }
    )
    return row


def run_sarima_grid_search(
    train: pd.DataFrame,
    test: pd.DataFrame,
    split: str,
    orders: list[tuple[int, int, int]],
    seasonal_orders: list[tuple[int, int, int, int]],
    target_col: str = "y",
    spec_name: str = "none",
) -> pd.DataFrame:
    """Run a small fixed-grid SARIMA forecast evaluation."""
    rows = []

    for order in orders:
        for seasonal_order in seasonal_orders:
            row = _empty_grid_row("sarima", split, order, seasonal_order, spec_name)
            try:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always", ConvergenceWarning)
                    result = fit_sarima(
                        train,
                        target_col=target_col,
                        order=order,
                        seasonal_order=seasonal_order,
                    )
                forecast_df = forecast_sarima(result, test, split=split, spec_name=spec_name)
                row = _add_fit_and_metric_values(row, result, forecast_df, _with_datetime_index(train))

                convergence_warnings = [
                    warning for warning in caught if issubclass(warning.category, ConvergenceWarning)
                ]
                if convergence_warnings and row["error"] == "":
                    row["error"] = "ConvergenceWarning"

            except Exception as exc:
                row["status"] = "failed"
                row["error"] = str(exc)

            rows.append(row)

    return pd.DataFrame(rows)


def run_sarimax_grid_search(
    train: pd.DataFrame,
    test: pd.DataFrame,
    exog_train: pd.DataFrame,
    exog_test: pd.DataFrame,
    split: str,
    orders: list[tuple[int, int, int]],
    seasonal_orders: list[tuple[int, int, int, int]],
    target_col: str = "y",
    spec_name: str = "baseline_m4",
) -> pd.DataFrame:
    """Run a small fixed-grid conditional SARIMAX forecast evaluation."""
    rows = []
    used_exog_columns = list(exog_train.columns)

    for order in orders:
        for seasonal_order in seasonal_orders:
            row = _empty_grid_row(
                "sarimax",
                split,
                order,
                seasonal_order,
                spec_name,
                used_exog_columns=used_exog_columns,
            )
            try:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always", ConvergenceWarning)
                    result = fit_sarimax(
                        train,
                        exog_train,
                        target_col=target_col,
                        order=order,
                        seasonal_order=seasonal_order,
                    )
                forecast_df = forecast_sarimax(
                    result,
                    test,
                    exog_test,
                    split=split,
                    spec_name=spec_name,
                )
                row = _add_fit_and_metric_values(row, result, forecast_df, _with_datetime_index(train))

                convergence_warnings = [
                    warning for warning in caught if issubclass(warning.category, ConvergenceWarning)
                ]
                if convergence_warnings and row["error"] == "":
                    row["error"] = "ConvergenceWarning"

            except Exception as exc:
                row["status"] = "failed"
                row["error"] = str(exc)

            rows.append(row)

    return pd.DataFrame(rows)
