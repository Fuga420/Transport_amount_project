"""Experimental COVID case-count exogenous-variable analysis.

This script reuses the existing parcel-volume loader and state-space model
without changing ``src/``.  It joins the preprocessing output for COVID-19
case counts to the connected parcel series and estimates four fixed-exog
specifications.  All new outputs are written below ``output/covid_cases_exog``.
"""

from __future__ import annotations

import itertools
import subprocess
import sys
import warnings
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import statsmodels
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from src.data_loader import load_connected_parcel_data
from src.paths import PROCESSED_DATA_DIR
from src.ssm_models import LocalLinearTrendSeasonalWithMultiFixedExog


OUTPUT_ROOT = PROJECT_ROOT / "output" / "covid_cases_exog"
METRICS_DIR = OUTPUT_ROOT / "metrics"
LOG_PATH = OUTPUT_ROOT / "logs" / "run_log.md"
PARCEL_DATA_PATH = PROCESSED_DATA_DIR / "parcel_volume_connected.csv"
COVID_MONTHLY_PATH = (
    PROJECT_ROOT / "data" / "experimental" / "covid_cases" / "processed" / "monthly_cases.csv"
)

COVID_START = pd.Timestamp("2020-03-01")
COVID_END = pd.Timestamp("2023-05-01")

BASE_PARAM_NAMES = ["obs_error", "level_noise", "slope_noise", "seasonal_noise"]
PARAM_NAME_OVERRIDES = {"hike_dummy": "hike_effect"}
START_HINTS = {
    "hike_dummy": 0.0,
    "covid_main": -2.0,
    "covid_wave1": -2.0,
    "covid_2021": -3.0,
    "post_stat_change": 0.0,
    "log1p_cases_lag0": 0.0,
    "log1p_cases_lag1": 0.0,
}

SPECIFICATIONS: list[tuple[str, str, list[str]]] = [
    (
        "current_five_event",
        "現行5変数モデル",
        ["hike_dummy", "covid_main", "covid_wave1", "covid_2021", "post_stat_change"],
    ),
    (
        "covid_main_log1p_lag1",
        "COVID期ダミー＋感染者数ラグ1＋統計接続ダミー",
        ["covid_main", "log1p_cases_lag1", "post_stat_change"],
    ),
    (
        "covid_main_log1p_lag0",
        "COVID期ダミー＋感染者数ラグ0＋統計接続ダミー",
        ["covid_main", "log1p_cases_lag0", "post_stat_change"],
    ),
    (
        "log1p_lag1_only",
        "感染者数ラグ1＋統計接続ダミー",
        ["log1p_cases_lag1", "post_stat_change"],
    ),
]


def ensure_output_dirs() -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def period_dummy(index: pd.DatetimeIndex, start: str, end: str | None) -> pd.Series:
    values = index >= pd.Timestamp(start)
    if end is not None:
        values &= index <= pd.Timestamp(end)
    return pd.Series(values.astype(float), index=index)


def build_analysis_data() -> tuple[pd.DataFrame, dict[str, object]]:
    """Join parcel data and preprocessing output, enforcing the COVID window."""
    if not PARCEL_DATA_PATH.exists():
        raise FileNotFoundError(PARCEL_DATA_PATH)
    if not COVID_MONTHLY_PATH.exists():
        raise FileNotFoundError(COVID_MONTHLY_PATH)

    parcel = load_connected_parcel_data(str(PARCEL_DATA_PATH))
    covid = pd.read_csv(COVID_MONTHLY_PATH, encoding="utf-8-sig")
    required = {"month", "monthly_cases_all", "log1p_cases_lag0", "log1p_cases_lag1"}
    missing = required.difference(covid.columns)
    if missing:
        raise ValueError(f"monthly_cases.csvに必要な列がありません: {sorted(missing)}")

    covid["date"] = pd.to_datetime(covid["month"].astype(str) + "-01", format="%Y-%m-%d")
    covid = covid.set_index("date").sort_index()
    covid["covid_period"] = (covid.index >= COVID_START) & (covid.index <= COVID_END)

    # Re-enforce the agreed analysis window even if the preprocessing file is
    # later extended.  Outside the window, all infection-count regressors are 0.
    for column in ("monthly_cases_all", "log1p_cases_lag0", "log1p_cases_lag1"):
        covid[column] = pd.to_numeric(covid[column], errors="raise")
        covid[column] = covid[column].where(covid["covid_period"], 0.0)

    merged = parcel.join(
        covid[["monthly_cases_all", "log1p_cases_lag0", "log1p_cases_lag1", "covid_period"]],
        how="left",
    )
    merged["covid_period"] = merged["covid_period"].astype("boolean").fillna(False).astype(bool)
    for column in ("monthly_cases_all", "log1p_cases_lag0", "log1p_cases_lag1"):
        merged[column] = merged[column].fillna(0.0)

    merged["hike_dummy"] = period_dummy(merged.index, "2017-10-01", "2019-12-01")
    merged["covid_main"] = period_dummy(merged.index, "2020-03-01", "2023-05-01")
    merged["covid_wave1"] = period_dummy(merged.index, "2020-04-01", "2020-05-01")
    merged["covid_2021"] = period_dummy(merged.index, "2021-01-01", "2021-09-01")
    merged["post_stat_change"] = pd.to_numeric(merged["post_stat_change"], errors="raise")

    metadata = {
        "parcel_start": parcel.index.min(),
        "parcel_end": parcel.index.max(),
        "nobs": len(merged),
        "covid_monthly_rows": len(covid),
        "covid_monthly_start": covid.index.min(),
        "covid_monthly_end": covid.index.max(),
        "covid_active_months_in_join": int(merged["covid_period"].sum()),
        "covid_start": COVID_START,
        "covid_end": COVID_END,
    }
    return merged, metadata


