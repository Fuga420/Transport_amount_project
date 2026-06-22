# ゼミ報告用メモ: 研究進捗と予測評価結果の整理

このメモは、日本国内の宅配便取扱個数の月次系列について、これまでに行った研究作業と予測評価結果をゼミで説明するために整理したものである。予測評価だけを単独で見るのではなく、旧統計・後続統計の接続、主分析モデル、`covid_main` 期間感度分析を踏まえたうえで、最後に予測評価を位置づける。

今回の重要な整理は、予測評価を「全モデルを完全に同一条件で競わせる予測コンペ」として扱わないことである。予測評価は、主分析モデルである状態空間モデル（SSM）の妥当性を、予測面から補助的に確認するための分析である。そのため、外生変数を使わないベンチマークと、外生変数を既知として与える構造変化考慮モデルを分けて解釈する。

## 1. 研究全体の目的

本研究の目的は、日本国内の宅配便取扱個数の月次系列を対象に、構造変化と予測性能を分析することである。

主分析では、状態空間モデルを用いて、宅配便取扱個数の変動をトレンド、季節性、イベント効果に分解する。特に、運賃改定、COVID-19、統計接続後の水準差といった要因が系列にどのような影響を与えているかを確認する。

予測評価は、主分析モデルであるSSMが、説明面だけでなく予測面でもどの程度妥当かを確認する補助分析である。単純な精度順位だけではなく、モデルが利用している情報条件を明確にしたうえで比較する。

## 2. データ接続の背景

旧統計は、国土交通省「トラック輸送情報」に基づく14社ベースの宅配便取扱個数の系列である。一方、後続統計は、国土交通省「国土交通月例経済」に基づく大手3社ベースの系列である。

両者は同じ「宅配便取扱個数」を対象としているが、対象企業の範囲が異なるため、水準は完全には一致しない。重複して確認できる2022年5月から2022年7月では、後続系列は旧系列のおよそ95から96%程度の水準であった。

したがって、後続統計を単純に接続すると、統計定義の違いによる水準差が系列に混入する可能性がある。このため、接続後の主分析では `post_stat_change` のような水準変化ダミーを考慮する必要がある。

## 3. 接続済み系列の位置づけ

予測評価では、接続済みデータ `data/processed/parcel_volume_connected.csv` を使用している。

目的変数は `number_parcels` である。SARIMA、SARIMAX、SSM、Prophet、Autoformer系モデルでは、学習時に `y = log(number_parcels)` を使う場合があるが、予測後は `exp()` で原系列に戻し、評価はすべて `number_parcels` スケールで行っている。

評価指標は、RMSE、MAE、MAPE、MASEである。評価スケールを原系列に統一することで、モデル間の予測誤差を同じ単位で比較できる。

## 4. 主分析モデルの位置づけ

主分析モデルは、local linear trend + seasonal + event dummies の状態空間モデルである。宅配便取扱個数の変動を、長期的な水準変化、季節性、イベント要因、観測誤差に分けて考える。

主なイベントダミーは以下である。

| 変数 | 意味 |
|---|---|
| `hike_dummy` | 運賃改定期の影響 |
| `covid_main` | COVID-19期の主な構造変化 |
| `covid_wave1` | COVID初期波の短期的影響 |
| `covid_2021` | 2021年のCOVID関連局面 |
| `post_stat_change` | 後続統計接続後の水準差 |

このうち `post_stat_change` は、単なるイベント効果というより、統計定義変更に伴う水準差を補正するための重要な変数である。

## 5. covid_main期間感度分析

`covid_main` はCOVID-19による主な構造変化を表す変数である。ただし、COVID期をどこまでとみなすかは自明ではない。

そのため、`covid_main` の終了時点を複数候補で変え、モデルの当てはまり、係数の安定性、`post_stat_change` の安定性、残差診断、トレンド形状を比較する感度分析を行った。

比較した候補は以下である。

| 仕様 | covid_main期間 |
|---|---|
| M1 | 2020-03から2021-12 |
| M2 | 2020-03から2022-03 |
| M2b | 2020-03から2022-06 |
| M3 | 2020-03から2022-12 |
| M4 | 2020-03から2023-05 |
| M5 | 2020-03以降ずっと |

この感度分析で重要なのは、AIC/BICだけで仕様を決めないことである。係数の符号や大きさが安定しているか、`post_stat_change` が不自然に吸収されていないか、トレンドに不自然な屈曲がないか、社会的に説明しやすい期間設定かを合わせて見る必要がある。

