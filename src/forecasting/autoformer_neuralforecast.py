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

from src.forecasting.forecast_utils import make_forecast_frame
from src.forecasting.evaluation import evaluate_forecasts


MODEL_NAME = "autoformer_neuralforecast"
SPEC_NAME = "neuralforecast_autoformer_minimal"
GRID_SPEC_NAME = "neuralforecast_autoformer_grid"


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


@dataclass
class AutoformerNeuralForecastBundle:
    model: object
    config: dict
    versions: dict
    train_seconds: float
    train_index: pd.DatetimeIndex


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
