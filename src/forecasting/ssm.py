"""State-space model fixed-split forecasting helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features import add_period_dummies
from src.forecasting.forecast_specs import get_forecast_spec
from src.forecasting.forecast_utils import make_forecast_frame
from src.ssm_models import LocalLinearTrendSeasonalWithMultiFixedExog


BASE_PARAM_NAMES = [
    "obs_error",
    "level_noise",
    "slope_noise",
    "seasonal_noise",
]

COEFF_START_HINTS = {
    "covid_main": -2.0,
    "covid_wave1": -2.0,
    "covid_2021": -3.0,
}

EXOG_PARAM_NAME_OVERRIDES = {
    "hike_dummy": "hike_effect",
}


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


def _make_param_names(exog_names: list[str]) -> list[str]:
    exog_param_names = [
        EXOG_PARAM_NAME_OVERRIDES.get(name, f"{name}_effect")
        for name in exog_names
    ]
    return BASE_PARAM_NAMES + exog_param_names


def _build_start_params(exog_names: list[str]) -> list[float]:
    init_variances = [0.01, 0.01, 0.001, 0.001]
    init_coeffs = [COEFF_START_HINTS.get(name, 0.0) for name in exog_names]
    return init_variances + init_coeffs


def prepare_ssm_exog_from_spec(df: pd.DataFrame, spec_name: str) -> pd.DataFrame:
    """Create SSM exogenous variables from a forecast spec."""
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


def fit_ssm(
    train: pd.DataFrame,
    exog_train: pd.DataFrame,
    target_col: str = "y",
):
    """Fit the local-linear-trend seasonal SSM on the log-scale target."""
    train_data = _with_datetime_index(train)
    if target_col not in train_data.columns:
        raise ValueError(f"target_col '{target_col}' does not exist in train.")

    exog = exog_train.reindex(train_data.index).astype(float)
    exog_names = list(exog.columns)
    param_names = _make_param_names(exog_names)

    model = LocalLinearTrendSeasonalWithMultiFixedExog(
        endog=train_data[target_col].astype(float),
        exog_list=[exog[name] for name in exog_names],
        param_names=param_names,
        seasonal_period=12,
    )
    result = model.fit(
        start_params=_build_start_params(exog_names),
        maxiter=1000,
        disp=False,
    )
    result.forecast_param_names = param_names
    result.forecast_exog_names = exog_names
    result.forecast_target_col = target_col
    return result


def forecast_ssm(
    result,
    test: pd.DataFrame,
    exog_test: pd.DataFrame,
    split: str,
    spec_name: str = "baseline_m4",
) -> pd.DataFrame:
    """Conditionally forecast SSM with known test-period exogenous variables."""
    test_data = _with_datetime_index(test)
    train_endog = pd.Series(result.model.endog[:, 0], index=result.model.data.row_labels)
    train_endog.index = pd.to_datetime(train_endog.index).to_period("M").to_timestamp()

    exog_names = list(getattr(result, "forecast_exog_names", list(exog_test.columns)))
    train_exog_arrays = getattr(result.model, "exogs", [])
    train_exog = pd.DataFrame(
        {
            name: np.asarray(values, dtype=float).reshape(-1)
            for name, values in zip(exog_names, train_exog_arrays)
        },
        index=train_endog.index,
    )

    exog_future = exog_test.reindex(test_data.index).reindex(columns=exog_names).astype(float)
    combined_exog = pd.concat([train_exog, exog_future], axis=0)
    combined_endog = pd.concat(
        [
            train_endog,
            pd.Series(np.nan, index=test_data.index, name=train_endog.name),
        ],
        axis=0,
    )

    param_names = list(getattr(result, "forecast_param_names", _make_param_names(exog_names)))
    forecast_model = LocalLinearTrendSeasonalWithMultiFixedExog(
        endog=combined_endog.astype(float),
        exog_list=[combined_exog[name] for name in exog_names],
        param_names=param_names,
        seasonal_period=12,
    )
    forecast_result = forecast_model.smooth(result.params)
    y_pred_log = forecast_result.predict(start=len(train_endog), end=len(combined_endog) - 1)
    y_pred = np.exp(np.asarray(y_pred_log, dtype=float))

    return make_forecast_frame(
        dates=test_data.index,
        y_true=test_data["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model="ssm",
        split=split,
        forecast_type="conditional",
        spec_name=spec_name,
        target_col="number_parcels",
        target_scale="original",
        cutoff=train_endog.index[-1],
        horizons=list(range(1, len(test_data) + 1)),
    )