特にM5は、当てはまりが良くなる可能性がある一方で、`covid_main` を恒久的な水準変化として解釈してしまうリスクがある。そのため、主分析仕様は統計的当てはまりだけでなく、解釈可能性を重視して決める必要がある。

## 6. 予測評価の位置づけ

予測評価は、接続済み系列とイベント仕様を踏まえたうえで、複数モデルの予測性能を同一の評価指標で確認するために行った。

ただし、今回の予測評価は、すべてのモデルを完全に同一条件で競わせるものではない。モデルによって、外生変数を使わないものと、test期間のイベントダミーを既知として与えるものがあるためである。

そこで、比較を以下の2系統に分けて整理した。

1. 外生変数なしベンチマーク / unconditional forecast
2. 外生変数あり・構造変化考慮モデル / conditional forecast

この分け方により、「過去系列だけでどこまで予測できるか」と、「構造変化ダミーを既知として与えた場合に、主分析モデルがどの程度妥当か」を分けて考えられる。

## 7. 予測評価設計

評価は固定分割で行った。

| split | 学習期間 | 評価期間 | 意味 |
|---|---|---|---|
| fixed A | 2002-04から2019-12 | 2020-01から2021-12 | COVID期を含む予測 |
| fixed B | 2002-04から2023-12 | 2024-01から2026-02 | 後続統計接続後を含む直近期予測 |

評価指標はRMSE、MAE、MAPE、MASEである。評価はすべて `number_parcels` の原系列スケールで行っている。

## 8. 比較表の再設計

以前は、unconditional forecast と conditional forecast を1つのランキング表に並べていた。しかし、外生ダミーを使わない予測と、test期間の外生ダミーを既知として与える予測では、情報条件が異なる。

そのため、主比較では以下の2系統に分けて整理する方針に変更した。

### 外生変数なしベンチマーク

この比較は、外生情報を使わず、過去系列だけでどこまで予測できるかを見るためのものである。

| 区分 | モデル |
|---|---|
| unconditional | naive |
| unconditional | seasonal_naive |
| unconditional | SARIMA |
| unconditional | Prophet without regressors |
| unconditional | autoformer_lite |
| unconditional | autoformer_neuralforecast_grid_best |

### 外生変数あり・構造変化考慮モデル

この比較は、SSMと同じ `baseline_m4` の外生変数を使える条件で、構造変化を考慮するモデル同士を比較するものである。

| 区分 | モデル |
|---|---|
| conditional | SARIMAX |
| conditional | SSM |
| conditional | Prophet regressors |
| conditional | autoformer_neuralforecast_exog |

conditional forecastでは、test期間の `hike_dummy`, `covid_main`, `covid_wave1`, `covid_2021`, `post_stat_change` を既知として与えている。そのため、unconditional forecastと単純に同じランキングで比較しない。

## 9. 外生変数なしベンチマークの結果

外生変数なしベンチマークでは、fixed AはProphet without regressorsが最良であった。

| split | best model | RMSE | MAPE | MASE |
|---|---|---:|---:|---:|
| fixed A | prophet | 27,498.77 | 6.25 | 2.24 |

fixed AはCOVID期を予測する期間であり、Prophetは外生変数なしでも比較的良い結果を示した。ただし、ProphetはCOVID要因を明示的に説明しているわけではない。そのため、構造変化の解釈はSSMやSARIMAXのイベントダミー分析と分けて考える必要がある。

fixed Bでは、seasonal naiveが最良であった。

| model | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| seasonal_naive | 13,622.78 | 2.91 | 0.93 |
| autoformer_neuralforecast_grid_best | 21,538.48 | 4.61 | 1.41 |
| prophet | 26,730.00 | 4.83 | 1.59 |
| autoformer_lite | 35,587.39 | 8.54 | 2.59 |

fixed Bでは、直近期の前年同月パターンがかなり強く、外生変数なしベンチマークとしてはseasonal naiveが強い基準になっている。Autoformer NeuralForecastの小規模グリッド探索bestは、Prophetやautoformer_liteを上回ったが、seasonal naiveには届かなかった。

## 10. 外生変数あり・構造変化考慮モデルの結果

外生変数あり・構造変化考慮モデルでは、fixed Bを中心に見る。fixed Bでは `baseline_m4` の外生変数が学習期間内でも変動しており、SSM、SARIMAX、Prophet regressors、Autoformer NeuralForecast exogを比較しやすい。

