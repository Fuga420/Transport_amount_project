# Autoformer NeuralForecast 実装監査メモ

作成日: 2026-06-25

このメモは、NeuralForecast Autoformer 実装について、ゼミで質問されたときに説明できるように、現在のリポジトリ上のコードと既存出力CSVに基づいて整理したものである。新しい再学習・再推定は行っていない。

## 1. 確認対象

主に以下を確認した。

- `src/forecasting/autoformer_neuralforecast.py`
- `notebooks/forecasting/09_autoformer_neuralforecast.ipynb`
- `output/forecasts/metrics/autoformer_neuralforecast_best_model.csv`
- `output/forecasts/metrics/autoformer_neuralforecast_grid_search.csv`
- `output/forecasts/metrics/autoformer_neuralforecast_best_metrics.csv`
- `output/forecasts/metrics/autoformer_neuralforecast_exog_metrics.csv`
- `output/forecasts/predictions/fixed_b_autoformer_neuralforecast_best.csv`
- `output/forecasts/predictions/fixed_b_autoformer_neuralforecast_exog.csv`

## 2. 使用ライブラリ・クラス

実装は、Nixtla の `neuralforecast` ライブラリを用いている。

コード上で確認できる主なクラス・関数は以下である。

| 用途 | ライブラリ・クラス |
|---|---|
| 予測フレームワーク | `neuralforecast.NeuralForecast` |
| モデル | `neuralforecast.models.Autoformer` |
| 損失関数 | `neuralforecast.losses.pytorch.MAE` |
| 学習基盤 | `pytorch_lightning` |
| テンソル計算 | `torch` |

`autoformer_neuralforecast.py` では、`ray` が未導入でも固定パラメータのAutoformer実行に必要なimportが通るように、最小限のray stubを入れている。出力CSVでは `version_ray_stub_used=True` が記録されている。

確認されたバージョンは以下である。

| item | version |
|---|---|
| neuralforecast | 3.1.9 |
| pytorch_lightning | 2.5.6 |
| torch | 2.12.1+cpu |
| ray stub | True |

## 3. 入力データ形式

元データは `data/processed/parcel_volume_connected.csv` である。確認時点で、期間は2002-04-01から2026-02-01、行数は287であった。

NeuralForecast用には、以下の形式に変換している。

| 列 | 内容 |
|---|---|
| `unique_id` | `"parcel_volume"` |
| `ds` | 月初日付 |
| `y` | log scale の目的変数 |

変換は `prepare_neuralforecast_frame()` で行っている。元データに `date` 列、`label` 列、または `DatetimeIndex` があれば月初日付のDatetimeIndexにそろえたうえで、NeuralForecast形式へ変換する。

外生変数あり版では、`prepare_neuralforecast_frame_with_exog()` により、`unique_id`, `ds`, `y` に加えて外生変数列を追加している。予測時のfuture dataframeでは `include_y=False` とし、test期間の外生変数を `futr_df` として渡している。

## 4. 目的変数のスケール変換

学習対象は `y = log(number_parcels)` である。

予測後は、NeuralForecastが出力したlog scaleの予測値に `np.exp()` を適用し、`number_parcels` の原系列スケールに戻している。

評価指標は原系列スケールで計算している。予測CSVでも以下の列が確認できる。

| 列 | 内容 |
|---|---|
| `y_true` | 実測の `number_parcels` |
| `y_pred` | `exp(log forecast)` 後の予測値 |
| `target_col` | `number_parcels` |
| `target_scale` | `original` |

## 5. fixed B の train/test 期間

Notebookと既存split仕様から、fixed Bは以下である。

| 区分 | 期間 |
|---|---|
| train | 2002-04-01 から 2023-12-01 |
| test | 2024-01-01 から 2026-02-01 |
| horizon | 26か月 |
| cutoff | 2023-12-01 |

予測CSVでも、`date` は2024-01-01から始まり、`cutoff` は2023-12-01、`horizon` は1から26であることを確認した。

## 6. 外生変数なし版と外生変数あり版の違い

### 外生変数なし版

外生変数なし版は、以下の位置づけである。

| 項目 | 内容 |
|---|---|
| model | `autoformer_neuralforecast` |
| forecast_type | `unconditional` |
| information_set | `unconditional` |
| spec_name | `neuralforecast_autoformer_grid` |
| 入力 | log系列 `y` のみ |
| 予測CSV | `fixed_b_autoformer_neuralforecast_best.csv` |

