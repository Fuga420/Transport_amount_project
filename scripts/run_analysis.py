"""Reproducible analysis entry point.

This script currently loads the main dataset, creates event dummies,
and writes lightweight reproducibility checks. Full model estimation and
paper-ready reporting will be added in a later phase.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from platform import python_version


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.data_loader import load_transport_data
from src.features import get_default_event_config, prepare_event_data
from src.ssm_models import LocalLinearTrendSeasonalWithMultiFixedExog
from src.paths import (
    FIGURES_DIR,
    INTERMEDIATE_DIR,
    LOGS_DIR,
    MAIN_DATA_PATH,
    OUTPUT_DIR,
    TABLES_DIR,
)


KEY_COLUMNS = [
    "year",
    "month",
    "Transport_tonnage",
    "number_parcels",
    "Number_companies_1",
    "Number_companies_2",
    "y",
]

BASE_PARAM_NAMES = [
    "obs_error",
    "level_noise",
    "slope_noise",
    "seasonal_noise",
]

LOCAL_LEVEL_PARAM_NAMES = [
    "obs_error",
    "trend_error",
    "seasonal_error",
]

COEFF_START_HINTS = {
    "covid_main": -2.0,
    "covid_wave1": -2.0,
    "covid_2021": -3.0,
}

FINAL_MODEL_NAME = "proposed_phase_fixed_exog"

EXOG_PARAM_NAME_OVERRIDES = {
    "hike_dummy": "hike_effect",
}

MODEL_COMPARISON_SPECS = [
    {
        "model_name": "baseline",
        "paper_label": "1. ベースラインモデル",
        "exog_names": [],
        "model_family": "local_level_seasonal",
    },
    {
        "model_name": "simple_event",
        "paper_label": "2. 単純イベントモデル",
        "exog_names": ["hike_dummy", "covid_main"],
        "model_family": "local_level_seasonal",
    },
    {
        "model_name": FINAL_MODEL_NAME,
        "paper_label": "3. 提案モデル",
        "exog_names": ["hike_dummy", "covid_main", "covid_wave1", "covid_2021"],
        "model_family": "local_linear_trend_seasonal",
    },
]


class LocalLevelSeasonalWithFixedExog(sm.tsa.statespace.MLEModel):
    """Notebook-derived local level + seasonal model with fixed exogenous terms."""

    def __init__(self, endog, exog_list, param_names, seasonal_period=12, **kwargs):
        self.k_seasonal = seasonal_period
        k_states = 1 + (self.k_seasonal - 1)
        k_posdef = 2

        self.param_names_custom = param_names
        self.num_exog = len(exog_list)

        super().__init__(
            endog=endog,
            k_states=k_states,
            k_posdef=k_posdef,
            initialization="diffuse",
            **kwargs,
        )

        self.ssm["design"] = np.zeros((1, k_states))
        self.ssm["design", 0, 0] = 1
        self.ssm["design", 0, 1] = 1

        transition = np.zeros((k_states, k_states))
        transition[0, 0] = 1
        transition[1, 1:] = -1
        for i in range(2, k_states):
            transition[i, i - 1] = 1
        self.ssm["transition"] = transition

        selection = np.zeros((k_states, k_posdef))
        selection[0, 0] = 1
        selection[1, 1] = 1
        self.ssm["selection"] = selection

        self.exogs = [ex.values.reshape(1, -1) for ex in exog_list]
        self.ssm["obs_intercept"] = np.zeros((1, len(endog)))

    @property
    def param_names(self):
        return self.param_names_custom

    def transform_params(self, unconstrained):
        constrained = unconstrained.copy()
        constrained[:3] = constrained[:3] ** 2
        return constrained

    def untransform_params(self, constrained):
        unconstrained = constrained.copy()
        unconstrained[:3] = np.sqrt(unconstrained[:3])
        return unconstrained

    def update(self, params, **kwargs):
        params = super().update(params, **kwargs)

        self["obs_cov", 0, 0] = params[0]
        self["state_cov", 0, 0] = params[1]
        self["state_cov", 1, 1] = params[2]

        total_exog_effect = 0
        for i in range(self.num_exog):
            total_exog_effect += params[3 + i] * self.exogs[i]

        self["obs_intercept", 0, :] = total_exog_effect


def ensure_output_dirs() -> None:
    """Create output directories required by the reproducible pipeline."""
    for path in (OUTPUT_DIR, TABLES_DIR, FIGURES_DIR, LOGS_DIR, INTERMEDIATE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def build_data_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build a one-row summary of the loaded analysis dataset."""
    return pd.DataFrame(
        [
            {
                "data_start": df.index.min().strftime("%Y-%m-%d"),
                "data_end": df.index.max().strftime("%Y-%m-%d"),
                "n_rows": len(df),
                "n_columns": len(df.columns),
                "columns": ",".join(df.columns),
                "key_columns_present": ",".join([col for col in KEY_COLUMNS if col in df.columns]),
            }
        ]
    )