fixed Bのconditional forecastでは、SARIMAX grid bestが最良で、SSM conditionalが僅差で2位であった。

| rank | model | RMSE | MAPE | MASE |
|---:|---|---:|---:|---:|
| 1 | sarimax_grid_best | 7,975.06 | 1.71 | 0.54 |
| 2 | ssm_conditional | 8,112.66 | 1.72 | 0.54 |
| 3 | prophet_regressors | 17,877.06 | 3.20 | 1.04 |
| 4 | autoformer_neuralforecast_exog | 23,967.15 | 4.95 | 1.60 |

SARIMAX grid bestとSSMは非常に近い性能であり、どちらもProphet regressorsやAutoformer NeuralForecast exogを大きく上回った。この結果は、季節性、構造変化ダミー、時系列構造を明示的に扱うモデルが、fixed Bの予測で有効である可能性を示している。

Prophet regressorsは、外生変数なしProphetより改善した。fixed BのProphet without regressorsはRMSE 26,730.00、MAPE 4.83、MASE 1.59であったのに対し、Prophet regressorsはRMSE 17,877.06、MAPE 3.20、MASE 1.04まで改善した。ただし、SSMやSARIMAXには届かなかった。

Autoformer NeuralForecast exogは、外生変数なしgrid bestより悪化した。外生変数なしgrid bestはRMSE 21,538.48、MAPE 4.61、MASE 1.41であったのに対し、exog版はRMSE 23,967.15、MAPE 4.95、MASE 1.60であった。小標本月次データでは、外生変数を与えても深層学習系モデルが安定して改善するとは限らない。

## 11. Prophet regressors の位置づけ

Prophet regressorsは、SSM/SARIMAXと同じ `baseline_m4` 外生変数を使ったconditional forecastである。

使用した外生変数は以下である。

- `hike_dummy`
- `covid_main`
- `covid_wave1`
- `covid_2021`
- `post_stat_change`

Prophet regressorsはfixed Bのみ実装している。fixed Aでは学習期間が2019-12までであり、COVID系ダミーや `post_stat_change` が学習期間内で変動しない。そのため、今回のProphet regressorsはfixed Aの評価対象外とした。

Prophet regressorsの意義は、ProphetにもSSM/SARIMAXと同じ外生情報を与えた場合に、どこまで改善するかを確認することである。結果として、外生変数なしProphetよりは明確に改善したが、SSM/SARIMAXには届かなかった。

## 12. SSMの位置づけ

SSMは、主分析モデルとして、説明面だけでなく予測面でも一定の妥当性を示している。

fixed Bのconditional forecastでは、SSMはRMSE 8,112.66、MAPE 1.72、MASE 0.54であり、SARIMAX grid bestに僅差で次ぐ結果であった。同じ `baseline_m4` 外生変数を使ったProphet regressorsやAutoformer NeuralForecast exogよりも大きく良い。

以前は、SSM conditionalとProphet without regressorsでは情報条件が異なっていたため、比較の意味がやや弱かった。今回、Prophet regressorsとAutoformer NeuralForecast exogを追加したことで、同じ外生変数条件での比較が可能になった。そのうえでもSSMが良好であるため、主分析モデルとしてのSSMは、構造変化を明示的に扱うモデルとして予測面でも安定していると整理できる。

ただし、SSMの予測はconditional forecastであり、test期間の外生ダミーを既知として与えている。この点は、seasonal naiveやProphet without regressorsなどのunconditional forecastと比較するときに明示する必要がある。

## 13. Autoformer系モデルの整理

Autoformer系は、深層学習系の参考baselineとして扱う。

`autoformer_lite` は、自前実装の Autoformer-inspired / decomposition Transformer baseline であり、厳密なAutoformer本体ではない。fixed Bのみ実装しており、外生変数は使っていない。結果はRMSE 35,587.39、MAPE 8.54、MASE 2.59で、naiveよりは良いが、seasonal naive、SARIMA、Prophet、SSM、SARIMAXには劣った。

`autoformer_neuralforecast_grid_best` は、既存ライブラリであるNeuralForecastのAutoformerを用いた小規模グリッド探索bestである。fixed Bのみの外生変数なしベンチマークであり、RMSE 21,538.48、MAPE 4.61、MASE 1.41であった。固定設定版やautoformer_liteより改善し、Prophet without regressorsも上回ったが、seasonal naiveには届かなかった。