小規模グリッド探索のbest configを使った予測である。外生変数は使っていないため、seasonal naive、SARIMA、Prophet without regressors、autoformer_liteと同じ「外生情報なしベンチマーク」側に置く。

### 外生変数あり版

外生変数あり版は、以下の位置づけである。

| 項目 | 内容 |
|---|---|
| model | `autoformer_neuralforecast_exog` |
| forecast_type | `conditional` |
| information_set | `conditional_exog_known` |
| spec_name | `neuralforecast_autoformer_exog_baseline_m4` |
| 入力 | log系列 `y` + `baseline_m4` future exogenous variables |
| 予測CSV | `fixed_b_autoformer_neuralforecast_exog.csv` |

NeuralForecast Autoformerの `futr_exog_list` に外生変数列を指定し、test期間の外生変数を既知として `futr_df` に渡している。したがって、unconditional forecastとは情報条件が異なる。

## 7. 使用した外生変数

外生変数は、`forecast_specs.py` の `baseline_m4` に基づいて作成している。`prepare_autoformer_exog_from_spec()` が `get_forecast_spec("baseline_m4")` を読み、`add_period_dummies()` で期間ダミーを作る。

fit summaryで確認された使用外生変数は以下である。

| 変数 | 期間 |
|---|---|
| `hike_dummy` | 2017-10-01 から 2019-12-01 |
| `covid_main` | 2020-03-01 から 2023-05-01 |
| `covid_wave1` | 2020-04-01 から 2020-05-01 |
| `covid_2021` | 2021-01-01 から 2021-09-01 |
| `post_stat_change` | 2022-08-01 以降 |

`autoformer_neuralforecast_exog_fit_summary.csv` では、実際に使われた列として以下が記録されている。

```text
hike_dummy,covid_main,covid_wave1,covid_2021,post_stat_change
```

## 8. グリッド探索で試したハイパーパラメータ

グリッド探索はfixed B、外生変数なし、unconditional forecastとして実行されている。`autoformer_neuralforecast_grid_search.csv` では12 configすべてが `status=success` であった。

固定された設定は以下である。

| parameter | value |
|---|---:|
| `n_head` | 2 |
| `encoder_layers` | 1 |
| `decoder_layers` | 1 |
| `moving_avg_window` | 13 |
| `random_seed` | 42 |

探索した設定と結果は以下である。表はRMSEの昇順である。

| config_id | input_size | hidden_size | max_steps | conv_hidden_size | RMSE | MAE | MAPE | MASE | status |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 8 | 24 | 32 | 200 | 32 | 21,538.48 | 17,628.14 | 4.61 | 1.41 | success |
| 7 | 24 | 32 | 100 | 32 | 24,499.13 | 20,538.44 | 5.33 | 1.64 | success |
| 10 | 36 | 16 | 200 | 16 | 29,776.91 | 25,738.93 | 6.76 | 2.06 | success |
| 9 | 36 | 16 | 100 | 16 | 31,034.89 | 26,192.46 | 6.88 | 2.09 | success |
| 11 | 36 | 32 | 100 | 32 | 32,781.94 | 25,466.48 | 6.75 | 2.04 | success |
| 5 | 24 | 16 | 100 | 16 | 32,929.37 | 24,639.60 | 6.26 | 1.97 | success |
| 6 | 24 | 16 | 200 | 16 | 32,929.37 | 24,639.60 | 6.26 | 1.97 | success |
| 12 | 36 | 32 | 200 | 32 | 33,025.81 | 25,416.67 | 6.75 | 2.03 | success |
| 3 | 12 | 32 | 100 | 32 | 34,462.90 | 24,094.16 | 5.86 | 1.93 | success |
| 4 | 12 | 32 | 200 | 32 | 34,462.90 | 24,094.16 | 5.86 | 1.93 | success |
| 1 | 12 | 16 | 100 | 16 | 39,327.72 | 28,565.42 | 6.99 | 2.28 | success |
| 2 | 12 | 16 | 200 | 16 | 39,327.72 | 28,565.42 | 6.99 | 2.28 | success |

## 9. best config

グリッド探索のbest configは以下である。

| 項目 | 値 |
|---|---:|
| config_id | 8 |
| input_size | 24 |
| hidden_size | 32 |
| max_steps | 200 |
| n_head | 2 |
| encoder_layers | 1 |
| decoder_layers | 1 |
| conv_hidden_size | 32 |
| moving_avg_window | 13 |
| random_seed | 42 |
| training_time_seconds | 6.39 |
| total_time_seconds | 6.46 |
| status | success |