def param_names(exog_names: list[str]) -> list[str]:
    return BASE_PARAM_NAMES + [
        PARAM_NAME_OVERRIDES.get(name, f"{name}_effect") for name in exog_names
    ]


def start_params(exog_names: list[str]) -> list[float]:
    return [0.01, 0.01, 0.001, 0.001] + [START_HINTS.get(name, 0.0) for name in exog_names]


def effect_percent(beta: float) -> float:
    return float(100.0 * np.expm1(beta)) if np.isfinite(beta) else np.nan


def design_diagnostics(exog: pd.DataFrame) -> dict[str, object]:
    matrix = exog.to_numpy(dtype=float)
    try:
        condition_number = float(np.linalg.cond(matrix))
    except np.linalg.LinAlgError:
        condition_number = np.inf

    diagnostics: dict[str, object] = {
        "design_n_rows": int(matrix.shape[0]),
        "design_n_columns": int(matrix.shape[1]),
        "design_rank": int(np.linalg.matrix_rank(matrix)),
        "design_condition_number": condition_number,
    }
    for left, right in itertools.combinations(exog.columns, 2):
        diagnostics[f"corr_{left}_{right}"] = float(exog[left].corr(exog[right]))
    return diagnostics


def empty_comparison_row(model_id: str, label: str, exog_names: list[str], df: pd.DataFrame) -> dict[str, object]:
    exog = df[exog_names]
    row: dict[str, object] = {
        "model_id": model_id,
        "model_label": label,
        "exog_columns": ",".join(exog_names),
        "status": "started",
        "error": "",
        "nobs": int(len(df)),
        "data_start": df.index.min().strftime("%Y-%m-%d"),
        "data_end": df.index.max().strftime("%Y-%m-%d"),
        "covid_start": COVID_START.strftime("%Y-%m-%d"),
        "covid_end": COVID_END.strftime("%Y-%m-%d"),
        **design_diagnostics(exog),
    }
    return row


