# ゼミ報告用メモ: 系列接続・主分析・予測評価の整理

このメモは、宅配便取扱個数の月次系列について、これまでに行った研究作業をゼミで説明するために整理したものである。予測評価だけを単独で見るのではなく、旧統計と後続統計の接続、主分析モデル、`covid_main` 期間設定の感度分析を踏まえたうえで、最後に予測評価を位置づける。

参照した主な結果は、`output/forecasts/metrics/model_comparison_unconditional.csv`、`output/forecasts/metrics/model_comparison_conditional.csv`、`output/forecasts/metrics/model_comparison_fixed_b_conditional.csv`、`output/forecasts/metrics/model_comparison_best_by_split.csv` である。

## 1. 研究全体の目的

本研究の目的は、日本国内の宅配便取扱個数の月次系列を対象に、構造変化と予測性能を分析することである。

主分析では、状態空間モデルを用いて、宅配便取扱個数の変動をトレンド、季節性、イベント効果に分解する。特に、運賃改定、COVID-19、統計接続後の水準差といった要因が系列にどのように影響しているかを確認する。

予測評価は、主分析モデルであるSSMの妥当性を予測面から補助的に確認するための分析である。ただし、これはすべてのモデルを完全に同一条件で競わせる予測コンペではない。モデルの自然な使用条件に応じて、外生変数なしベンチマークと、外生変数あり・構造変化考慮モデルを分けて解釈する。

## 2. データ接続の背景

旧統計は、国土交通省「トラック輸送情報」に基づく宅配便取扱個数の系列である。この系列は大手14社ベースの月次データとして扱っている。

一方、後続統計は、国土交通省「国土交通月例経済」に基づく系列であり、大手3社ベースである。旧系列と後続系列では対象企業の範囲が異なるため、同じ「宅配便取扱個数」であっても水準が完全には一致しない。

重複して確認できる期間は 2022年5月から2022年7月であり、この期間では後続系列は旧系列のおよそ95〜96%程度の水準であった。したがって、単純に後続統計をつなぐだけでは、統計定義の変更による水準差が系列に混入する可能性がある。

このため、接続後の分析では `post_stat_change` のような水準変化ダミーを考慮する必要がある。

## 3. 接続済み系列の位置づけ

予測評価では、接続済みデータ `data/processed/parcel_volume_connected.csv` を使用している。

目的変数は `number_parcels` である。SARIMA、SARIMAX、SSM、Prophet、`autoformer_lite` など、モデルによっては学習時に `y = log(number_parcels)` を用いるが、予測後は原系列に戻し、評価はすべて `number_parcels` スケールで行っている。

評価スケールを原系列に統一することで、モデル間の RMSE、MAE、MAPE、MASE を同じ単位で比較できる。

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

接続済み系列とイベント仕様を整理したうえで、複数モデルの予測性能を同じ評価指標で確認した。

予測評価の目的は、主分析モデルであるSSMが、説明面だけでなく予測面でもどの程度妥当かを確認することである。また、期間や情報条件によって、単純な季節モデル、統計モデル、状態空間モデル、機械学習系モデルのどれが有効かを見る補助分析でもある。

ただし、予測評価は単純な全体順位で結論を出すものではない。外生変数を使わないモデルと、test期間のイベントダミーを既知として与えるモデルでは、予測の性質が異なる。そのため、現在の比較表では次の2系統に分けて結果を整理している。

1. 外生変数なしベンチマーク / unconditional forecast
2. 外生変数あり・構造変化考慮モデル / conditional forecast

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

## 8. 比較表の再設計

以前は、unconditional forecast と conditional forecast を1つの表に並べていた。しかし、外生ダミーを使わない予測と、test期間の外生ダミーを既知として与える予測では情報条件が異なるため、主比較では分けて考える方針にした。

外生変数なしベンチマークは、過去の系列のみ、または外生ダミーなしでどこまで予測できるかを見るための比較である。

| 区分 | モデル |
|---|---|
| unconditional forecast | naive |
| unconditional forecast | seasonal naive |
| unconditional forecast | SARIMA |
| unconditional forecast | Prophet without regressors |
| unconditional forecast | autoformer_lite |

外生変数あり・構造変化考慮モデルは、SSMと同じ `baseline_m4` の外生変数を使える条件で、構造変化を考慮するモデル同士を比較するための表である。

