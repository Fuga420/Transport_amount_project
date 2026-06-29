# 予測評価の設計と結果解釈メモ

このメモは、ゼミで予測評価パートを説明するための整理である。予測評価は、全モデルを完全に同一条件で競わせる予測コンペではなく、主分析モデルである状態空間モデル（SSM）の妥当性を予測面から補助的に確認するために行った。

## 1. 予測評価の目的

本研究の主分析は、日本国内の宅配便取扱個数の月次系列について、トレンド、季節性、イベント効果、統計接続後の水準差を状態空間モデルで分解することである。

予測評価は、この主分析モデルが説明面だけでなく、予測面でも一定の妥当性を持つかを確認する補助分析として位置づける。したがって、単純な精度順位だけで結論を出すのではなく、各モデルが利用している情報条件を分けて解釈する。

評価対象のデータは、接続済み系列 `data/processed/parcel_volume_connected.csv` である。評価はすべて原系列の `number_parcels` スケールで行う。SARIMA、SARIMAX、SSM、Prophet、Autoformer系では学習時に `y = log(number_parcels)` を使う場合があるが、予測後に `exp()` で原系列へ戻して評価している。

## 2. fixed A / fixed B の意味

予測評価では、固定分割を2つ設定している。

| split | train | test | 主な意味 |
|---|---|---|---|
| fixed A | 2002-04 から 2019-12 | 2020-01 から 2021-12 | COVID期を予測する設定。学習期間はCOVID前で終わる。 |
| fixed B | 2002-04 から 2023-12 | 2024-01 から 2026-02 | 後続統計接続後を含む直近期の予測設定。 |

fixed Aは、COVID期の急な変化をどの程度予測できるかを見る設定である。ただし、COVID関連ダミーや `post_stat_change` は学習期間で変動しないため、外生変数ありモデルの解釈には注意が必要である。

fixed Bは、後続統計接続後の期間を含めた直近期の予測評価である。主分析で扱う `post_stat_change` やCOVID後の構造変化を踏まえたモデルの比較に向いている。

## 3. unconditional / conditional forecast の違い

予測評価では、以下の2系統を分けている。

### unconditional forecast

外生ダミーを使わず、過去の系列情報だけ、または外生変数なしのモデル構造で予測する。

対象モデル:

- `naive`
- `seasonal_naive`
- `sarima_fixed`
- `sarima_grid_best`
- `prophet`
- `autoformer_lite`
- `autoformer_neuralforecast_grid_best`

この比較は、「外生情報を使わず、過去系列だけでどこまで予測できるか」を見るためのベンチマークである。

### conditional forecast

test期間の外生ダミーを既知として与える予測である。ここで使う外生変数は、主分析の `baseline_m4` と同じである。

- `hike_dummy`
- `covid_main`
- `covid_wave1`
- `covid_2021`
- `post_stat_change`

対象モデル:

- `sarimax_fixed`
- `sarimax_grid_best`
- `ssm_conditional`
- `prophet_regressors`
- `autoformer_neuralforecast_exog`

conditional forecastは、予測期間にどのイベント・構造変化ダミーが立つかを既知として与えている。そのため、unconditional forecastと同じランキング表で単純比較するのは適切ではない。ゼミでは、unconditionalとconditionalを分けて説明する。

## 4. 各モデルの構造と役割

| model | 区分 | 役割 |
|---|---|---|
| `naive` | unconditional | 直前値をそのまま使う最小ベンチマーク。 |
| `seasonal_naive` | unconditional | 前年同月を使う月次季節ベンチマーク。 |
| `SARIMA` | unconditional | 自己相関と季節性を明示的に使う時系列ベースライン。 |
| `SARIMAX` | conditional | SARIMAに外生ダミーを加え、構造変化を条件付きで扱うモデル。 |
| `SSM` | conditional | 主分析モデル。local linear trend、seasonal、event dummiesを状態空間で扱う。 |
| `Prophet` | unconditional | 外生変数なしのトレンド・季節性モデル。 |
| `Prophet regressors` | conditional | Prophetに `baseline_m4` の外生変数を加えた条件付き予測。 |
| `autoformer_lite` | unconditional | 自前のAutoformer-inspired / decomposition Transformer baseline。厳密なAutoformerではない。 |
| `autoformer_neuralforecast_grid_best` | unconditional | NeuralForecast Autoformerの小規模グリッド探索best。参考baseline。 |
| `autoformer_neuralforecast_exog` | conditional | NeuralForecast Autoformerに `baseline_m4` 外生変数を与えた参考baseline。 |

