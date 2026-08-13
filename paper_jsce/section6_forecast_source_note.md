# 第6章「予測評価」出典確認・本文方針メモ

## 1. 第6章の位置づけ

予測評価は，状態空間モデル（SSM）の構造分解を補助的に検証するための分析であり，すべての手法を同一条件で競わせる予測コンペではない。特に，外生情報を使わない`unconditional forecast`と，評価期間のイベントダミーを既知として与える`conditional forecast`は情報条件が異なるため，両者を同じ順位表で単純比較しない。

本文では，直近の統計接続後期間を含む`fixed B`を中心に扱う。COVID期をまたぐ`COVID one-year`は，SSMのトレンド仕様に対する補助的な確認として，本文では1段落程度に圧縮する。Autoformer，Prophet，SARIMAXの詳細な設定や探索履歴は本文の主題とせず，必要な場合も補足資料に回す。

## 2. fixed Bの設定

接続済み系列`data/processed/parcel_volume_connected.csv`を用い，学習期間を2002年4月から2023年12月，評価期間を2024年1月から2026年2月とする。学習月数は261か月，評価月数は26か月である。評価値は`number_parcels`の原系列スケールで計算される。モデルによって学習時に対数系列を使う場合も，予測後に原系列へ戻してから指標を算出している。

fixed BのSSMおよび他の条件付きモデルでは，`baseline_m4`の外生変数（`hike_dummy`，`covid_main`，`covid_wave1`，`covid_2021`，`post_stat_change`）を評価期間について既知として与える。このため，SSMの結果は将来のイベント発生を無条件に予測したものではなく，イベントダミーが既知という情報条件下のconditional forecastである。

## 3. 本文で扱う比較モデル

### 3.1 外生変数なしの基準

`seasonal_naive`を，前年同月を用いる月次季節ベンチマークとして扱う。fixed Bでは，RMSE 13,622.8，MAE 11,619.9，MAPE 2.91%，MASE 0.929である。seasonal naiveは外生変数を使わないため，条件付きSSMとの数値を直接的な優劣として比較せず，情報条件の異なる基準として示す。

### 3.2 構造変化を条件付けたモデル

主分析モデルのTR0に対応する`ssm_conditional`は，RMSE 8,112.7，MAE 6,756.3，MAPE 1.72%，MASE 0.540である。固定傾きの`ssm_fixed_slope`は，RMSE 8,135.1，MAE 6,728.9，MAPE 1.71%，MASE 0.538であり，TR0とほぼ同等である。両者の差は，fixed Bにおける予測性能が傾きノイズの有無に大きく依存しないことを補助的に示す。

条件付き比較の参照として，`sarimax_grid_best`はRMSE 7,975.1，MAE 6,701.3，MAPE 1.71%，MASE 0.536であり，`sarimax_fixed`はRMSE 8,197.0，MAE 6,873.3，MAPE 1.76%，MASE 0.550である。SSMは`SARIMAX`の探索最良仕様に僅差で及ばないが，同程度の水準にある。`prophet_regressors`および`autoformer_neuralforecast_exog`は，それぞれRMSE 17,877.1および23,967.2であり，本文では詳細順位を広げず，参考比較として扱う。

## 4. 評価指標

RMSE，MAE，MAPEおよびMASEを用いる。RMSEは大きな誤差を重く評価し，MAEは平均的な絶対誤差を表す。MAPEは相対誤差率，MASEはseasonal naive等を基準に標準化した誤差である。本文では4指標を併記するが，単一指標による精度順位を主張しない。

## 5. COVID one-yearの扱い

COVID one-yearでは，学習期間を2002年4月から2021年2月（227か月），評価期間を2021年3月から2023年5月（27か月）とする。SSMの`ssm_conditional_baseline_m4`はRMSE 18,236.0，MAE 14,561.1，MAPE 3.67%，MASE 1.180，`ssm_fixed_slope`はRMSE 18,244.6，MAE 14,565.3，MAPE 3.67%，MASE 1.180である。`seasonal_naive`はRMSE 19,347.9，MAE 14,410.3，MAPE 3.61%，MASE 1.167である。