出力CSVに記録されたbest configの評価値は以下である。

| model | RMSE | MAE | MAPE | MASE |
|---|---:|---:|---:|---:|
| `autoformer_neuralforecast_grid_best` | 21,538.48 | 17,628.14 | 4.61 | 1.41 |

## 10. 外生変数あり版の評価指標

外生変数あり版の評価値は以下である。

| model | forecast_type | RMSE | MAE | MAPE | MASE |
|---|---|---:|---:|---:|---:|
| `autoformer_neuralforecast_exog` | conditional | 23,967.15 | 19,986.70 | 4.95 | 1.60 |

外生変数あり版は、外生変数なしgrid bestより悪化している。

| 比較 | RMSE | MAPE | MASE |
|---|---:|---:|---:|
| 外生変数なしgrid best | 21,538.48 | 4.61 | 1.41 |
| 外生変数ありexog | 23,967.15 | 4.95 | 1.60 |

## 11. 実装上の注意点

- これはNeuralForecastライブラリのAutoformerを使った参考baselineであり、主分析モデルではない。
- fixed Bのみで実装・評価している。fixed Aは未評価である。
- 学習はlog scaleの `y`、評価は原系列 `number_parcels` scaleで行う。
- 外生変数あり版はconditional forecastであり、test期間の外生ダミーを既知として与えている。
- `ray_stub_used=True` が記録されている。Windows + Python 3.13 + CPU環境でray本体が使えない・入っていない場合でも、固定パラメータAutoformerを動かすための最小stubを使っている。
- `moving_avg_window=13` としている。Notebookでは、Autoformerの分解でcentered moving averageを使うため、偶数窓による長さ不一致を避ける意図が書かれている。
- グリッド探索は小規模であり、本格的な深層学習チューニングではない。
- 287点程度の月次小標本であるため、深層学習モデルの結果は設定に敏感で、過学習リスクもある。
- 予測CSVの形式は既存の共通forecast formatに合わせている。
- 不明な点: NeuralForecast内部のAutoformer実装の詳細なアーキテクチャ挙動や、より広い探索空間での性能は、この監査では確認していない。

## 12. ゼミでの短い説明文

今回のAutoformerは、自前の簡易版ではなく、NixtlaのNeuralForecastに含まれる `Autoformer` クラスを使った既存ライブラリ版の参考baselineです。入力は月次の宅配便取扱個数のlog系列で、fixed B、つまり2002年4月から2023年12月までで学習し、2024年1月から2026年2月までの26か月を予測しました。予測値は `exp()` で原系列に戻して、RMSE、MAE、MAPE、MASEを計算しています。

外生変数なし版では小規模な手動グリッド探索を行い、`input_size=24`, `hidden_size=32`, `max_steps=200` がbestでした。このbestはProphetや自前の `autoformer_lite` より良かった一方、seasonal naiveには届きませんでした。

また、SSMやSARIMAXと同じ `baseline_m4` の外生ダミーを与えるexog版も試しましたが、外生変数なしのgrid bestより悪化し、SSM、SARIMAX、Prophet regressorsにも届きませんでした。したがって、現段階ではAutoformer系は主分析モデルではなく、小標本月次データに対する参考baselineとして扱うのが妥当です。

## 13. 参考baselineとして扱う理由

Autoformer NeuralForecastを主分析モデルではなく参考baselineとして扱う理由は以下である。

- 本研究の主目的は、状態空間モデルによるトレンド・季節性・イベント効果の分解である。
- SSMは `hike_dummy`, `covid_main`, `covid_wave1`, `covid_2021`, `post_stat_change` の解釈が可能で、研究上の説明と直接つながる。
- Autoformerは予測モデルとしては有用な候補だが、今回の実装ではイベント効果や統計接続後の水準差を解釈する主分析モデルにはなっていない。
- fixed Bのみの評価であり、rolling forecastやfixed Aでの検証はまだ行っていない。
- 小標本月次データでは深層学習系モデルは設定依存・過学習リスクが大きい。
- 実際の結果でも、外生変数なしgrid bestはseasonal naiveに届かず、exog版はSSM/SARIMAX/Prophet regressorsに届かなかった。

以上から、Autoformer NeuralForecastは「深層学習系モデルを試した場合の参考比較」として位置づけ、主分析の中心は引き続きSSMに置く。