def build_event_dummy_summary(df: pd.DataFrame, event_names: list[str]) -> pd.DataFrame:
    """Summarize event dummy columns for quick reproducibility checks."""
    rows = []

    for name in event_names:
        active_index = df.index[df[name] == 1]
        rows.append(
            {
                "event": name,
                "active_months": int(df[name].sum()),
                "first_active_month": (
                    active_index.min().strftime("%Y-%m-%d") if len(active_index) > 0 else ""
                ),
                "last_active_month": (
                    active_index.max().strftime("%Y-%m-%d") if len(active_index) > 0 else ""
                ),
            }
        )

    return pd.DataFrame(rows)


def write_run_metadata(df: pd.DataFrame) -> None:
    """Write lightweight run metadata for reproducibility."""
    metadata = {
        "run_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "input_data_path": str(MAIN_DATA_PATH),
        "data_start": df.index.min().strftime("%Y-%m-%d"),
        "data_end": df.index.max().strftime("%Y-%m-%d"),
        "n_rows": len(df),
        "n_columns": len(df.columns),
        "versions": {
            "python": python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
    }

    metadata_path = LOGS_DIR / "run_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_start_params(exog_names: list[str]) -> list[float]:
    """Build start params matching the notebook's final proposed model setup."""
    init_variances = [0.01, 0.01, 0.001, 0.001]
    init_coeffs = [COEFF_START_HINTS.get(name, 0.0) for name in exog_names]
    return init_variances + init_coeffs


def make_param_names(exog_names: list[str]) -> list[str]:
    """Build parameter names matching paper and notebook naming."""
    exog_param_names = [
        EXOG_PARAM_NAME_OVERRIDES.get(name, f"{name}_effect")
        for name in exog_names
    ]
    return BASE_PARAM_NAMES + exog_param_names


def fit_model(
    df: pd.DataFrame,
    exog_data: list[pd.Series],
    exog_names: list[str],
):
    """Fit one state-space model with the given fixed exogenous variables."""
    param_names = make_param_names(exog_names)

    model = LocalLinearTrendSeasonalWithMultiFixedExog(
        endog=df["y"],
        exog_list=exog_data,
        param_names=param_names,
        seasonal_period=12,
    )

    result = model.fit(
        start_params=build_start_params(exog_names),
        maxiter=1000,
        disp=False,
    )

    return result, param_names


def fit_local_level_model(
    df: pd.DataFrame,
    exog_data: list[pd.Series],
    exog_names: list[str],
):
    """Fit the notebook-derived baseline/simple-event comparison model."""
    exog_param_names = [
        EXOG_PARAM_NAME_OVERRIDES.get(name, f"{name}_effect")
        for name in exog_names
    ]
    param_names = LOCAL_LEVEL_PARAM_NAMES + exog_param_names

    model = LocalLevelSeasonalWithFixedExog(
        endog=df["y"],
        exog_list=exog_data,
        param_names=param_names,
        seasonal_period=12,
    )

    result = model.fit(
        start_params=[0.0, 0.0, 0.5] + [COEFF_START_HINTS.get(name, 0.0) for name in exog_names],
        maxiter=1000,
        disp=False,
    )

    return result, param_names


def fit_final_model(
    df: pd.DataFrame,
    exog_data: list[pd.Series],
    exog_names: list[str],
):
    """Fit the paper's proposed final model only."""
    return fit_model(df, exog_data, exog_names)


def build_final_model_params(result, param_names: list[str]) -> pd.DataFrame:
    """Build a parameter table from a fitted statsmodels result."""
    estimates = np.asarray(result.params, dtype=float)
    std_errors = np.asarray(result.bse, dtype=float)
    z_values = np.asarray(result.zvalues, dtype=float)
    p_values = np.asarray(result.pvalues, dtype=float)

    return pd.DataFrame(
        {
            "parameter": param_names,
            "estimate": estimates,
            "std_error": std_errors,
            "z_value": z_values,
            "p_value": p_values,
        }
    )


def summarize_fit(
    result,
    model_name: str,
    paper_label: str,
    exog_names: list[str],
    model_family: str,
) -> dict:
    """Build one model-comparison row from a successful fit."""
    log_likelihood = float(result.llf)
    aic = float(result.aic)
    bic = float(result.bic)

    return {
        "model_name": model_name,
        "paper_label": paper_label,
        "model_family": model_family,
        "status": "success",
        "error": "",
        "nobs": int(result.nobs),
        "log_likelihood": log_likelihood,
        "aic": aic,
        "bic": bic,
        "log_likelihood_rounded": round(log_likelihood, 1),
        "aic_rounded": round(aic, 1),
        "bic_rounded": round(bic, 1),
        "dependent_variable": "y",
        "exog_variables": ",".join(exog_names),
    }


def summarize_failure(
    model_name: str,
    paper_label: str,
    exog_names: list[str],
    model_family: str,
    error: Exception,
) -> dict:
    """Build one model-comparison row from a failed fit."""
    return {
        "model_name": model_name,
        "paper_label": paper_label,
        "model_family": model_family,
        "status": "failed",
        "error": str(error),
        "nobs": np.nan,
        "log_likelihood": np.nan,
        "aic": np.nan,
        "bic": np.nan,
        "log_likelihood_rounded": np.nan,
        "aic_rounded": np.nan,
        "bic_rounded": np.nan,
        "dependent_variable": "y",
        "exog_variables": ",".join(exog_names),
    }


def build_model_comparison(
    df: pd.DataFrame,
    final_result,
) -> pd.DataFrame:
    """Fit the paper's model-comparison specifications and summarize them."""
    rows = []

    for spec in MODEL_COMPARISON_SPECS:
        model_name = spec["model_name"]
        paper_label = spec["paper_label"]
        exog_names = spec["exog_names"]

        model_family = spec["model_family"]

        if model_name == FINAL_MODEL_NAME:
            rows.append(summarize_fit(final_result, model_name, paper_label, exog_names, model_family))
            continue

        try:
            exog_data = [df[name] for name in exog_names]
            if model_family == "local_level_seasonal":
                result, _param_names = fit_local_level_model(df, exog_data, exog_names)
            else:
                result, _param_names = fit_model(df, exog_data, exog_names)
            rows.append(summarize_fit(result, model_name, paper_label, exog_names, model_family))
        except Exception as exc:
            rows.append(summarize_failure(model_name, paper_label, exog_names, model_family, exc))

    return pd.DataFrame(rows)


def build_final_model_fit_summary(
    result,
    df: pd.DataFrame,
    exog_names: list[str],
) -> pd.DataFrame:
    """Build a one-row fit summary for the paper's final model."""
    return pd.DataFrame(
        [
            {
                "model_name": FINAL_MODEL_NAME,
                "nobs": int(result.nobs),
                "log_likelihood": float(result.llf),
                "aic": float(result.aic),
                "bic": float(result.bic),
                "dependent_variable": "y",
                "exog_variables": ",".join(exog_names),
                "data_start": df.index.min().strftime("%Y-%m-%d"),
                "data_end": df.index.max().strftime("%Y-%m-%d"),
            }
        ]
    )


def main() -> None:
    ensure_output_dirs()

    print("Reproducible analysis scaffold: data loading and feature checks")
    print(f"Input data: {MAIN_DATA_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Tables directory: {TABLES_DIR}")
    print(f"Figures directory: {FIGURES_DIR}")
    print(f"Logs directory: {LOGS_DIR}")
    print(f"Intermediate directory: {INTERMEDIATE_DIR}")

    df = load_transport_data(str(MAIN_DATA_PATH))

    event_config = get_default_event_config()
    df, exog_data, event_names = prepare_event_data(df, event_config)

    data_summary = build_data_summary(df)
    event_dummy_summary = build_event_dummy_summary(df, event_names)

    data_summary.to_csv(TABLES_DIR / "data_summary.csv", index=False)
    event_dummy_summary.to_csv(TABLES_DIR / "event_dummy_summary.csv", index=False)
    write_run_metadata(df)

    print("\nData summary")
    print(f"- Period: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    print(f"- Shape: {len(df)} rows x {len(df.columns)} columns")
    print(f"- Key columns: {', '.join([col for col in KEY_COLUMNS if col in df.columns])}")

    print("\nEvent dummy summary")
    print(event_dummy_summary.to_string(index=False))

    print("\nFinal model")
    print(f"- Model name: {FINAL_MODEL_NAME}")
    print("- State-space class: LocalLinearTrendSeasonalWithMultiFixedExog")
    print("- Dependent variable: y")
    print(f"- Exogenous variables: {', '.join(event_names)}")
    print(f"- Estimation period: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")

    result, param_names = fit_final_model(df, exog_data, event_names)
    final_model_params = build_final_model_params(result, param_names)
    final_model_fit_summary = build_final_model_fit_summary(result, df, event_names)

    final_model_params.to_csv(TABLES_DIR / "final_model_params.csv", index=False)
    final_model_fit_summary.to_csv(TABLES_DIR / "final_model_fit_summary.csv", index=False)

    print("\nFinal model fit summary")
    print(final_model_fit_summary.to_string(index=False))

    print("\nModel comparison")
    model_comparison = build_model_comparison(df, result)
    model_comparison.to_csv(TABLES_DIR / "model_comparison.csv", index=False)
    print(model_comparison.to_string(index=False))

    # TODO: Generate reproducible figures for paper_2.tex.
    # TODO: Save run metadata and diagnostics.


if __name__ == "__main__":
    main()
