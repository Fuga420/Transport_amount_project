# src/visualization.py

from __future__ import annotations

from itertools import cycle
from typing import Dict, List, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


EventConfig = Dict[str, Tuple[str, Optional[str]]]


class ThesisVisualizer:
    """
    論文用のモノクロスタイルで時系列分解図を作成するクラス。

    - すべての成分に平滑化推定量を使用する
    - post_stat_change などの接続補正項は、推定には含めても図から除外可能
    """

    def __init__(
        self,
        result,
        df: pd.DataFrame,
        exog_names: Optional[List[str]] = None,
        event_config: Optional[EventConfig] = None,
        effects_to_plot: Optional[List[str]] = None,
        n_base_params: int = 4,
    ):
        self.result = result
        self.df = df
        self.exog_names = exog_names if exog_names is not None else []
        self.event_config = event_config if event_config is not None else {}
        self.effects_to_plot = effects_to_plot
        self.n_base_params = n_base_params

        sns.set_theme(style="whitegrid")
        plt.rcParams["figure.figsize"] = (10, 15)
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.size"] = 11

    def _compute_components(self) -> dict:
        """
        平滑化状態を用いて各成分を計算する。
        """
        if "y" not in self.df.columns:
            raise ValueError("df に 'y' 列が必要です。")

        trend_smoothed = self.result.smoothed_state[0, :]
        seasonal_smoothed = self.result.smoothed_state[2, :]

        total_exog_effect = np.zeros(len(self.df))
        effects = {}

        for i, name in enumerate(self.exog_names):
            beta = self.result.params[self.n_base_params + i]

            if name not in self.df.columns:
                raise ValueError(f"外生変数 '{name}' が df に存在しません。")

            series = self.df[name].values
            effect = beta * series

            effects[name] = effect
            total_exog_effect += effect

        fitted_smoothed = trend_smoothed + seasonal_smoothed + total_exog_effect
        resid_smoothed = self.df["y"].values - fitted_smoothed

        return {
            "trend": trend_smoothed,
            "seasonal": seasonal_smoothed,
            "effects": effects,
            "total_exog_effect": total_exog_effect,
            "fitted": fitted_smoothed,
            "residual": resid_smoothed,
        }

    def plot_reproduction(
        self,
        title_suffix: str = "",
        save_path: Optional[str] = None,
        show: bool = True,
    ):
        """
        5段構成の時系列分解図を作成する。

        Parameters
        ----------
        title_suffix : str
            各タイトルの末尾につける文字列
        save_path : str, optional
            保存先パス
        show : bool
            True の場合、plt.show() する
        """
        components = self._compute_components()

        fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True)

        # 1. Observed vs Fitted
        axes[0].plot(
            self.df.index,
            self.df["y"],
            color="dimgray",
            label="Observed",
            linewidth=0.8,
        )
        axes[0].plot(
            self.df.index,
            components["fitted"],
            color="black",
            linestyle="--",
            label="Fitted",
            linewidth=1.0,
        )
        axes[0].set_title(f"Observed vs. Fitted Values{title_suffix}", fontsize=14)
        axes[0].legend(loc="upper left")

        # 2. Trend
        axes[1].plot(
            self.df.index,
            components["trend"],
            color="black",
            label="Trend",
            linewidth=0.8,
        )
        axes[1].set_title(f"Trend Component{title_suffix}", fontsize=14)

        # 3. Seasonal
        axes[2].plot(
            self.df.index,
            components["seasonal"],
            color="black",
            label="Seasonal",
            linewidth=0.8,
        )
        axes[2].set_title(f"Seasonal Component{title_suffix}", fontsize=14)
        axes[2].axhline(y=0, color="grey", linestyle=":", linewidth=1)

        # 4. External Event Effects
        line_styles = cycle(["-.", "--", "-", ":"])

        for name, series in components["effects"].items():
            if self.effects_to_plot is not None and name not in self.effects_to_plot:
                continue

            linestyle = next(line_styles)
            label_name = name.replace("_", " ").title()

            axes[3].plot(
                self.df.index,
                series,
                color="black",
                linestyle=linestyle,
                label=label_name,
                linewidth=1.0,
            )

        axes[3].set_title(f"External Event Effects{title_suffix}", fontsize=14)
        axes[3].axhline(y=0, color="grey", linestyle=":", linewidth=1)
        axes[3].legend(loc="upper left")

        # 5. Residuals
        axes[4].plot(
            self.df.index,
            components["residual"],
            color="black",
            linewidth=0.8,
            label="Residuals",
        )
        axes[4].set_title(f"Residuals{title_suffix}", fontsize=14)
        axes[4].axhline(y=0, color="grey", linestyle=":", linewidth=1)
        axes[4].set_xlabel("Date", fontsize=12)

        for ax in axes:
            ax.set_ylabel("Value (log)")
            self._add_gray_shading(ax)
            self._format_xaxis(ax)

        plt.tight_layout()

        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        if show:
            plt.show()

        return fig, axes

    def _add_gray_shading(self, ax):
        """
        イベント期間にグレーの背景色を付ける。
        post_stat_change は通常 event_config に含めない。
        """
        for name, (start, end) in self.event_config.items():
            start_ts = pd.Timestamp(start)
            end_ts = pd.Timestamp(end) if end is not None else self.df.index[-1]

            ax.axvspan(
                start_ts,
                end_ts,
                color="gray",
                alpha=0.15,
                zorder=-1,
            )

    @staticmethod
    def _format_xaxis(ax):
        """
        x軸の日付表示を整える。
        """
        ax.xaxis.set_major_locator(mdates.YearLocator(base=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))