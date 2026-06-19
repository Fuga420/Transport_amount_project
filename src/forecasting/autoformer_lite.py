"""Autoformer-inspired fixed-split forecasting helpers.

This module implements a lightweight decomposition Transformer baseline. It is
not a full Autoformer implementation.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.forecasting.forecast_utils import make_forecast_frame


def _import_torch():
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError as exc:
        raise ImportError(
            "The 'torch' package is required for autoformer_lite. "
            "Install PyTorch in the active environment before running this model."
        ) from exc
    return torch, nn, DataLoader, TensorDataset


def set_random_seed(seed: int) -> None:
    """Set random seeds for reproducible CPU training."""
    torch, _nn, _DataLoader, _TensorDataset = _import_torch()
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


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


def moving_average_decompose(series: object, kernel_size: int = 12) -> tuple[np.ndarray, np.ndarray]:
    """Split a series into trailing moving-average trend and residual parts."""
    values = np.asarray(series, dtype=float)
    if values.ndim != 1:
        raise ValueError("series must be one-dimensional.")
    if kernel_size <= 0:
        raise ValueError("kernel_size must be a positive integer.")

    trend = (
        pd.Series(values)
        .rolling(window=kernel_size, min_periods=1)
        .mean()
        .to_numpy(dtype=float)
    )
    residual = values - trend
    return trend, residual


def make_supervised_windows(series: object, lookback: int = 24) -> tuple[np.ndarray, np.ndarray]:
    """Create one-step-ahead supervised windows from a univariate series."""
    values = np.asarray(series, dtype=float)
    if values.ndim != 1:
        raise ValueError("series must be one-dimensional.")
    if lookback <= 0:
        raise ValueError("lookback must be a positive integer.")
    if len(values) <= lookback:
        raise ValueError("series length must be greater than lookback.")

    x_values = []
    y_values = []
    for end in range(lookback, len(values)):
        window = values[end - lookback : end]
        trend, residual = moving_average_decompose(window, kernel_size=min(12, lookback))
        x_values.append(np.column_stack([trend, residual]))
        y_values.append(values[end])

    return np.asarray(x_values, dtype=np.float32), np.asarray(y_values, dtype=np.float32)


class _AutoformerLiteNet:
    """Small decomposition Transformer encoder for one-step forecasting."""

    def __new__(cls, *args, **kwargs):
        _torch, nn, _DataLoader, _TensorDataset = _import_torch()

        class AutoformerLiteNet(nn.Module):
            def __init__(
                self,
                lookback: int,
                input_dim: int = 2,
                hidden_size: int = 32,
                n_heads: int = 2,
                n_layers: int = 1,
                dropout: float = 0.1,
            ) -> None:
                super().__init__()
                self.input_projection = nn.Linear(input_dim, hidden_size)
                self.position_embedding = nn.Parameter(_torch.zeros(1, lookback, hidden_size))
                encoder_layer = nn.TransformerEncoderLayer(
                    d_model=hidden_size,
                    nhead=n_heads,
                    dim_feedforward=hidden_size * 2,
                    dropout=dropout,
                    batch_first=True,
                    activation="gelu",
                )
                self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
                self.head = nn.Sequential(
                    nn.LayerNorm(hidden_size),
                    nn.Linear(hidden_size, hidden_size),
                    nn.GELU(),
                    nn.Linear(hidden_size, 1),
                )

            def forward(self, x):
                hidden = self.input_projection(x) + self.position_embedding[:, : x.shape[1], :]
                encoded = self.encoder(hidden)
                return self.head(encoded[:, -1, :]).squeeze(-1)

        return AutoformerLiteNet(*args, **kwargs)


@dataclass
class AutoformerLiteBundle:
    model: object
    lookback: int
    mean: float
    std: float
    train_values_scaled: np.ndarray
    train_index: pd.DatetimeIndex
    train_history: pd.DataFrame
    config: dict


def fit_autoformer_lite(
    train: pd.DataFrame,
    target_col: str = "y",
    lookback: int = 24,
    max_epochs: int = 100,
    random_seed: int = 42,
    hidden_size: int = 32,
    n_heads: int = 2,
    n_layers: int = 1,
    batch_size: int = 32,
    learning_rate: float = 1e-3,
    patience: int = 10,
) -> AutoformerLiteBundle:
    """Fit autoformer_lite on the log-scale target."""
    torch, nn, DataLoader, TensorDataset = _import_torch()
    set_random_seed(random_seed)

    train_data = _with_datetime_index(train)
    if target_col not in train_data.columns:
        raise ValueError(f"target_col '{target_col}' does not exist in train.")

    values = train_data[target_col].to_numpy(dtype=float)
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=0))
    if not np.isfinite(std) or std == 0:
        raise ValueError("Training target standard deviation is zero or non-finite.")

    scaled = (values - mean) / std
    x_all, y_all = make_supervised_windows(scaled, lookback=lookback)
    if len(x_all) < 24:
        raise ValueError("Not enough supervised windows for training and validation.")

    val_size = min(24, max(8, len(x_all) // 5))
    train_x, val_x = x_all[:-val_size], x_all[-val_size:]
    train_y, val_y = y_all[:-val_size], y_all[-val_size:]

    train_dataset = TensorDataset(
        torch.tensor(train_x, dtype=torch.float32),
        torch.tensor(train_y, dtype=torch.float32),
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_x_tensor = torch.tensor(val_x, dtype=torch.float32)
    val_y_tensor = torch.tensor(val_y, dtype=torch.float32)

    model = _AutoformerLiteNet(
        lookback=lookback,
        hidden_size=hidden_size,
        n_heads=n_heads,
        n_layers=n_layers,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    loss_fn = nn.MSELoss()

    best_state = None
    best_val_loss = float("inf")
    best_epoch = 0
    epochs_without_improvement = 0
    history_rows = []

    for epoch in range(1, max_epochs + 1):
        model.train()
        train_losses = []
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            pred = model(batch_x)
            loss = loss_fn(pred, batch_y)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_losses.append(float(loss.item()))

        model.eval()
        with torch.no_grad():
            val_pred = model(val_x_tensor)
            val_loss = float(loss_fn(val_pred, val_y_tensor).item())

        train_loss = float(np.mean(train_losses)) if train_losses else float("nan")
        history_rows.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})

        if val_loss < best_val_loss - 1e-6:
            best_val_loss = val_loss
            best_epoch = epoch
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= patience:
            break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    train_history = pd.DataFrame(history_rows)
    config = {
        "target_col": target_col,
        "lookback": lookback,
        "max_epochs": max_epochs,
        "epochs_run": int(len(train_history)),
        "best_epoch": int(best_epoch),
        "best_val_loss": float(best_val_loss),
        "random_seed": random_seed,
        "hidden_size": hidden_size,
        "n_heads": n_heads,
        "n_layers": n_layers,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "patience": patience,
        "model_note": "Autoformer-inspired decomposition Transformer baseline; not a full Autoformer implementation.",
    }

    return AutoformerLiteBundle(
        model=model,
        lookback=lookback,
        mean=mean,
        std=std,
        train_values_scaled=scaled.astype(float),
        train_index=train_data.index,
        train_history=train_history,
        config=config,
    )


def _predict_next_scaled(bundle: AutoformerLiteBundle, history_scaled: list[float]) -> float:
    torch, _nn, _DataLoader, _TensorDataset = _import_torch()
    window = np.asarray(history_scaled[-bundle.lookback :], dtype=float)
    trend, residual = moving_average_decompose(window, kernel_size=min(12, bundle.lookback))
    x = np.column_stack([trend, residual]).astype(np.float32)
    x_tensor = torch.tensor(x[None, :, :], dtype=torch.float32)

    bundle.model.eval()
    with torch.no_grad():
        pred = bundle.model(x_tensor).detach().cpu().numpy().reshape(-1)[0]
    return float(pred)


def forecast_autoformer_lite(
    model_bundle: AutoformerLiteBundle,
    test: pd.DataFrame,
    split: str = "fixed_b",
) -> pd.DataFrame:
    """Recursively forecast autoformer_lite and return the common forecast frame."""
    test_data = _with_datetime_index(test)
    if "number_parcels" not in test_data.columns:
        raise ValueError("test must contain 'number_parcels'.")

    history_scaled = list(np.asarray(model_bundle.train_values_scaled, dtype=float))
    pred_log_values = []

    for _ in range(len(test_data)):
        pred_scaled = _predict_next_scaled(model_bundle, history_scaled)
        history_scaled.append(pred_scaled)
        pred_log_values.append(pred_scaled * model_bundle.std + model_bundle.mean)

    y_pred = np.exp(np.asarray(pred_log_values, dtype=float))

    return make_forecast_frame(
        dates=test_data.index,
        y_true=test_data["number_parcels"].to_numpy(dtype=float),
        y_pred=y_pred,
        model="autoformer_lite",
        split=split,
        forecast_type="unconditional",
        spec_name="autoformer_lite_univariate",
        target_col="number_parcels",
        target_scale="original",
        cutoff=model_bundle.train_index[-1],
        horizons=list(range(1, len(test_data) + 1)),
    )
