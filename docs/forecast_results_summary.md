# Forecast Results Summary

ゼミ報告用に、fixed A/B の予測評価結果を要約する。参照元は以下の既存CSVである。

- `output/forecasts/metrics/model_comparison_fixed_splits.csv`
- `output/forecasts/metrics/model_comparison_best_by_split.csv`

## 比較設定

評価はすべて `number_parcels` の原系列スケールで行った。主な指標は RMSE、MAE、MAPE、MASE である。

| split | train | test | 目的 |
|---|---|---|---|
| fixed A | 2002-04 to 2019-12 | 2020-01 to 2021-12 | COVID期を含む短期外挿 |
| fixed B | 2002-04 to 2023-12 | 2024-01 to 2026-02 | 後続統計接続後を含む直近予測 |

## 情報条件の違い

モデル比較では、情報条件が異なる点に注意する必要がある。

| information_set | 該当モデル | 説明 |
|---|---|---|
| unconditional | naive, seasonal naive, SARIMA, Prophet, autoformer_lite | test期間のイベントダミー等を使わない |
| conditional_exog_known | SARIMAX, SSM | test期間の外生ダミーを既知として与える |

したがって、SARIMAX/SSM と Prophet/SARIMA/seasonal naive/autoformer_lite は、単純な予測精度だけで横並びに解釈しない。

## Best Model

| split | best model | information_set | RMSE | MAPE | MASE |
|---|---|---|---:|---:|---:|
| fixed A | prophet | unconditional | 27,498.77 | 6.25 | 2.24 |
| fixed B | sarimax_grid_best | conditional_exog_known | 7,975.06 | 1.71 | 0.54 |

## fixed A の結果

fixed A では Prophet が最も良い。unconditional モデルとしても、conditional モデルを含めた全体としても RMSE が最小である。

| rank | model | information_set | RMSE | MAPE |
|---:|---|---|---:|---:|
| 1 | prophet | unconditional | 27,498.77 | 6.25 |
| 2 | sarimax_grid_best | conditional_exog_known | 29,828.57 | 6.78 |
| 3 | ssm_conditional | conditional_exog_known | 30,857.61 | 7.02 |
| 4 | sarimax_fixed | conditional_exog_known | 33,985.76 | 7.83 |
| 5 | sarima_grid_best | unconditional | 40,578.64 | 9.59 |
| 6 | sarima_fixed | unconditional | 41,548.02 | 9.84 |
| 7 | seasonal_naive | unconditional | 44,753.89 | 10.34 |
| 8 | naive | unconditional | 80,656.77 | 20.09 |

解釈として、COVID期の fixed A では、Prophet のトレンド・季節性モデルが比較的うまく機能している。一方、SARIMAX/SSM は外生ダミー既知の conditional forecast であるため、情報条件の違いに注意する。

## fixed B の結果

fixed B では SARIMAX grid best が最も良い。SSM conditional もほぼ同水準で強い。

| rank | model | information_set | RMSE | MAPE |
|---:|---|---|---:|---:|
| 1 | sarimax_grid_best | conditional_exog_known | 7,975.06 | 1.71 |
| 2 | ssm_conditional | conditional_exog_known | 8,112.66 | 1.72 |
| 3 | sarimax_fixed | conditional_exog_known | 8,196.97 | 1.76 |
| 4 | seasonal_naive | unconditional | 13,622.78 | 2.91 |
| 5 | sarima_grid_best | unconditional | 14,790.76 | 3.07 |
| 6 | sarima_fixed | unconditional | 16,686.68 | 3.50 |
| 7 | prophet | unconditional | 26,730.00 | 4.83 |
| 8 | autoformer_lite | unconditional | 35,587.39 | 8.54 |
| 9 | naive | unconditional | 107,649.95 | 27.06 |

unconditional モデルだけで見ると、fixed B の best は seasonal naive である。conditional モデルを含めると SARIMAX grid best が best になる。

## autoformer_lite の位置づけ

autoformer_lite は fixed B のみ実装済みである。厳密な Autoformer 本体ではなく、Autoformer-inspired / decomposition Transformer baseline として扱う。

fixed B では naive よりは良いが、seasonal naive、SARIMA、SARIMAX、SSM、Prophet より悪い。月次287点程度の小標本では深層学習系モデルは過学習しやすく、現段階では参考baselineとして扱うのが妥当である。

## 報告時の要点

- fixed A の best は Prophet。
- fixed B の overall best は SARIMAX grid best。
- fixed B の unconditional best は seasonal naive。
- SARIMAX/SSM は conditional forecast であり、test期間の外生ダミーを既知として与えている。
- Prophet は fixed A では強いが、fixed B では seasonal naive や SARIMA より弱い。
- autoformer_lite は参考baselineであり、現時点では既存の単純・統計モデルを上回っていない。

## 今後の確認事項

- main 分析に使う比較では、conditional/unconditional を分けて提示する。
- SARIMAX grid best は小規模グリッド内の best であり、探索範囲を広げると結果が変わる可能性がある。
- autoformer_lite は fixed A 未実装であり、必要なら追加実験として扱う。
- 予測評価を論文本文に入れる場合は、評価設計と情報条件の説明を明確にする。
