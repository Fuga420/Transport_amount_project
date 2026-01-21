import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import seaborn as sns
from itertools import cycle

class ColorThesisVisualizer:
    """
    論文用のカラープロットを作成するクラス（修正版）
    - 線の色: 基本的に「黒」で統一
    - Fitted（当てはまり）: 「オレンジ」
    - 背景帯（外生変数）: 画像のカラーパレット（青・紺系）を使用
    """
    def __init__(self, result, df, exog_names=None, event_config=None):
        self.result = result
        self.df = df
        self.exog_names = exog_names if exog_names else []
        self.event_config = event_config if event_config else {}
        
        # --- 画像に基づくカラー定義 (近似HEXコード) ---
        self.event_colors = {
            'hike_dummy': '#2B4F73',   # 深い青 (beta1)
            'covid_main': '#C6D9E9',   # 薄い水色 (beta2)
            'covid_wave1': '#030615',  # ほぼ黒に近い紺 (beta3)
            'covid_2021': '#4671A0',   # 中間の青 (beta4)
        }
        self.default_event_color = 'gray'

        # --- スタイル設定 ---
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (10, 15)
        plt.rcParams['font.family'] = 'sans-serif' 
        plt.rcParams['font.size'] = 11
        # グリッド線は控えめに
        plt.rcParams['grid.alpha'] = 0.5

    def plot_reproduction(self):
        """
        ユーザー指定の「5段構成」を再現する。
        """
        # --- 1. 平滑化済み成分の取得と計算 ---
        
        # (A) トレンドと季節性 (smoothed_stateを使用)
        trend_smoothed = self.result.smoothed_state[0, :]
        seasonal_smoothed = self.result.smoothed_state[2, :]

        # (B) 外生変数の効果
        n_base_params = 4
        total_exog_effect = np.zeros(len(self.df))
        effects = {}
        
        for i, name in enumerate(self.exog_names):
            beta = self.result.params[n_base_params + i]
            series = self.df[name].values
            effect = beta * series
            
            effects[name] = effect
            total_exog_effect += effect

        # (C) Smoothed Fitted Value
        fitted_smoothed = trend_smoothed + seasonal_smoothed + total_exog_effect

        # (D) Smoothed Residuals
        resid_smoothed = self.df['y'] - fitted_smoothed


        # --- 2. プロット作成 ---
        fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        # [Ax0] Observed vs Smoothed Fitted
        # 観測値は黒、Fitted（Smoothed）はオレンジ
        axes[0].plot(self.df.index, self.df['y'], color='black', label='Observed', linewidth=1.0)
        axes[0].plot(self.df.index, fitted_smoothed, color="#f1c39b", linestyle='--', label='Fitted', linewidth=0.8)
        axes[0].set_title('Observed vs. Fitted Values', fontsize=14, fontweight='bold')
        axes[0].legend(loc='upper left', frameon=True)

        # [Ax1] Trend -> 黒
        axes[1].plot(self.df.index, trend_smoothed, color='black', label='Trend', lw=1.2)
        axes[1].set_title('Trend Component', fontsize=14)
        
        # [Ax2] Seasonal -> 黒
        axes[2].plot(self.df.index, seasonal_smoothed, color='black', label='Seasonal', lw=1.0)
        axes[2].set_title('Seasonal Component', fontsize=14)
        axes[2].axhline(y=0, color='grey', linestyle=':', linewidth=1)

        # [Ax3] External Event Effects -> 黒（線種で区別）
        # 複数の線が重なるため、線種(linestyle)を変えて区別しやすくしています
        line_styles = cycle(['-', '--', '-.', ':'])
        for name, series in effects.items():
            ls = next(line_styles)
            label_name = name.replace('_', ' ').title()
            axes[3].plot(self.df.index, series, color='black', linestyle=ls, label=label_name, linewidth=1.2)
            
        axes[3].set_title('External Event Effects', fontsize=14)
        axes[3].axhline(y=0, color='grey', linestyle=':', linewidth=1)
        axes[3].legend(loc='upper left', frameon=True)

        # [Ax4] Residuals -> 黒
        axes[4].plot(self.df.index, resid_smoothed, color='black', linewidth=0.8, label='Residuals')
        axes[4].set_title('Residuals', fontsize=14)
        axes[4].axhline(y=0, color='grey', linestyle=':', linewidth=1)
        axes[4].set_xlabel('Date', fontsize=12)

        # --- 全グラフ共通設定（背景色の適用） ---
        for ax in axes:
            ax.set_ylabel('Value (log)')
            self._add_colored_shading(ax)

        plt.tight_layout()
        plt.show()

    def _add_colored_shading(self, ax):
        """
        イベント期間に指定のカラーで背景色を付ける
        """
        for name, (start, end) in self.event_config.items():
            if end is None: end = self.df.index[-1]
            
            # イベント名に対応する色を取得
            color = self.event_colors.get(name, self.default_event_color)
            
            # alpha値で透明度を調整
            ax.axvspan(start, end, color=color, alpha=0.8, zorder=-1)