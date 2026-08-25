"""Experimental COVID decay-event analysis.

The existing state-space class is reused without modifying src/. Outputs are
written only below output/time_varying_event/.
"""

from __future__ import annotations

import subprocess
import sys
import warnings
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from src.data_loader import load_connected_parcel_data
from src.paths import PROCESSED_DATA_DIR
from src.ssm_models import LocalLinearTrendSeasonalWithMultiFixedExog


OUTPUT_ROOT = PROJECT_ROOT / "output" / "time_varying_event"
METRICS_DIR = OUTPUT_ROOT / "metrics"
FIGURES_DIR = OUTPUT_ROOT / "figures"
LOG_PATH = OUTPUT_ROOT / "logs" / "run_log.md"
DATA_PATH = PROCESSED_DATA_DIR / "parcel_volume_connected.csv"

COVID_START = pd.Timestamp("2020-03-01")
COVID_END = pd.Timestamp("2023-05-01")
RHO_GRID = (0.70, 0.80, 0.90, 0.95, 0.98)
BASE_PARAM_NAMES = ["obs_error", "level_noise", "slope_noise", "seasonal_noise"]
PARAM_NAME_OVERRIDES = {"hike_dummy": "hike_effect"}
START_HINTS = {
    "hike_dummy": 0.0,
    "covid_main": -2.0,
    "covid_wave1": -2.0,
    "covid_2021": -3.0,
    "covid_decay": 0.0,
    "post_stat_change": 0.0,
}


def ensure_output_dirs() -> None:
    for directory in (METRICS_DIR, FIGURES_DIR, LOG_PATH.parent):
        directory.mkdir(parents=True, exist_ok=True)


def period_dummy(index: pd.DatetimeIndex, start: str, end: str | None) -> pd.Series:
    start_ts = pd.Timestamp(start)
    values = index >= start_ts
    if end is not None:
        values &= index <= pd.Timestamp(end)
    return pd.Series(values.astype(float), index=index)


def decay_variable(
    index: pd.DatetimeIndex,
    rho: float,
    start: pd.Timestamp = COVID_START,
    end: pd.Timestamp = COVID_END,
) -> pd.Series:
    values = np.zeros(len(index), dtype=float)
    active = (index >= start) & (index <= end)
    elapsed = ((index.year - start.year) * 12 + index.month - start.month).astype(int)
    values[active] = rho ** elapsed[active]
    return pd.Series(values, index=index, name="covid_decay")


def exog_frame(
    index: pd.DatetimeIndex, model_id: str, rho: float | None
) -> tuple[pd.DataFrame, str]:
    exog = pd.DataFrame(index=index)
    exog["hike_dummy"] = period_dummy(index, "2017-10-01", "2019-12-01")
    exog["covid_main"] = period_dummy(
        index, COVID_START.strftime("%Y-%m-%d"), COVID_END.strftime("%Y-%m-%d")
    )
    exog["post_stat_change"] = period_dummy(index, "2022-08-01", None)

    if model_id == "current_five_event":
        exog["covid_wave1"] = period_dummy(index, "2020-04-01", "2020-05-01")
        exog["covid_2021"] = period_dummy(index, "2021-01-01", "2021-09-01")
        names = ["hike_dummy", "covid_main", "covid_wave1", "covid_2021", "post_stat_change"]
        return exog[names], "current five-variable model"
    if model_id == "reduced_step":
        names = ["hike_dummy", "covid_main", "post_stat_change"]
        return exog[names], "reduced step model"
    if model_id.startswith("covid_decay_rho_"):
        if rho is None:
            raise ValueError("rho is required for a decay specification")
        exog["covid_decay"] = decay_variable(index, rho)
        names = ["hike_dummy", "covid_main", "covid_decay", "post_stat_change"]
        return exog[names], f"COVID decay intervention (rho={rho:.2f})"
    raise ValueError(f"Unknown model_id: {model_id}")


def param_names(exog_names: list[str]) -> list[str]:
    return BASE_PARAM_NAMES + [
        PARAM_NAME_OVERRIDES.get(name, f"{name}_effect") for name in exog_names
    ]


def start_params(exog_names: list[str]) -> list[float]:
    return [0.01, 0.01, 0.001, 0.001] + [
        START_HINTS.get(name, 0.0) for name in exog_names
    ]


def effect_percent(beta: float) -> float:
    return float(100.0 * np.expm1(beta)) if np.isfinite(beta) else np.nan


def effect_percent_se(beta: float, se: float) -> float:
    return float(100.0 * np.exp(beta) * se) if np.isfinite(beta + se) else np.nan


