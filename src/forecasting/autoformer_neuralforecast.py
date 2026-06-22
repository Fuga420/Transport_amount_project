"""NeuralForecast Autoformer fixed-split forecasting helpers.

This module uses Nixtla's NeuralForecast Autoformer as a library baseline.
It is separate from autoformer_lite, which is a local Autoformer-inspired
baseline rather than a library Autoformer implementation.
"""

from __future__ import annotations

import sys
import time
import types
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.forecasting.evaluation import evaluate_forecasts
from src.features import add_period_dummies
from src.forecasting.forecast_specs import get_forecast_spec
from src.forecasting.forecast_utils import make_forecast_frame


MODEL_NAME = "autoformer_neuralforecast"
SPEC_NAME = "neuralforecast_autoformer_minimal"
GRID_SPEC_NAME = "neuralforecast_autoformer_grid"
EXOG_MODEL_NAME = "autoformer_neuralforecast_exog"
EXOG_SPEC_NAME = "neuralforecast_autoformer_exog_baseline_m4"


def _install_ray_import_stubs() -> bool:
    """Install minimal ray stubs needed by NeuralForecast auto-tuning imports.

    NeuralForecast imports ray for its auto-tuning classes at package import
    time. The fixed-parameter Autoformer path used here does not call ray, but
    Windows + Python 3.13 may not have a compatible ray wheel.
    """
    try:
        import ray

        if getattr(ray, "__AUTOFORMER_NEURALFORECAST_STUB__", False):
            return True

        return False
    except ImportError:
        pass

    module_names = [
        "ray",
        "ray.air",
        "ray.tune",
        "ray.tune.integration",
        "ray.tune.integration.pytorch_lightning",
        "ray.tune.search",
        "ray.tune.search.basic_variant",
        "ray.tune.search.hyperopt",
    ]
    for name in module_names:
        sys.modules.setdefault(name, types.ModuleType(name))

    sys.modules["ray"].__AUTOFORMER_NEURALFORECAST_STUB__ = True
    sys.modules["ray"].air = sys.modules["ray.air"]
    sys.modules["ray"].tune = sys.modules["ray.tune"]

    class TuneReportCallback:
        def __init__(self, *args, **kwargs) -> None:
            pass

    class BasicVariantGenerator:
        def __init__(self, *args, **kwargs) -> None:
            pass

    class HyperOptSearch:
        def __init__(self, *args, **kwargs) -> None:
            pass

    sys.modules["ray.tune.integration.pytorch_lightning"].TuneReportCallback = TuneReportCallback
    sys.modules["ray.tune.search.basic_variant"].BasicVariantGenerator = BasicVariantGenerator
    sys.modules["ray.tune.search.hyperopt"].HyperOptSearch = HyperOptSearch
    return True


def _import_neuralforecast():
    ray_stub_used = _install_ray_import_stubs()
    try:
        import neuralforecast
        import pytorch_lightning
        import torch
        from neuralforecast import NeuralForecast
        from neuralforecast.losses.pytorch import MAE
        from neuralforecast.models import Autoformer
    except ImportError as exc:
        raise ImportError(
            "NeuralForecast Autoformer requires neuralforecast, pytorch-lightning, "
            "torch, and their runtime dependencies in the active environment."
        ) from exc

    versions = {
        "neuralforecast": getattr(neuralforecast, "__version__", "unknown"),
        "pytorch_lightning": getattr(pytorch_lightning, "__version__", "unknown"),
        "torch": getattr(torch, "__version__", "unknown"),
        "ray_stub_used": ray_stub_used,
    }
    return NeuralForecast, Autoformer, MAE, versions


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


def prepare_neuralforecast_frame(
    df: pd.DataFrame,
    target_col: str = "y",
    unique_id: str = "parcel_volume",
) -> pd.DataFrame:
    """Convert a monthly dataframe to NeuralForecast's unique_id/ds/y format."""
    data = _with_datetime_index(df)
    if target_col not in data.columns:
        raise ValueError(f"target_col '{target_col}' does not exist.")

    return pd.DataFrame(
        {
            "unique_id": unique_id,
            "ds": data.index,
            "y": data[target_col].to_numpy(dtype=float),
        }
    )


def prepare_autoformer_exog_from_spec(df: pd.DataFrame, spec_name: str) -> pd.DataFrame:
    """Create baseline exogenous dummy columns from a forecast spec."""
    data = _with_datetime_index(df)
    spec = get_forecast_spec(spec_name)
    periods = spec.get("exog_periods", {})
    if not periods:
        return pd.DataFrame(index=data.index)

    data = add_period_dummies(data, periods)
    return data[list(periods.keys())].astype(float)