Autoformer系は主分析モデルではなく、深層学習系の参考baselineとして扱う。月次データは約287点程度の小標本であり、深層学習モデルが安定して優位になる設定ではない。

## 5. 評価指標の意味

| 指標 | 意味 | 読み方 |
|---|---|---|
| RMSE | 二乗誤差平均の平方根。大きな外れを重く見る。 | 小さいほど良い。 |
| MAE | 絶対誤差平均。平均的なズレを見る。 | 小さいほど良い。 |
| MAPE | 実測値に対する相対誤差率。 | 小さいほど良い。単位は割合。 |
| MASE | seasonal naiveなどの基準誤差で標準化した誤差。 | 1未満なら基準より良い目安。 |

本研究では、RMSEだけでなく、MAPEとMASEも合わせて確認する。特に月次系列では季節性が強いため、seasonal naiveを基準にしたMASEが有用である。

## 6. 主要結果

### fixed A: unconditional forecast

`output/forecasts/metrics/model_comparison_unconditional.csv` に基づくと、fixed Aのunconditionalでは `prophet` が最良だった。

| model | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| `prophet` | 27498.77 | 6.25 | 2.24 |
| `sarima_grid_best` | 40578.64 | 9.59 | 3.53 |
| `sarima_fixed` | 41548.02 | 9.84 | 3.62 |
| `seasonal_naive` | 44753.89 | 10.34 | 3.83 |
| `naive` | 80656.77 | 20.09 | 6.98 |

fixed AはCOVID期を予測する設定である。Prophetは外生変数なしでも比較的良い結果を示したが、COVID要因を明示的に説明しているわけではない。そのため、この結果は「外生変数なしでもトレンド・季節構造から一定の予測ができた」という位置づけに留める。

### fixed B: unconditional forecast

fixed Bのunconditionalでは `seasonal_naive` が最良だった。

| model | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| `seasonal_naive` | 13622.78 | 2.91 | 0.93 |
| `sarima_grid_best` | 14790.76 | 3.07 | 0.98 |
| `sarima_fixed` | 16686.68 | 3.50 | 1.12 |
| `autoformer_neuralforecast_grid_best` | 21538.48 | 4.61 | 1.41 |
| `prophet` | 26730.00 | 4.83 | 1.59 |
| `autoformer_lite` | 35587.39 | 8.54 | 2.59 |
| `naive` | 107649.95 | 27.06 | 8.14 |

直近期のfixed Bでは、前年同月を使うseasonal naiveが非常に強い。これは、直近期の月次パターンが前年同月に近いことを示唆する。

Autoformer NeuralForecastのgrid bestは、`autoformer_lite` や外生変数なしProphetより良かったが、seasonal naiveには届かなかった。深層学習系モデルは参考baselineとして扱うのが妥当である。

### fixed B: conditional forecast

fixed Bのconditionalでは、`sarimax_grid_best` が最良で、`ssm_conditional` が僅差で2位だった。

| model | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| `sarimax_grid_best` | 7975.06 | 1.71 | 0.54 |
| `ssm_conditional` | 8112.66 | 1.72 | 0.54 |
| `sarimax_fixed` | 8196.97 | 1.76 | 0.55 |
| `prophet_regressors` | 17877.06 | 3.20 | 1.04 |
| `autoformer_neuralforecast_exog` | 23967.15 | 4.95 | 1.60 |

conditional forecastでは、test期間の外生ダミーを既知として与えている。この条件では、SARIMAXとSSMが強い。特にSSMは、主分析モデルとしてイベント効果や統計接続後の水準差を明示的に扱っており、予測面でもSARIMAX grid bestに近い性能を示している。

Prophet regressorsは、外生変数なしProphetより改善したが、SSM/SARIMAXには届かなかった。Autoformer NeuralForecast exogは、外生変数なしのgrid bestより悪化し、conditionalモデルの中では弱い結果だった。

## 7. Plotly診断で見るポイント

補足資料として、以下のPlotly HTMLを作成済みである。

- `output/forecasts/html/fixed_a_unconditional_forecasts.html`
- `output/forecasts/html/fixed_b_unconditional_forecasts.html`
- `output/forecasts/html/fixed_b_conditional_forecasts.html`

Plotly図では、全期間の実測値を表示し、予測線はtest期間に限定して重ねている。凡例でモデルを表示・非表示にでき、ズームして予測期間のズレを確認できる。

見るポイントは以下。