この設定では`post_stat_change`が学習期間内で定数0となるため，SSMの条件付きモデルから除外され，統計接続後の水準補正を学習できない。したがって，COVID one-yearはfixed Bと同じ比較表に混在させず，TR0/TR1の予測差が小さいことを確認する補助的な一段落として扱う。独立した表や図は作成しない。

## 6. 第6章本文の構成案

1. **予測設定**：接続済み系列，fixed Bの学習・評価期間，原系列スケール，unconditional / conditionalの区別，既知外生ダミーを説明する。
2. **fixed Bの評価結果**：seasonal naiveを情報条件の異なる基準として示し，SSM（TR0）とSSM（TR1）の4指標を中心に記述する。SARIMAX grid bestは参照値として短く触れる。
3. **COVID one-yearの補助評価**：27か月の設定，TR0/TR1がほぼ同等であること，`post_stat_change`が学習期間内で変動しないことを一段落で示す。
4. **解釈上の注意と小括**：conditional forecastを無条件の将来予測と解釈しないこと，seasonal naiveとの直接順位比較を避けること，予測評価は構造分解モデルの補助的な妥当性確認であることを述べる。

## 7. 表案（本文に入れる場合）

紙幅を優先し，表を1つだけ置く場合は，fixed Bの情報条件を分けた次の簡略表を推奨する。`table`環境を用い，片側カラム内で`\small`または`\footnotesize`とする。`table*`，`figure*`，`\textwidth`は用いない。

| 情報条件 | モデル | RMSE | MAE | MAPE (%) | MASE |
|---|---|---:|---:|---:|---:|
| unconditional | `seasonal_naive` | 13,622.8 | 11,619.9 | 2.91 | 0.929 |
| conditional | `ssm_conditional`（TR0） | 8,112.7 | 6,756.3 | 1.72 | 0.540 |
| conditional | `ssm_fixed_slope`（TR1） | 8,135.1 | 6,728.9 | 1.71 | 0.538 |
| conditional | `sarimax_grid_best` | 7,975.1 | 6,701.3 | 1.71 | 0.536 |

注）conditionalは評価期間の`baseline_m4`外生ダミーを既知として与えた条件付き予測である。unconditionalとの数値は情報条件が異なるため，単純な順位比較を行わない。COVID one-yearは本文の補助段落に留め，表には含めない。

## 8. 出典ファイルと注意点

- fixed B SSM/TR1：`output/forecasts/metrics/fixed_b_ssm_slope_comparison.csv`
- fixed B SSM：`output/forecasts/metrics/ssm_metrics.csv`
- fixed B TR1：`output/forecasts/metrics/fixed_slope_ssm_forecast_metrics.csv`
- fixed B unconditional/conditional比較：`output/forecasts/metrics/model_comparison_unconditional.csv`，`model_comparison_conditional.csv`，`model_comparison_fixed_b_conditional.csv`
- fixed B予測系列：`output/forecasts/predictions/fixed_b_ssm.csv`，`fixed_b_fixed_slope_ssm.csv`，`fixed_b_naive.csv`等
- COVID one-year指標：`output/forecasts/metrics/covid_one_year_forecast_metrics.csv`
- COVID one-year予測系列：`output/forecasts/predictions/covid_one_year_forecasts.csv`
- 設定・情報条件：`docs/forecast_evaluation_design_note.md`，`notebooks/forecasting/10_fixed_slope_ssm_forecast.ipynb`，`notebooks/forecasting/11_covid_one_year_forecast.ipynb`

SARIMAX，Prophet，Autoformerの詳細仕様，ハイパーパラメータ探索およびPlotly診断HTMLは，10ページ以内の本文では扱いを広げない。これらは，SSMの予測性能を補足的に位置付ける必要がある場合の補助資料とする。

## 9. main.texへの反映判断

現時点では，数値の出典と情報条件は確認済みであり，第6章本文へ進める。反映時は，fixed Bを中心とし，COVID one-yearを1段落に圧縮する。表を採用する場合も片側カラム内の小型`table`に限定し，図は作成しない方針が妥当である。