def select_nonconstant_exog(
    exog_train: pd.DataFrame,
    exog_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Drop exogenous columns that are constant in the training period."""
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


def prepare_neuralforecast_frame_with_exog(
    df: pd.DataFrame,
    exog: pd.DataFrame,
    target_col: str = "y",
    unique_id: str = "parcel_volume",
    include_y: bool = True,
) -> pd.DataFrame:
    """Convert data and aligned future exogenous variables to NeuralForecast format."""
    data = _with_datetime_index(df)
    exog_data = exog.reindex(data.index).astype(float)
    frame = pd.DataFrame({"unique_id": unique_id, "ds": data.index})
    if include_y:
        if target_col not in data.columns:
            raise ValueError(f"target_col '{target_col}' does not exist.")
        frame["y"] = data[target_col].to_numpy(dtype=float)
    for col in exog_data.columns:
        frame[col] = exog_data[col].to_numpy(dtype=float)
    return frame


@dataclass
class AutoformerNeuralForecastBundle:
    model: object
    config: dict
    versions: dict
    train_seconds: float
    train_index: pd.DatetimeIndex
    used_exog_columns: list[str] | None = None


def fit_autoformer_neuralforecast(
    train: pd.DataFrame,
    target_col: str = "y",
    horizon: int = 26,
    input_size: int = 24,
    hidden_size: int = 16,
    n_head: int = 2,
    encoder_layers: int = 1,
    decoder_layers: int = 1,
    conv_hidden_size: int = 16,
    moving_avg_window: int = 13,
    max_steps: int = 200,
    random_seed: int = 42,
    spec_name: str = SPEC_NAME,
) -> AutoformerNeuralForecastBundle:
    """Fit a fixed-parameter NeuralForecast Autoformer on log-scale y."""
    NeuralForecast, Autoformer, MAE, versions = _import_neuralforecast()
    train_data = _with_datetime_index(train)
    train_nf = prepare_neuralforecast_frame(train_data, target_col=target_col)

    model = Autoformer(
        h=horizon,
        input_size=input_size,
        hidden_size=hidden_size,
        n_head=n_head,
        encoder_layers=encoder_layers,
        decoder_layers=decoder_layers,
        conv_hidden_size=conv_hidden_size,
        MovingAvg_window=moving_avg_window,
        max_steps=max_steps,
        learning_rate=1e-3,
        batch_size=1,
        valid_batch_size=1,
        windows_batch_size=32,
        inference_windows_batch_size=32,
        scaler_type="standard",
        random_seed=random_seed,
        loss=MAE(),
        val_check_steps=10,
        early_stop_patience_steps=3,
        alias=MODEL_NAME,
        accelerator="cpu",
        devices=1,
        enable_checkpointing=False,
        logger=False,
        enable_progress_bar=False,
        enable_model_summary=False,
    )
    nf = NeuralForecast(models=[model], freq="MS")

    start = time.perf_counter()
    nf.fit(df=train_nf, val_size=horizon)
    train_seconds = time.perf_counter() - start

    config = {
        "model": MODEL_NAME,
        "spec_name": spec_name,
        "target_col": target_col,
        "target_scale_training": "log",
        "horizon": horizon,
        "input_size": input_size,
        "hidden_size": hidden_size,
        "n_head": n_head,
        "encoder_layers": encoder_layers,
        "decoder_layers": decoder_layers,
        "conv_hidden_size": conv_hidden_size,
        "moving_avg_window": moving_avg_window,
        "max_steps": max_steps,
        "random_seed": random_seed,
        "forecast_type": "unconditional",
        "information_set": "unconditional",
        "note": "NeuralForecast Autoformer library baseline; fixed B only; no exogenous variables.",
    }

    return AutoformerNeuralForecastBundle(
        model=nf,
        config=config,
        versions=versions,
        train_seconds=float(train_seconds),
        train_index=train_data.index,
        used_exog_columns=None,
    )


def fit_autoformer_neuralforecast_exog(
    train: pd.DataFrame,
    exog_train: pd.DataFrame,
    used_exog_columns: list[str],
    target_col: str = "y",
    horizon: int = 26,
    input_size: int = 24,
    hidden_size: int = 32,
    n_head: int = 2,
    encoder_layers: int = 1,
    decoder_layers: int = 1,
    conv_hidden_size: int = 32,
    moving_avg_window: int = 13,
    max_steps: int = 200,
    random_seed: int = 42,
) -> AutoformerNeuralForecastBundle:
    """Fit NeuralForecast Autoformer with known future exogenous variables."""
    if not used_exog_columns:
        raise ValueError("At least one nonconstant exogenous variable is required.")

    NeuralForecast, Autoformer, MAE, versions = _import_neuralforecast()
    train_data = _with_datetime_index(train)
    train_nf = prepare_neuralforecast_frame_with_exog(
        train_data,
        exog_train[used_exog_columns],
        target_col=target_col,
        include_y=True,
    )

    model = Autoformer(
        h=horizon,
        input_size=input_size,
        futr_exog_list=used_exog_columns,
        hidden_size=hidden_size,
        n_head=n_head,
        encoder_layers=encoder_layers,
        decoder_layers=decoder_layers,
        conv_hidden_size=conv_hidden_size,
        MovingAvg_window=moving_avg_window,
        max_steps=max_steps,
        learning_rate=1e-3,
        batch_size=1,
        valid_batch_size=1,
        windows_batch_size=32,
        inference_windows_batch_size=32,
        scaler_type="standard",
        random_seed=random_seed,
        loss=MAE(),
        val_check_steps=10,
        early_stop_patience_steps=3,
        alias=EXOG_MODEL_NAME,
        accelerator="cpu",
        devices=1,
        enable_checkpointing=False,
        logger=False,
        enable_progress_bar=False,
        enable_model_summary=False,
    )
    nf = NeuralForecast(models=[model], freq="MS")

    start = time.perf_counter()
    nf.fit(df=train_nf, val_size=horizon)
    train_seconds = time.perf_counter() - start

    config = {
        "model": EXOG_MODEL_NAME,
        "spec_name": EXOG_SPEC_NAME,
        "target_col": target_col,
        "target_scale_training": "log",
        "horizon": horizon,
        "input_size": input_size,
        "hidden_size": hidden_size,
        "n_head": n_head,
        "encoder_layers": encoder_layers,
        "decoder_layers": decoder_layers,
        "conv_hidden_size": conv_hidden_size,
        "moving_avg_window": moving_avg_window,
        "max_steps": max_steps,
        "random_seed": random_seed,
        "forecast_type": "conditional",
        "information_set": "conditional_exog_known",
        "used_exog_columns": ",".join(used_exog_columns),
        "note": "NeuralForecast Autoformer with baseline_m4 future exogenous dummies; fixed B only.",
    }

    return AutoformerNeuralForecastBundle(
        model=nf,
        config=config,
        versions=versions,
        train_seconds=float(train_seconds),
        train_index=train_data.index,
        used_exog_columns=list(used_exog_columns),
    )


def forecast_autoformer_neuralforecast(
    model_bundle: AutoformerNeuralForecastBundle,
    test: pd.DataFrame,
    split: str = "fixed_b",
    spec_name: str | None = None,
) -> pd.DataFrame:
    """Forecast fixed B and return the common forecast frame."""
    test_data = _with_datetime_index(test)
    if "number_parcels" not in test_data.columns:
        raise ValueError("test must contain 'number_parcels'.")

    forecast = model_bundle.model.predict()
    if MODEL_NAME not in forecast.columns:
        raise ValueError(f"NeuralForecast output must contain '{MODEL_NAME}'.")

    forecast = forecast.sort_values("ds").reset_index(drop=True)
    y_pred_log = forecast[MODEL_NAME].to_numpy(dtype=float)
    y_pred = np.exp(y_pred_log)

    if len(y_pred) != len(test_data):
        raise ValueError(
            f"Forecast horizon length mismatch: got {len(y_pred)}, expected {len(test_data)}."
        )

    return make_forecast_frame(
        dates=test_data.index,
        y_true=test_data["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model=MODEL_NAME,
        split=split,
        forecast_type="unconditional",
        spec_name=spec_name or model_bundle.config.get("spec_name", SPEC_NAME),
        target_col="number_parcels",
        target_scale="original",
        cutoff=model_bundle.train_index[-1],
        horizons=list(range(1, len(test_data) + 1)),
    )


def forecast_autoformer_neuralforecast_exog(
    model_bundle: AutoformerNeuralForecastBundle,
    test: pd.DataFrame,
    exog_test: pd.DataFrame,
    split: str = "fixed_b",
) -> pd.DataFrame:
    """Conditionally forecast fixed B with known future exogenous variables."""
    test_data = _with_datetime_index(test)
    if "number_parcels" not in test_data.columns:
        raise ValueError("test must contain 'number_parcels'.")

    used_exog_columns = model_bundle.used_exog_columns or []
    if not used_exog_columns:
        raise ValueError("model_bundle must record used_exog_columns.")

    futr_df = prepare_neuralforecast_frame_with_exog(
        test_data,
        exog_test[used_exog_columns],
        target_col="y",
        include_y=False,
    )
    forecast = model_bundle.model.predict(futr_df=futr_df)
    if EXOG_MODEL_NAME not in forecast.columns:
        raise ValueError(f"NeuralForecast output must contain '{EXOG_MODEL_NAME}'.")

    forecast = forecast.sort_values("ds").reset_index(drop=True)
    y_pred_log = forecast[EXOG_MODEL_NAME].to_numpy(dtype=float)
    y_pred = np.exp(y_pred_log)

    if len(y_pred) != len(test_data):
        raise ValueError(
            f"Forecast horizon length mismatch: got {len(y_pred)}, expected {len(test_data)}."
        )

    return make_forecast_frame(
        dates=test_data.index,
        y_true=test_data["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model=EXOG_MODEL_NAME,
        split=split,
        forecast_type="conditional",
        spec_name=EXOG_SPEC_NAME,
        target_col="number_parcels",
        target_scale="original",
        cutoff=model_bundle.train_index[-1],
        horizons=list(range(1, len(test_data) + 1)),
    )


def run_autoformer_neuralforecast_grid_search(
    train: pd.DataFrame,
    test: pd.DataFrame,
    configs: list[dict],
    target_col: str = "y",
    split: str = "fixed_b",
) -> tuple[pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None, AutoformerNeuralForecastBundle | None]:
    """Run a small manual grid search and keep failed configurations."""
    rows: list[dict] = []
    best_forecast: pd.DataFrame | None = None
    best_metrics: pd.DataFrame | None = None
    best_bundle: AutoformerNeuralForecastBundle | None = None

    for config_id, config in enumerate(configs, start=1):
        row = {
            "config_id": config_id,
            "model": MODEL_NAME,
            "split": split,
            "forecast_type": "unconditional",
            "information_set": "unconditional",
            "spec_name": GRID_SPEC_NAME,
            "target_col": target_col,
            "status": "failed",
            "error": "",
        }
        row.update(config)

        try:
            start = time.perf_counter()
            bundle = fit_autoformer_neuralforecast(
                train=train,
                target_col=target_col,
                horizon=len(_with_datetime_index(test)),
                input_size=int(config["input_size"]),
                hidden_size=int(config["hidden_size"]),
                max_steps=int(config["max_steps"]),
                n_head=int(config.get("n_head", 2)),
                encoder_layers=int(config.get("encoder_layers", 1)),
                decoder_layers=int(config.get("decoder_layers", 1)),
                conv_hidden_size=int(config.get("conv_hidden_size", config["hidden_size"])),
                moving_avg_window=int(config.get("moving_avg_window", 13)),
                random_seed=int(config.get("random_seed", 42)),
                spec_name=GRID_SPEC_NAME,
            )
            forecast_df = forecast_autoformer_neuralforecast(
                bundle,
                test,
                split=split,
                spec_name=GRID_SPEC_NAME,
            )
            metrics_df = evaluate_forecasts(
                forecast_df,
                y_train=_with_datetime_index(train)["number_parcels"],
            )
            elapsed = time.perf_counter() - start

            metrics_row = metrics_df.iloc[0].to_dict()
            row.update(
                {
                    "status": "success",
                    "training_time_seconds": bundle.train_seconds,
                    "total_time_seconds": float(elapsed),
                    "rmse": metrics_row.get("rmse"),
                    "mae": metrics_row.get("mae"),
                    "mape": metrics_row.get("mape"),
                    "mase": metrics_row.get("mase"),
                    **{f"version_{key}": value for key, value in bundle.versions.items()},
                }
            )

            if best_metrics is None or float(metrics_row["rmse"]) < float(best_metrics.loc[0, "rmse"]):
                best_forecast = forecast_df
                best_metrics = metrics_df
                best_bundle = bundle
        except Exception as exc:  # noqa: BLE001 - grid search should record failures
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["training_time_seconds"] = np.nan
            row["total_time_seconds"] = np.nan
            row["rmse"] = np.nan
            row["mae"] = np.nan
            row["mape"] = np.nan
            row["mase"] = np.nan

        rows.append(row)

    grid_df = pd.DataFrame(rows)
    return grid_df, best_forecast, best_metrics, best_bundle