def design_diagnostics(exog: pd.DataFrame) -> dict:
    matrix = exog.to_numpy(dtype=float)
    try:
        condition = float(np.linalg.cond(matrix))
    except np.linalg.LinAlgError:
        condition = np.inf
    result = {
        "design_n_rows": int(matrix.shape[0]),
        "design_n_columns": int(matrix.shape[1]),
        "design_rank": int(np.linalg.matrix_rank(matrix)),
        "design_condition_number": condition,
        "corr_covid_main_covid_decay": np.nan,
        "corr_covid_main_post_stat_change": np.nan,
        "corr_covid_decay_post_stat_change": np.nan,
    }
    if {"covid_main", "covid_decay"} <= set(exog.columns):
        result["corr_covid_main_covid_decay"] = float(
            exog["covid_main"].corr(exog["covid_decay"])
        )
    if {"covid_main", "post_stat_change"} <= set(exog.columns):
        result["corr_covid_main_post_stat_change"] = float(
            exog["covid_main"].corr(exog["post_stat_change"])
        )
    if {"covid_decay", "post_stat_change"} <= set(exog.columns):
        result["corr_covid_decay_post_stat_change"] = float(
            exog["covid_decay"].corr(exog["post_stat_change"])
        )
    return result


def fit_one(df: pd.DataFrame, model_id: str, rho: float | None) -> dict:
    exog, label = exog_frame(df.index, model_id, rho)
    names = list(exog.columns)
    diagnostics = design_diagnostics(exog)
    names_full = param_names(names)
    row = {
        "model_id": model_id,
        "model_label": label,
        "model_family": (
            "current_five_event"
            if model_id == "current_five_event"
            else "reduced_step"
            if model_id == "reduced_step"
            else "covid_decay"
        ),
        "rho": rho,
        "covid_start": COVID_START.strftime("%Y-%m-%d"),
        "covid_end": COVID_END.strftime("%Y-%m-%d"),
        "status": "started",
        "error": "",
        "nobs": int(len(df)),
        **diagnostics,
    }
    coefficient_rows: list[dict] = []
    components = None
    try:
        model = LocalLinearTrendSeasonalWithMultiFixedExog(
            endog=df["y"],
            exog_list=[exog[name] for name in names],
            param_names=names_full,
            seasonal_period=12,
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = model.fit(
                start_params=start_params(names),
                maxiter=1000,
                disp=False,
            )
        convergence_warnings = [
            w for w in caught if issubclass(w.category, ConvergenceWarning)
        ]
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
        total_event = np.zeros(len(df), dtype=float)
        event_effects = {}
        for name in names:
            parameter = PARAM_NAME_OVERRIDES.get(name, f"{name}_effect")
            effect = estimates[parameter] * exog[name].to_numpy(dtype=float)
            event_effects[name] = effect
            total_event += effect
        fitted = trend + seasonal + total_event
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
        for event_name in ("covid_main", "covid_decay", "post_stat_change"):
            parameter = f"{event_name}_effect"
            if parameter in estimates:
                beta = estimates[parameter]
                row[f"{event_name}_estimate"] = beta
                row[f"{event_name}_std_error"] = errors[parameter]
                row[f"{event_name}_percent"] = effect_percent(beta)
                row[f"{event_name}_percent_se"] = effect_percent_se(beta, errors[parameter])

        for i, parameter in enumerate(names_full):
            is_event = parameter.endswith("_effect") or parameter == "hike_effect"
            coefficient_rows.append(
                {
                    "model_id": model_id,
                    "model_label": label,
                    "model_family": row["model_family"],
                    "rho": rho,
                    "parameter": parameter,
                    "parameter_group": "event" if is_event else "variance",
                    "estimate": params[i],
                    "std_error": standard_errors[i],
                    "z_value": zvalues[i],
                    "p_value": pvalues[i],
                    "percent_conversion": effect_percent(params[i]) if is_event else np.nan,
                    "percent_conversion_se": effect_percent_se(params[i], standard_errors[i]) if is_event else np.nan,
                }
            )
        components = {
            "index": df.index,
            "observed": df["y"].to_numpy(dtype=float),
            "fitted": fitted,
            "trend": trend,
            "seasonal": seasonal,
            "residual": residual,
            "event_effects": event_effects,
        }
    except Exception as exc:
        row.update(
            {
                "status": "failed",
                "converged": False,
                "warnflag": np.nan,
                "convergence_warning": False,
                "error": repr(exc),
            }
        )
    return {
        "comparison": row,
        "coefficients": coefficient_rows,
        "components": components,
        "design": {
            "model_id": model_id,
            "model_label": label,
            "model_family": row["model_family"],
            "rho": rho,
            "exog_columns": ",".join(names),
            **diagnostics,
        },
    }


def plot_decay_functions(index: pd.DatetimeIndex) -> None:
    active = index[(index >= COVID_START) & (index <= COVID_END)]
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    for rho in RHO_GRID:
        ax.plot(active, decay_variable(active, rho), linewidth=1.5, label=fr"$\rho={rho:.2f}$")
    ax.set_title("COVID decay intervention functions")
    ax.set_xlabel("Month")
    ax.set_ylabel(r"$z_t(\rho)$")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.grid(True, color="0.85", linewidth=0.8)
    ax.legend(ncol=2)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "decay_functions.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_rho_coefficients(comparisons: pd.DataFrame) -> None:
    decay = comparisons[
        (comparisons["model_family"] == "covid_decay")
        & (comparisons["status"] == "success")
    ].sort_values("rho")
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 8.5), sharex=True)
    for ax, name, title in zip(
        axes,
        ("covid_main", "covid_decay", "post_stat_change"),
        ("COVID step", "COVID decay", "Statistical connection"),
    ):
        if f"{name}_percent" in decay:
            y = decay[f"{name}_percent"].to_numpy(float)
            yerr = decay[f"{name}_percent_se"].to_numpy(float)
            ax.errorbar(decay["rho"], y, yerr=yerr, marker="o", color="black", capsize=3)
        ax.axhline(0, color="black", linestyle=":", linewidth=0.8)
        ax.set_ylabel("%")
        ax.set_title(title)
        ax.grid(True, color="0.88", linewidth=0.7)
    axes[-1].set_xlabel(r"Fixed decay parameter $\rho$")
    fig.suptitle("Coefficient sensitivity to the COVID decay shape", y=0.995)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "rho_sensitivity_coefficients.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_rho_fit(comparisons: pd.DataFrame) -> None:
    decay = comparisons[
        (comparisons["model_family"] == "covid_decay")
        & (comparisons["status"] == "success")
    ].sort_values("rho")
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 8.5), sharex=True)
    for ax, metric, title in zip(
        axes, ("log_likelihood", "aic", "bic"), ("Log likelihood", "AIC", "BIC")
    ):
        ax.plot(decay["rho"], decay[metric], marker="o", color="black", linewidth=1.3)
        ax.set_ylabel(title)
        ax.grid(True, color="0.88", linewidth=0.7)
    axes[-1].set_xlabel(r"Fixed decay parameter $\rho$")
    fig.suptitle("Fit metrics across fixed COVID decay shapes", y=0.995)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "rho_sensitivity_fit.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_components(components: dict) -> None:
    index = components["index"]
    effects = components["event_effects"]
    fig, axes = plt.subplots(6, 1, figsize=(9.0, 11.5), sharex=True)
    axes[0].plot(index, components["observed"], color="black", linewidth=0.9, label="Observed")
    axes[0].plot(index, components["fitted"], color="black", linestyle="--", linewidth=0.9, label="Fitted")
    axes[0].set_ylabel("log volume")
    axes[0].set_title("Representative COVID decay model (rho=0.90)")
    axes[0].legend(loc="upper left", ncol=2)
    axes[1].plot(index, components["trend"], color="black", linewidth=0.9)
    axes[1].set_ylabel("Trend")
    axes[2].plot(index, components["seasonal"], color="black", linewidth=0.9)
    axes[2].set_ylabel("Seasonal")
    axes[3].plot(index, effects["covid_main"], color="black", linewidth=0.9, label="COVID step")
    axes[3].plot(index, effects["covid_decay"], color="black", linestyle="--", linewidth=0.9, label="COVID decay")
    axes[3].set_ylabel("COVID effects")
    axes[3].legend(loc="upper left", ncol=2)
    axes[4].plot(index, effects["post_stat_change"], color="black", linewidth=0.9)
    axes[4].set_ylabel("Stat. correction")
    axes[5].plot(index, components["residual"], color="black", linewidth=0.9)
    axes[5].axhline(0, color="black", linestyle=":", linewidth=0.8)
    axes[5].set_ylabel("Residual")
    axes[5].set_xlabel("Month")
    for ax in axes:
        ax.grid(True, color="0.88", linewidth=0.7)
        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "components_representative_rho090.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_log(comparisons: pd.DataFrame, representative_ok: bool) -> None:
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    fit_returned = comparisons[comparisons["status"] == "success"]
    converged = fit_returned[fit_returned["converged"] == True]
    decay_fit_returned = fit_returned[fit_returned["model_family"] == "covid_decay"]
    decay_converged = decay_fit_returned[decay_fit_returned["converged"] == True]
    nonconverged_ids = fit_returned.loc[
        fit_returned["converged"] != True, "model_id"
    ].tolist()
    lines = [
        "# COVID減衰型介入モデル 実行ログ",
        "",
        f"- 実行ブランチ: {branch}",
        f"- 入力: {DATA_PATH.relative_to(PROJECT_ROOT)}",
        f"- 期間: {COVID_START:%Y-%m}--{COVID_END:%Y-%m}",
        f"- 観測数: {len(pd.read_csv(DATA_PATH))}か月",
        "- 既存srcと既存output/sensitivity, output/forecastsは変更していない。",
        "- covid_decayは2020年3月を起点にrho^kとし，2023年5月で打ち切った。",
        "- rhoグリッド: " + ", ".join(f"{rho:.2f}" for rho in RHO_GRID),
        "",
        "## 仕様",
        "",
        "- 現行5変数: hike_dummy, covid_main, covid_wave1, covid_2021, post_stat_change",
        "- 縮約ステップ: hike_dummy, covid_main, post_stat_change",
        "- 減衰型: hike_dummy, covid_main, covid_decay, post_stat_change",
        "",
        "## 結果概要",
        "",
        f"- 推定結果を取得できた仕様数: {len(fit_returned)} / {len(comparisons)}",
        f"- 収束仕様数: {len(converged)} / {len(comparisons)}",
        f"- 減衰型の収束数: {len(decay_converged)} / {len(RHO_GRID)}",
        "- 非収束またはwarnflagあり: "
        + (", ".join(nonconverged_ids) if nonconverged_ids else "なし"),
        f"- rho=0.90代表図: {'成功' if representative_ok else '失敗'}",
        "- AIC/BICだけで最良rhoを決めず，係数安定性，設計診断，残差診断，トレンド形状と併せて評価する。",
        "- イベント係数は指定期間・指定減衰形に対応するモデル上の水準差であり，因果効果として解釈しない。",
        "",
        "## 環境",
        "",
        f"- pandas: {pd.__version__}",
        f"- numpy: {np.__version__}",
        f"- statsmodels: {statsmodels.__version__}",
        f"- matplotlib: {matplotlib.__version__}",
        "",
        "## 生成ファイル",
        "",
        "- metrics/model_comparison.csv",
        "- metrics/coefficients.csv",
        "- metrics/design_diagnostics.csv",
        "- figures/decay_functions.png",
        "- figures/rho_sensitivity_coefficients.png",
        "- figures/rho_sensitivity_fit.png",
        "- figures/components_representative_rho090.png",
        "",
    ]
    LOG_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_output_dirs()
    if not DATA_PATH.exists():
        raise FileNotFoundError(DATA_PATH)
    df = load_connected_parcel_data(str(DATA_PATH))
    specs: list[tuple[str, float | None]] = [
        ("current_five_event", None),
        ("reduced_step", None),
    ]
    specs.extend(
        (f"covid_decay_rho_{int(round(rho * 100)):03d}", rho) for rho in RHO_GRID
    )

    comparison_rows: list[dict] = []
    coefficient_rows: list[dict] = []
    design_rows: list[dict] = []
    fitted_components: dict[str, dict] = {}
    for model_id, rho in specs:
        result = fit_one(df, model_id, rho)
        comparison_rows.append(result["comparison"])
        coefficient_rows.extend(result["coefficients"])
        design_rows.append(result["design"])
        if result["components"] is not None:
            fitted_components[model_id] = result["components"]

    comparisons = pd.DataFrame(comparison_rows)
    coefficients = pd.DataFrame(coefficient_rows)
    designs = pd.DataFrame(design_rows)
    comparisons.to_csv(METRICS_DIR / "model_comparison.csv", index=False)
    coefficients.to_csv(METRICS_DIR / "coefficients.csv", index=False)
    designs.to_csv(METRICS_DIR / "design_diagnostics.csv", index=False)

    plot_decay_functions(df.index)
    plot_rho_coefficients(comparisons)
    plot_rho_fit(comparisons)
    representative_id = "covid_decay_rho_090"
    representative_ok = representative_id in fitted_components
    if representative_ok:
        plot_components(fitted_components[representative_id])
    write_log(comparisons, representative_ok)
    print(comparisons.to_string(index=False))
    print(f"Saved outputs under {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