| 区分 | モデル |
|---|---|
| conditional forecast | SARIMAX |
| conditional forecast | SSM |
| conditional forecast | Prophet regressors |

conditional forecast では、test期間の `hike_dummy`, `covid_main`, `covid_wave1`, `covid_2021`, `post_stat_change` を既知として与えている。そのため、unconditional forecast と同じ主比較表で単純に順位づけるのではなく、別表で考察する。

## 9. 外生変数なしベンチマークの結果

外生変数なしベンチマークは、「外生情報を使わず、過去系列だけでどこまで予測できるか」を見るための比較である。

fixed A では Prophet without regressors が最良であった。

| split | best model | RMSE | MAPE | MASE |
|---|---|---:|---:|---:|
| fixed A | prophet | 27,498.77 | 6.25 | 2.24 |

fixed B では seasonal naive が最良であった。

| split | best model | RMSE | MAPE | MASE |
|---|---|---:|---:|---:|
| fixed B | seasonal_naive | 13,622.78 | 2.91 | 0.93 |

fixed A では、Prophet が外生変数なしでもCOVID期の予測で相対的に良い結果を示した。ただし、Prophet はCOVID要因を明示的に説明しているわけではないため、構造変化の解釈はSSMやSARIMAXのイベントダミー分析と分けて考える必要がある。

fixed B では、seasonal naive が最も良かった。直近期では前年同月パターンがかなり強く、外生情報を使わないベンチマークとしては seasonal naive が強い基準になる。

参考までに、fixed B の外生変数なしモデルの主な結果は以下である。

| model | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| seasonal_naive | 13,622.78 | 2.91 | 0.93 |
| sarima_grid_best | 14,790.76 | 3.07 | 0.98 |
| sarima_fixed | 16,686.68 | 3.50 | 1.12 |
| prophet | 26,730.00 | 4.83 | 1.59 |
| autoformer_lite | 35,587.39 | 8.54 | 2.59 |
| naive | 107,649.95 | 27.06 | 8.14 |

## 10. 外生変数あり・構造変化考慮モデルの結果

外生変数あり・構造変化考慮モデルでは、fixed B を中心に見る。これは、fixed B では `baseline_m4` の外生変数が学習期間内でも変動しており、SSM、SARIMAX、Prophet regressors を比較しやすいためである。

fixed B の conditional forecast では、SARIMAX grid best が最良であり、SSM conditional が僅差で2位だった。

| rank | model | RMSE | MAPE | MASE |
|---:|---|---:|---:|---:|
| 1 | sarimax_grid_best | 7,975.06 | 1.71 | 0.54 |
| 2 | ssm_conditional | 8,112.66 | 1.72 | 0.54 |
| 3 | sarimax_fixed | 8,196.97 | 1.76 | 0.55 |
| 4 | prophet_regressors | 17,877.06 | 3.20 | 1.04 |

SARIMAX grid best と SSM は非常に近い性能を示している。これは、構造変化ダミーを既知として与えられる条件では、季節性とイベント効果を明示的に扱うモデルが強いことを示している。

Prophet regressors は、外生変数なし Prophet より改善した。fixed B の Prophet without regressors は RMSE 26,730.00、MAPE 4.83、MASE 1.59 であったのに対し、Prophet regressors は RMSE 17,877.06、MAPE 3.20、MASE 1.04 まで改善した。

ただし、同じ conditional forecast の枠組みで見ると、Prophet regressors は SSM や SARIMAX には届かなかった。この結果から、単に外生ダミーを加えるだけではなく、季節性、トレンド、状態空間構造、あるいはSARIMAXの季節差分構造が予測性能に効いている可能性がある。

## 11. Prophet regressors の位置づけ

Prophet regressors は、SSM/SARIMAX と同じ `baseline_m4` 外生変数を使った conditional forecast である。

使用した外生変数は以下である。

- `hike_dummy`
- `covid_main`
- `covid_wave1`
- `covid_2021`
- `post_stat_change`

実装対象は fixed B のみである。fixed A では学習期間が 2019-12 までであり、`covid_main`, `covid_wave1`, `covid_2021`, `post_stat_change` が学習期間で変動しない。そのため、Prophet regressors は今回 fixed A の評価対象外とした。

Prophet regressors の意味は、Prophet にも SSM/SARIMAX と同じ外生情報を与えた場合にどこまで改善するかを確認することである。結果として、外生変数なし Prophet よりは明確に改善したが、SSM/SARIMAXには届かなかった。