def fit_one(df: pd.DataFrame, model_id: str, label: str, exog_names: list[str]) -> tuple[dict[str, object], list[dict[str, object]]]:
    exog = df[exog_names].astype(float)
    names_full = param_names(exog_names)
    row = empty_comparison_row(model_id, label, exog_names, df)
    coefficient_rows: list[dict[str, object]] = []

    try:
        model = LocalLinearTrendSeasonalWithMultiFixedExog(
            endog=df["y"],
            exog_list=[exog[name] for name in exog_names],
            param_names=names_full,
            seasonal_period=12,
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = model.fit(start_params=start_params(exog_names), maxiter=1000, disp=False)

        convergence_warnings = [w for w in caught if issubclass(w.category, ConvergenceWarning)]
        retvals = getattr(result, "mle_retvals", {}) or {}
        params = np.asarray(result.params, dtype=float)
        standard_errors = np.asarray(result.bse, dtype=float)
        zvalues = np.asarray(result.zvalues, dtype=float)
        pvalues = np.asarray(result.pvalues, dtype=float)
        estimates = dict(zip(names_full, params))
        errors = dict(zip(names_full, standard_errors))

        smoothed = np.asarray(result.smoother_results.smoothed_state, dtype=float)
        trend = smoothed[0]
        seasonal = smoothed[2]
        event_effect = np.zeros(len(df), dtype=float)
        for name in exog_names:
            parameter = PARAM_NAME_OVERRIDES.get(name, f"{name}_effect")
            event_effect += estimates[parameter] * exog[name].to_numpy(dtype=float)
        fitted = trend + seasonal + event_effect
        residual = df["y"].to_numpy(dtype=float) - fitted
        lb = acorr_ljungbox(residual, lags=[12, 24], return_df=True)

        row.update(
            {
                "status": "success",
                "converged": retvals.get("converged"),
                "warnflag": retvals.get("warnflag"),
                "convergence_warning": bool(convergence_warnings),
                "optimizer_iterations": retvals.get("iterations"),
                "log_likelihood": float(result.llf),
                "aic": float(result.aic),
                "bic": float(result.bic),
                "residual_std": float(np.std(residual, ddof=1)),
                "residual_rmse": float(np.sqrt(np.mean(residual**2))),
                "ljung_box_p_value_lag12": float(lb["lb_pvalue"].iloc[0]),
                "ljung_box_p_value_lag24": float(lb["lb_pvalue"].iloc[1]),
                "warning_messages": " | ".join(str(w.message) for w in caught),
            }
        )

        for i, parameter in enumerate(names_full):
            is_event = parameter.endswith("_effect") or parameter == "hike_effect"
            coefficient_rows.append(
                {
                    "model_id": model_id,
                    "model_label": label,
                    "parameter": parameter,
                    "parameter_group": "event" if is_event else "variance",
                    "estimate": params[i],
                    "std_error": standard_errors[i],
                    "z_value": zvalues[i],
                    "p_value": pvalues[i],
                    "percent_conversion": effect_percent(params[i]) if is_event else np.nan,
                }
            )
    except Exception as exc:  # retain a row so failed specifications are explicit
        row.update(
            {
                "status": "failed",
                "converged": False,
                "warnflag": np.nan,
                "convergence_warning": False,
                "error": repr(exc),
            }
        )
    return row, coefficient_rows


def write_log(comparisons: pd.DataFrame, metadata: dict[str, object]) -> None:
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip() or "(clean)"
    success = comparisons[comparisons["status"] == "success"]
    converged = success[success["converged"] == True]
    lines = [
        "# 感染者数外生変数モデル 実行ログ",
        "",
        f"- 実行ブランチ: {branch}",
        f"- 宅配便入力: `{PARCEL_DATA_PATH.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- 感染者数入力: `{COVID_MONTHLY_PATH.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- 宅配便分析期間: {metadata['parcel_start']:%Y-%m}--{metadata['parcel_end']:%Y-%m}（{metadata['nobs']}か月）",
        f"- 感染者数月次入力: {metadata['covid_monthly_start']:%Y-%m}--{metadata['covid_monthly_end']:%Y-%m}（{metadata['covid_monthly_rows']}行）",
        f"- COVID外生変数対象期間: {COVID_START:%Y-%m}--{COVID_END:%Y-%m}（結合後の対象月数{metadata['covid_active_months_in_join']}）",
        "- 対象期間外の感染者数外生変数は0とした。",
        "- log1p_cases_lag1を主仕様候補、lag0を感度確認として定義した。",
        "- 既存のsrc、output/sensitivity、output/forecasts、paper_jsceは変更していない。",
        "",
        "## 推定仕様",
        "",
        "- 現行5変数モデル: hike_dummy, covid_main, covid_wave1, covid_2021, post_stat_change",
        "- COVID期ダミー＋感染者数ラグ1＋統計接続ダミー",
        "- COVID期ダミー＋感染者数ラグ0＋統計接続ダミー",
        "- 感染者数ラグ1＋統計接続ダミー",
        "- すべて既存のlocal linear trend＋12か月季節状態モデルを用い、感染者数係数を固定係数として推定した。",
        "",
        "## 結果概要",
        "",
        f"- 推定成功: {len(success)}/{len(comparisons)}、収束判定True: {len(converged)}/{len(comparisons)}",
        "- 係数は指定された外生変数に対応するモデル上の水準差であり、感染者数係数を因果効果として解釈しない。",
        "- AIC/BIC、残差診断、設計行列の相関・条件数を併せて確認し、単一指標だけで仕様を選択しない。",
        "",
        "## 生成ファイル",
        "",
        "- metrics/model_comparison.csv",
        "- metrics/coefficients.csv",
        "- metrics/design_diagnostics.csv",
        "- logs/run_log.md",
        "",
        "## 実行時のgit status --short",
        "",
        "```text",
        status,
        "```",
    ]
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_output_dirs()
    df, metadata = build_analysis_data()
    comparison_rows: list[dict[str, object]] = []
    coefficient_rows: list[dict[str, object]] = []
    design_rows: list[dict[str, object]] = []

    for model_id, label, exog_names in SPECIFICATIONS:
        comparison, coefficients = fit_one(df, model_id, label, exog_names)
        comparison_rows.append(comparison)
        coefficient_rows.extend(coefficients)
        design_rows.append(
            {
                "model_id": model_id,
                "model_label": label,
                "exog_columns": ",".join(exog_names),
                **design_diagnostics(df[exog_names].astype(float)),
            }
        )

    comparisons = pd.DataFrame(comparison_rows)
    coefficients = pd.DataFrame(coefficient_rows)
    designs = pd.DataFrame(design_rows)
    comparisons.to_csv(METRICS_DIR / "model_comparison.csv", index=False)
    coefficients.to_csv(METRICS_DIR / "coefficients.csv", index=False)
    designs.to_csv(METRICS_DIR / "design_diagnostics.csv", index=False)
    write_log(comparisons, metadata)

    display_columns = [
        column
        for column in (
            "model_id",
            "status",
            "converged",
            "warnflag",
            "log_likelihood",
            "aic",
            "bic",
            "residual_std",
            "residual_rmse",
            "ljung_box_p_value_lag12",
            "ljung_box_p_value_lag24",
        )
        if column in comparisons.columns
    ]
    print(comparisons[display_columns].to_string(index=False))
    print(f"Saved outputs under {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
