# ゼミ報告用メモ: 系列接続・主分析・予測評価の整理

このメモは、宅配便取扱個数の月次系列について、これまでに行った研究作業をゼミで説明するために整理したものである。予測評価だけを単独で見るのではなく、旧統計と後続統計の接続、主分析モデル、`covid_main` 期間設定の感度分析を踏まえたうえで、最後に予測評価を位置づける。

参照した主な結果は、`output/forecasts/metrics/model_comparison_fixed_splits.csv` と `output/forecasts/metrics/model_comparison_best_by_split.csv` である。

## 1. 研究全体の目的

本研究の目的は、日本国内の宅配便取扱個数の月次系列を対象に、構造変化と予測性能を分析することである。

主分析では、状態空間モデルを用いて、宅配便取扱個数の変動をトレンド、季節性、イベント効果に分解する。特に、運賃改定、COVID-19、統計接続後の水準差といった要因が系列にどのように影響しているかを確認する。

予測評価は、主分析モデルの妥当性を予測面から補助的に確認するための分析である。単なる精度競争ではなく、どの期間で、どの情報条件のもとで、どのモデルが有効かを見ることを目的としている。

## 2. データ接続の背景

旧統計は、国土交通省「トラック輸送情報」に基づく宅配便取扱個数の系列である。この系列は大手14社ベースの月次データとして扱っている。

一方、後続統計は、国土交通省「国土交通月例経済」に基づく系列であり、大手3社ベースである。旧系列と後続系列では対象企業の範囲が異なるため、同じ「宅配便取扱個数」であっても水準が完全には一致しない。

重複して確認できる期間は 2022年5月から2022年7月であり、この期間では後続系列は旧系列のおよそ95〜96%程度の水準であった。したがって、単純に後続統計をつなぐだけでは、統計定義の変更による水準差が系列に混入する可能性がある。

このため、接続後の分析では `post_stat_change` のような水準変化ダミーを考慮する必要がある。

## 3. 接続済み系列の位置づけ

予測評価では、接続済みデータ `data/processed/parcel_volume_connected.csv` を使用している。

このデータでは、目的変数として `number_parcels` を用いる。SARIMA、SARIMAX、SSM、Prophet、autoformer_lite など、モデルによっては学習時に `y = log(number_parcels)` を用いるが、予測評価はすべて `number_parcels` の原系列スケールで行っている。

評価スケールを原系列に統一することで、モデル間のRMSE、MAE、MAPE、MASEを同じ単位で比較できる。

## 4. 主分析モデルの位置づけ

主分析モデルは、local linear trend + seasonal + event dummies の状態空間モデルである。

基本的には、時系列を以下の要素に分けて考える。

- 長期的な水準変化を表すトレンド
- 月次データ特有の季節性
- 外生的なイベント効果
- 観測誤差

主なイベントダミーは以下である。

| 変数 | 意味 |
|---|---|
| `hike_dummy` | 運賃改定期の影響 |
| `covid_main` | COVID-19期の主要な構造変化 |
| `covid_wave1` | COVID初期波の短期的影響 |
| `covid_2021` | 2021年のCOVID関連局面 |
| `post_stat_change` | 後続統計接続後の水準差 |

このうち `post_stat_change` は、需要イベントというよりも、統計定義変更に伴う水準差を補正するための変数として重要である。

## 5. covid_main期間感度分析

`covid_main` は、COVID-19による主要な構造変化を表す変数である。ただし、COVID期をどこまでとみなすかは自明ではない。

そのため、`covid_main` の終了時点を複数候補で変え、モデルの当てはまり、係数の安定性、`post_stat_change` の安定性、残差診断、トレンド形状を比較する感度分析を行った。

比較候補は以下である。

| 仕様 | covid_main期間 |
|---|---|
| M1 | 2020-03〜2021-12 |
| M2 | 2020-03〜2022-03 |
| M2b | 2020-03〜2022-06 |
| M3 | 2020-03〜2022-12 |
| M4 | 2020-03〜2023-05 |
| M5 | 2020-03以降ずっと |

この感度分析で重要なのは、AIC/BICだけで仕様を決めないことである。係数の符号や大きさが安定しているか、`post_stat_change` が不自然に吸収されていないか、トレンドに不自然な屈曲がないか、社会的に説明しやすい期間設定かを合わせて見る必要がある。