このため、Prophet regressors は「Prophetに外生ダミーを入れればSSMと同等になるか」を確認するための補助比較として位置づける。

## 12. SSMの位置づけ

SSMは fixed A/B の両方で安定して良好な性能を示している。

| split | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| fixed A | 30,857.61 | 7.02 | 2.57 |
| fixed B | 8,112.66 | 1.72 | 0.54 |

以前は、SSM conditional と Prophet without regressors では情報条件が異なっていた。そのため、Prophetとの比較は「予測精度の参考」にはなっても、SSMの構造変化モデルとしての妥当性を直接支える比較としてはやや弱かった。

今回、Prophet regressors を追加したことで、同じ `baseline_m4` 外生情報を与えたモデル同士の比較が可能になった。fixed B では、同じ外生変数条件で見ても SSM は Prophet regressors より大きく良い。

この結果は、SSMが主分析モデルとして、説明面だけでなく予測面でも一定の妥当性を持つという主張をより自然にしている。ただし、SSMの予測は conditional forecast であり、test期間の外生ダミーを既知として与えている点は明示する必要がある。

## 13. Autoformer-liteの位置づけ

`autoformer_lite` は fixed B のみ実装した。これは厳密なAutoformerではなく、Autoformer-inspired / decomposition Transformer baseline である。

fixed B の結果は以下である。

| model | information_set | RMSE | MAPE | MASE |
|---|---|---:|---:|---:|
| autoformer_lite | unconditional | 35,587.39 | 8.54 | 2.59 |

`autoformer_lite` は naive よりは良いが、seasonal naive、SARIMA、Prophet、SARIMAX、SSMには劣る。月次287点程度の小標本では、深層学習系モデルは過学習しやすく、現段階では外生変数なしベンチマーク側の参考baselineとして扱うのが妥当である。

## 14. 暫定結論

ここまでの結果から、以下のように整理できる。

- 旧統計と後続統計には水準差があるため、接続後の水準変化を考慮する必要がある。
- `post_stat_change` は、後続統計接続後の水準差を扱ううえで重要である。
- `covid_main` の期間設定は主分析結果に影響するため、AIC/BICだけでなく、係数安定性、トレンド形状、残差診断、外部的妥当性を含めて判断する必要がある。
- 予測パートでは、全体順位よりも情報条件別の比較を重視する。
- 外生変数なしベンチマークでは、fixed A は Prophet、fixed B は seasonal naive が強い。
- 外生変数あり・構造変化考慮モデルでは、fixed B で SARIMAX grid best と SSM が強い。
- Prophet regressors は外生変数なし Prophet より改善するが、SSM/SARIMAXには届かない。
- SSMは、構造変化を明示的に扱う主分析モデルとして、予測面でも安定した候補である。
- 小標本月次データでは、深層学習系よりも、季節性、外生変数、状態空間構造を明示したモデルが有効である可能性がある。

## 15. 今後の課題

今後の課題は以下である。

- `covid_main` 期間感度分析を整理し、主分析仕様を確定する。
- 主分析モデルの残差診断をさらに確認する。
- rolling forecast を導入し、固定分割だけに依存しない評価を行う。
- Prophet regressors の fixed A は原則対象外、または慎重に扱う。
- `autoformer_lite` fixed A の必要性を検討する。
- conditional forecast と unconditional forecast を分けた表を論文用に整備する。
- 論文用に採用する表・図を選定する。
- ゼミ用スライドに落とし込む。

## 報告時に強調する点

ゼミでは、予測評価だけを独立した結果として説明するのではなく、以下の流れで説明するのが自然である。

1. 旧統計と後続統計の定義差により、接続後の水準差を考慮する必要がある。
2. そのため、主分析モデルでは `post_stat_change` を含め、トレンド・季節性・イベント効果を分解する。
3. `covid_main` の期間設定は解釈に影響するため、感度分析で確認する。
4. そのうえで、接続済み系列に対して予測評価を行い、主分析モデルであるSSMが予測面でも一定の妥当性を持つか確認する。
5. 予測評価では、unconditional forecast と conditional forecast を分けて解釈する。
6. fixed A の外生変数なしベンチマークでは Prophet、fixed B の外生変数なしベンチマークでは seasonal naive が強い。
7. fixed B の外生変数あり・構造変化考慮モデルでは SARIMAX/SSM が強く、Prophet regressors を追加したことで、SSMの予測面での妥当性をより自然に説明できる。
