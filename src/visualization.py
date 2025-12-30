import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import seaborn as sns
from itertools import cycle

class ThesisVisualizer:
    """
    論文用のモノクロスタイル（白黒・線種区別）で時系列プロットを作成するクラス
    ※すべての成分に「平滑化（Smoothed）」推定量を使用する
    """
    def __init__(self, result, df, exog_names=None, event_config=None):
        self.result = result
        self.df = df
        self.exog_names = exog_names if exog_names else []
        self.event_config = event_config if event_config else {}
        
        # --- スタイル設定 ---
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (10, 15)
        plt.rcParams['font.family'] = 'sans-serif' 
        plt.rcParams['font.size'] = 11

    def plot_reproduction(self):
        """
        ユーザー指定の「5段構成」を再現する。
        フィルタ値（Filtered）ではなく、平滑化値（Smoothed）を使用する。
        """
        # --- 1. 平滑化済み成分の取得と計算 ---
        
        # (A) トレンドと季節性 (smoothed_stateを使用)
        # モデル定義: state[0]=Level, state[1]=Slope, state[2...]=Seasonal
        trend_smoothed = self.result.smoothed_state[0, :]
        seasonal_smoothed = self.result.smoothed_state[2, :]

        # (B) 外生変数の効果 (係数 x データ)
        # ※係数自体は全期間一定なので、smoothedもfilteredも同じですが、計算に使用します
        n_base_params = 4
        total_exog_effect = np.zeros(len(self.df))
        effects = {}
        
        for i, name in enumerate(self.exog_names):
            beta = self.result.params[n_base_params + i]
            series = self.df[name].values
            effect = beta * series
            
            effects[name] = effect
            total_exog_effect += effect

        # (C) Smoothed Fitted Value (全データに基づく当てはまり)
        # 観測方程式: y = Level + Seasonal + Exog + Noise
        # したがって、Fitted = Level(smooth) + Seasonal(smooth) + Exog
        fitted_smoothed = trend_smoothed + seasonal_smoothed + total_exog_effect

        # (D) Smoothed Residuals (不規則項 Irregular)
        # 観測値 - 平滑化Fitted
        resid_smoothed = self.df['y'] - fitted_smoothed


        # --- 2. プロット作成 ---
        fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True)
        
        # [Ax0] Observed vs Smoothed Fitted
        axes[0].plot(self.df.index, self.df['y'], color='dimgray', label='Observed', linewidth=0.8)
        # ここを平滑化値に変更
        axes[0].plot(self.df.index, fitted_smoothed, color='black', linestyle='--', label='Fitted (Smoothed)', linewidth=1)
        axes[0].set_title('Observed vs. Fitted Values (Smoothed)', fontsize=14)
        axes[0].legend(loc='upper left')

        # [Ax1] Trend (Smoothed)
        axes[1].plot(self.df.index, trend_smoothed, color='black', label='Trend', lw=0.8)
        axes[1].set_title('Trend Component (Smoothed)', fontsize=14)
        
        # [Ax2] Seasonal (Smoothed)
        axes[2].plot(self.df.index, seasonal_smoothed, color='black', label='Seasonal', lw=0.8)
        axes[2].set_title('Seasonal Component (Smoothed)', fontsize=14)
        axes[2].axhline(y=0, color='grey', linestyle=':', linewidth=1)

        # [Ax3] External Event Effects
        line_styles = cycle(['-.', '--', '-', ':'])
        for name, series in effects.items():
            ls = next(line_styles)
            label_name = name.replace('_', ' ').title()
            axes[3].plot(self.df.index, series, color='black', linestyle=ls, label=label_name, linewidth=1)
            
        axes[3].set_title('External Event Effects', fontsize=14)
        axes[3].axhline(y=0, color='grey', linestyle=':', linewidth=1)
        axes[3].legend(loc='upper left')

        # [Ax4] Residuals (Smoothed) -> つまり Irregular Component
        axes[4].plot(self.df.index, resid_smoothed, color='black', linewidth=0.8, label='Residuals')
        axes[4].set_title('Residuals (Observed - Smoothed Fitted)', fontsize=14)
        axes[4].axhline(y=0, color='grey', linestyle=':', linewidth=1)
        axes[4].set_xlabel('Date', fontsize=12)

        # --- 全グラフ共通設定 ---
        for ax in axes:
            ax.set_ylabel('Value (log)')
            self._add_gray_shading(ax)

        plt.tight_layout()
        plt.show()

    def _add_gray_shading(self, ax):
        """
        イベント期間にグレーの背景色を付ける
        """
        for i, (name, (start, end)) in enumerate(self.event_config.items()):
            if end is None: end = self.df.index[-1]
            ax.axvspan(start, end, color='gray', alpha=0.15, zorder=-1)