特に M5 は、当てはまりが良くなる可能性がある一方で、`covid_main` を恒久的な水準変化として解釈してしまうリスクがある。そのため、主分析仕様は統計的当てはまりだけでなく、解釈可能性を重視して決める必要がある。

## 6. 予測評価を行った理由

接続済み系列とイベント仕様を整理したうえで、複数モデルの予測性能を同一基準で比較した。

予測評価の目的は、主分析モデルであるSSMが、説明面だけでなく予測面でもどの程度妥当かを確認することである。また、期間や情報条件によって、単純な季節モデル、統計モデル、状態空間モデル、機械学習系モデルのどれが有効かを見る補助分析でもある。

このため、予測評価は「最も精度が良いモデルを選ぶ」だけではなく、主分析の解釈を支える補助的な検証として位置づける。

## 7. 予測評価設計

評価は fixed split で行った。

| split | 学習期間 | 評価期間 | 評価期間の意味 |
|---|---|---|---|
| fixed A | 2002-04〜2019-12 | 2020-01〜2021-12 | COVID期を含む予測 |
| fixed B | 2002-04〜2023-12 | 2024-01〜2026-02 | 後続統計接続後を含む直近予測 |

評価指標は以下である。

- RMSE
- MAE
- MAPE
- MASE

評価はすべて `number_parcels` の原系列スケールで行った。

## 8. 比較モデル

比較したモデルは以下である。

| モデル | 概要 |
|---|---|
| naive | 最後の観測値をそのまま将来に使う |
| seasonal naive | 前年同月の値を使う |
| SARIMA | 外生変数なしの季節ARIMA |
| SARIMAX | イベントダミーを外生変数として与えるSARIMAX |
| SSM | 主分析と同じ状態空間モデル |
| Prophet | holidaysなし・regressorsなしのProphet |
| autoformer_lite | Autoformer-inspired / decomposition Transformer baseline |

autoformer_lite は厳密なAutoformer本体ではない。外生変数なしの軽量な参考baselineとして扱う。

## 9. 情報条件の整理

予測評価では、モデルごとに利用できる情報条件が異なる。

| 情報条件 | モデル | 説明 |
|---|---|---|
| unconditional forecast | naive, seasonal naive, SARIMA, Prophet, autoformer_lite | test期間の外生ダミーを使わない |
| conditional forecast | SARIMAX, SSM | test期間の外生ダミーを既知として与える |

したがって、SARIMAX/SSM と Prophet/SARIMA/seasonal naive/autoformer_lite を単純に横並びで比較する場合は注意が必要である。

## 10. fixed A の結果

fixed A では Prophet が最も良い結果だった。

| rank | model | information_set | RMSE | MAPE | MASE |
|---:|---|---|---:|---:|---:|
| 1 | prophet | unconditional | 27,498.77 | 6.25 | 2.24 |
| 2 | sarimax_grid_best | conditional_exog_known | 29,828.57 | 6.78 | 2.49 |
| 3 | ssm_conditional | conditional_exog_known | 30,857.61 | 7.02 | 2.57 |
| 4 | sarimax_fixed | conditional_exog_known | 33,985.76 | 7.83 | 2.88 |
| 5 | sarima_grid_best | unconditional | 40,578.64 | 9.59 | 3.53 |
| 6 | sarima_fixed | unconditional | 41,548.02 | 9.84 | 3.62 |
| 7 | seasonal_naive | unconditional | 44,753.89 | 10.34 | 3.83 |
| 8 | naive | unconditional | 80,656.77 | 20.09 | 6.98 |

Prophet は外生変数なしでも良い予測性能を示した。ただし、ProphetはCOVID要因を明示的に説明しているわけではない。したがって、fixed A のProphetの良さは予測性能として評価しつつ、構造変化の解釈はSSMやSARIMAXのイベントダミー分析と分けて考える必要がある。

SARIMAX grid best と SSM も良好であり、COVID期のイベントダミーを既知として与えた conditional forecast として一定の妥当性が確認できる。

## 11. fixed B の結果

fixed B では SARIMAX grid best が最も良い結果だった。SSMも非常に近い性能を示している。