- 実測値の季節ピークや谷を、各モデルがどの程度追えているか。
- fixed Bでseasonal naiveが強い理由として、前年同月パターンが効いているか。
- conditionalモデルでSARIMAX/SSMが実測値に近い動きをしているか。
- Prophet regressorsやAutoformer exogが、外生変数を入れてもどの時点でズレるか。
- Autoformer系の予測線が、月次小標本に対して過度に滑らか、または不安定になっていないか。

注意点として、SARIMA/SARIMAXについてはgrid bestの予測CSVが保存されていない場合がある。その場合、Plotly診断では保存済み予測CSVのあるfixed仕様を表示している。評価表のgrid best順位と、Plotly上のSARIMA/SARIMAX予測線は完全には対応しない場合がある。

## 8. Autoformerの実装と位置づけ

Autoformer系は2種類を扱った。

1. `autoformer_lite`
   - 自前実装のAutoformer-inspired / decomposition Transformer baseline。
   - 厳密なAutoformer本体ではない。
   - fixed Bのみ実装。

2. `autoformer_neuralforecast_grid_best` / `autoformer_neuralforecast_exog`
   - NeuralForecastのAutoformerを用いた既存ライブラリ版。
   - 外生変数なし版は小規模グリッド探索を実施し、fixed Bのbestを採用。
   - 外生変数あり版は `baseline_m4` の外生変数をfuture exogenous variablesとして与えた。

結果として、NeuralForecast版Autoformerのgrid bestは、`autoformer_lite` やProphet without regressorsより改善したが、seasonal naiveには届かなかった。外生変数あり版は、外生変数なしgrid bestより悪化し、Prophet regressors、SSM、SARIMAXにも届かなかった。

したがって、Autoformer系は本研究の主分析モデルではなく、小標本月次データに対する参考baselineとして整理する。

## 9. fixed slope SSMの予測比較結果

固定傾きSSMは、総合比較表に混ぜるのではなく、SSM内部の頑健性確認として扱う。

背景として、現行SSMの傾きノイズがほぼ0に推定されていたため、傾きノイズを推定しない固定傾き仕様を補助的に検討した。固定傾き仕様では、slope disturbanceをselection matrixから外し、傾きノイズを0固定として扱った。

モデリング比較では、`fixed_slope_m4` は `baseline_m4` よりAIC/BICが改善した。

| model_id | AIC | BIC |
|---|---:|---:|
| `baseline_m4` | -1124.14 | -1043.63 |
| `fixed_slope_m4` | -1126.14 | -1049.29 |

fixed B conditional forecastで既存SSMと比較した結果は以下。

| model | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| `ssm_conditional` | 8112.66 | 1.7185 | 0.5402 |
| `ssm_fixed_slope` | 8135.05 | 1.7110 | 0.5380 |

RMSEは固定傾きSSMがごくわずかに悪化したが、MAPE/MASEはわずかに改善した。予測線もほぼ重なっており、予測面では既存SSMとほぼ同等である。

この結果は、固定傾き仕様が主仕様候補として検討可能であることを示す。ただし、現時点では総合比較表に混ぜず、査読対応用の補助分析・頑健性確認として扱うのが安全である。

## 10. ゼミでの説明用要約

ゼミでは、以下の順番で説明すると自然である。

1. 予測評価は、主分析SSMの補助検証であり、単純な予測コンペではない。
2. 評価はfixed Aとfixed Bに分けた。fixed AはCOVID期、fixed Bは直近期を対象にしている。
3. モデルはunconditionalとconditionalに分けて解釈する。conditionalでは予測期間の外生ダミーを既知として与えている。
4. fixed AのunconditionalではProphetが最良だった。
5. fixed Bのunconditionalではseasonal naiveが最良だった。
6. fixed BのconditionalではSARIMAX grid bestが最良で、SSMが僅差で2位だった。
7. SSMは主分析モデルとして、説明面だけでなく予測面でも一定の妥当性がある。
8. Autoformer系は参考baselineであり、小標本月次データではseasonal naiveやSSM/SARIMAXを上回らなかった。
9. fixed slope SSMは、総合比較表に入れるものではなく、SSM内部の頑健性確認である。既存SSMと予測性能はほぼ同等だった。

結論として、予測評価からは「外生変数なしではseasonal naiveが強い場面がある一方、構造変化ダミーを既知として与えた条件ではSARIMAX/SSMが強い」と整理できる。主分析SSMは、構造変化を明示的に扱うモデルとして、予測面でも十分に妥当な候補である。
