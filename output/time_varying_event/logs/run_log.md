# COVID減衰型介入モデル 実行ログ

- 実行ブランチ: feature/covid-decay-event
- 入力: data\processed\parcel_volume_connected.csv
- 期間: 2020-03--2023-05
- 観測数: 287か月
- 既存srcと既存output/sensitivity, output/forecastsは変更していない。
- covid_decayは2020年3月を起点にrho^kとし，2023年5月で打ち切った。
- rhoグリッド: 0.70, 0.80, 0.90, 0.95, 0.98

## 仕様

- 現行5変数: hike_dummy, covid_main, covid_wave1, covid_2021, post_stat_change
- 縮約ステップ: hike_dummy, covid_main, post_stat_change
- 減衰型: hike_dummy, covid_main, covid_decay, post_stat_change

## 結果概要

- 推定結果を取得できた仕様数: 7 / 7
- 収束仕様数: 5 / 7
- 減衰型の収束数: 4 / 5
- 非収束またはwarnflagあり: reduced_step, covid_decay_rho_095
- rho=0.90代表図: 成功
- AIC/BICだけで最良rhoを決めず，係数安定性，設計診断，残差診断，トレンド形状と併せて評価する。
- イベント係数は指定期間・指定減衰形に対応するモデル上の水準差であり，因果効果として解釈しない。

## 環境

- pandas: 2.2.3
- numpy: 2.2.5
- statsmodels: 0.14.4
- matplotlib: 3.10.1

## 生成ファイル

- metrics/model_comparison.csv
- metrics/coefficients.csv
- metrics/design_diagnostics.csv
- figures/decay_functions.png
- figures/rho_sensitivity_coefficients.png
- figures/rho_sensitivity_fit.png
- figures/components_representative_rho090.png