`autoformer_neuralforecast_exog` は、NeuralForecast Autoformerに `baseline_m4` のfuture exogenous variablesを与えたconditional forecastである。結果はRMSE 23,967.15、MAPE 4.95、MASE 1.60であり、外生変数なしgrid bestより悪化した。また、Prophet regressors、SSM、SARIMAXには届かなかった。

月次287点程度の小標本では、深層学習系モデルは過学習しやすく、設定に対する感度も大きい。現段階では、Autoformer系は主分析モデルではなく、発展的な参考baselineとして扱うのが妥当である。

## 14. Plotly診断HTML

評価指標だけでは予測のズレ方が分かりにくいため、Plotlyによる補足診断HTMLを作成している。これにより、全期間の実測値と、各モデルのtest期間予測をズーム・パンしながら確認できる。

作成済みのHTMLは以下である。

| HTML | 内容 |
|---|---|
| `output/forecasts/html/fixed_a_unconditional_forecasts.html` | fixed Aの外生変数なし予測 |
| `output/forecasts/html/fixed_b_unconditional_forecasts.html` | fixed Bの外生変数なし予測 |
| `output/forecasts/html/fixed_b_conditional_forecasts.html` | fixed Bの外生変数あり予測 |

fixed B unconditionalのHTMLには、`autoformer_neuralforecast_grid_best` を追加済みである。fixed B conditionalのHTMLには、`autoformer_neuralforecast_exog` を追加済みである。

ただし、SARIMA/SARIMAXについては、grid bestの予測CSVが保存されていない。そのため、Plotly診断では評価表で扱うgrid bestではなく、保存済み予測CSVのあるfixed仕様の予測線を表示している。この点は、図を見るときに注意が必要である。

## 15. 暫定結論

ここまでの結果は、以下のように整理できる。

- 旧統計と後続統計には水準差があるため、接続後の水準変化を考慮する必要がある。
- `post_stat_change` は、後続統計接続後の水準差を扱ううえで重要である。
- `covid_main` の期間設定は主分析結果に影響するため、AIC/BICだけでなく、係数安定性、トレンド形状、残差診断、外部妥当性を含めて判断する必要がある。
- 予測評価では、全体順位よりも情報条件別の比較を重視する。
- 外生変数なしベンチマークでは、fixed AはProphet、fixed Bはseasonal naiveが強い。
- fixed Bの外生変数なしベンチマークでは、Autoformer NeuralForecast grid bestはProphetやautoformer_liteを上回ったが、seasonal naiveには届かなかった。
- 外生変数あり・構造変化考慮モデルでは、fixed BでSARIMAX grid bestとSSMが強い。
- Prophet regressorsは外生変数なしProphetより改善するが、SSM/SARIMAXには届かない。
- Autoformer NeuralForecast exogは外生変数なしgrid bestより悪化し、SSM/SARIMAX/Prophet regressorsには届かなかった。
- SSMは、構造変化を明示的に扱う主分析モデルとして、予測面でも一定の妥当性がある。
- 小標本月次データでは、深層学習系よりも、季節性・外生変数・状態空間構造を明示したモデルが有効である可能性がある。

## 16. 今後の課題

今後の課題は以下である。

- `covid_main` 期間感度分析を整理し、主分析仕様を確定する。
- 主分析モデルの残差診断をさらに確認する。
- rolling forecastを導入し、固定分割だけに依存しない評価を行う。
- 予測評価で論文に載せる表・図を選定する。
- Plotly診断HTMLをゼミ報告時の補足資料として活用する。
- ゼミ用スライドに、データ接続、主分析、感度分析、予測評価の流れを落とし込む。

## ゼミ報告時に強調する点

ゼミでは、予測評価を独立した精度競争として説明するのではなく、以下の流れで説明すると自然である。

1. 旧統計と後続統計には定義差があり、接続後の水準差を考慮する必要がある。
2. 主分析モデルでは `post_stat_change` を含め、トレンド・季節性・イベント効果を分解する。
3. `covid_main` の期間設定は解釈に影響するため、感度分析で確認する。
4. そのうえで、接続済み系列に対して予測評価を行い、主分析モデルであるSSMが予測面でも一定の妥当性を持つか確認する。
5. 予測評価では、unconditional forecast と conditional forecast を分けて解釈する。
6. fixed Bのconditional forecastでは、SARIMAX grid bestとSSMが強く、SSMの主分析モデルとしての位置づけを補助的に支持している。
