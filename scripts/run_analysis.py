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

COEFF_START_HINTS = {
    "covid_main": -2.0,
    "covid_wave1": -2.0,
    "covid_2021": -3.0,
}

FINAL_MODEL_NAME = "proposed_phase_fixed_exog"

EXOG_PARAM_NAME_OVERRIDES = {
    "hike_dummy": "hike_effect",
}


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


def fit_final_model(
    df: pd.DataFrame,
    exog_data: list[pd.Series],
    exog_names: list[str],
):
    """Fit the paper's proposed final model only."""
    exog_param_names = [
        EXOG_PARAM_NAME_OVERRIDES.get(name, f"{name}_effect")
        for name in exog_names
    ]
    param_names = BASE_PARAM_NAMES + exog_param_names

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

    # TODO: Estimate baseline and simple-event comparison models.
    # TODO: Generate reproducible figures for paper_2.tex.
    # TODO: Save run metadata and diagnostics.


if __name__ == "__main__":
    main()