| rank | model | information_set | RMSE | MAPE | MASE |
|---:|---|---|---:|---:|---:|
| 1 | sarimax_grid_best | conditional_exog_known | 7,975.06 | 1.71 | 0.54 |
| 2 | ssm_conditional | conditional_exog_known | 8,112.66 | 1.72 | 0.54 |
| 3 | sarimax_fixed | conditional_exog_known | 8,196.97 | 1.76 | 0.55 |
| 4 | seasonal_naive | unconditional | 13,622.78 | 2.91 | 0.93 |
| 5 | sarima_grid_best | unconditional | 14,790.76 | 3.07 | 0.98 |
| 6 | sarima_fixed | unconditional | 16,686.68 | 3.50 | 1.12 |
| 7 | prophet | unconditional | 26,730.00 | 4.83 | 1.59 |
| 8 | autoformer_lite | unconditional | 35,587.39 | 8.54 | 2.59 |
| 9 | naive | unconditional | 107,649.95 | 27.06 | 8.14 |

conditional forecast を含めると、SARIMAX grid best と SSM が強い。一方、unconditional forecast だけで見ると、seasonal naive が最も良い。

この結果から、直近期では前年同月パターンがかなり強く、さらに統計接続後の水準差やイベントダミーを既知として扱える場合には、SARIMAX/SSMが高い予測性能を示す可能性がある。

## 12. SSMの位置づけ

SSMは fixed A/B の両方で安定して良好な性能を示している。

| split | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| fixed A | 30,857.61 | 7.02 | 2.57 |
| fixed B | 8,112.66 | 1.72 | 0.54 |

fixed A では全体3位、fixed B では全体2位であり、主分析モデルとして説明面だけでなく、予測面でも一定の妥当性がある。

ただし、SSMの予測は conditional forecast であり、test期間の外生ダミーを既知として与えている。この点は、Prophetやseasonal naiveとの比較で明示する必要がある。

## 13. Autoformer-liteの位置づけ

autoformer_lite は fixed B のみ実装した。これは厳密なAutoformerではなく、Autoformer-inspired / decomposition Transformer baseline である。

fixed B の結果は以下である。

| model | information_set | RMSE | MAPE | MASE |
|---|---|---:|---:|---:|
| autoformer_lite | unconditional | 35,587.39 | 8.54 | 2.59 |

autoformer_lite は naive よりは良いが、seasonal naive、SARIMA、SARIMAX、SSM、Prophetには劣る。月次287点程度の小標本では、深層学習系モデルは過学習しやすく、現段階では参考baselineとして扱うのが妥当である。

## 14. 暫定結論

ここまでの結果から、以下のように整理できる。

- 旧統計と後続統計には水準差があるため、接続後の水準変化を考慮する必要がある。
- `post_stat_change` は、後続統計接続後の水準差を扱ううえで重要である。
- `covid_main` の期間設定は主分析結果に影響するため、AIC/BICだけでなく、係数安定性、トレンド形状、残差診断、外部的妥当性を含めて判断する必要がある。
- fixed A では Prophet が強い。
- fixed B では SARIMAX/SSM が強い。
- SSMは全体として安定した候補であり、主分析モデルとして予測面でも一定の妥当性がある。
- 小標本月次データでは、深層学習系よりも、季節性、外生変数、状態空間構造を明示したモデルが有効である可能性がある。

## 15. 今後の課題

今後の課題は以下である。

- `covid_main` 期間感度分析を整理し、主分析仕様を確定する。
- 主分析モデルの残差診断をさらに確認する。
- rolling forecast を導入し、固定分割だけに依存しない評価を行う。
- autoformer_lite の fixed A を追加するか検討する。
- Prophet に `baseline_m4` regressors を加えた仕様を検討する。
- conditional forecast と unconditional forecast を分けた表を整備する。
- 論文用に採用する表・図を選定する。

## 報告時に強調する点

ゼミでは、予測評価だけを独立した結果として説明するのではなく、以下の流れで説明するのが自然である。

1. 旧統計と後続統計の定義差により、接続後の水準差を考慮する必要がある。
2. そのため、主分析モデルでは `post_stat_change` を含め、トレンド・季節性・イベント効果を分解する。
3. `covid_main` の期間設定は解釈に影響するため、感度分析で確認する。
4. そのうえで、接続済み系列に対して予測評価を行い、主分析モデルであるSSMが予測面でも一定の妥当性を持つか確認する。
5. 結果として、fixed AではProphet、fixed BではSARIMAX/SSMが強いが、情報条件の違いを明示して解釈する必要がある。
