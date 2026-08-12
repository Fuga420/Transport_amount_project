# 第4章用TR0 / `baseline_m4` 図生成メモ

## 1. 生成目的

第4章の主仕様であるTR0 / `baseline_m4` だけを描画した投稿用分解図を作成した。既存のTR0/TR1比較図および6仕様比較図は上書きしていない。`main.tex` への反映とLaTeXビルドは行っていない。

## 2. 使用データ

- 入力：`data/processed/parcel_volume_connected.csv`
- 系列：旧統計と後続統計を接続した`number_parcels`
- 目的変数：自然対数を取った`y=log(number_parcels)`
- 期間：2002年4月～2026年2月
- 観測数：287か月
- 図の生成時には`src.data_loader.load_connected_parcel_data`と，既存Notebookで使用されている`add_period_dummies`を利用した。

## 3. 使用モデル仕様

- 仕様名：TR0 / `baseline_m4`
- モデル：`src.ssm_models.LocalLinearTrendSeasonalWithMultiFixedExog`
- トレンド：local linear trend（水準ノイズ・傾きノイズを推定）
- 季節成分：月次季節成分（周期12）
- 外生変数：固定係数のイベント・統計接続ダミー
- 推定条件：既存の`notebooks/06_fixed_slope_ssm_sensitivity.ipynb`におけるTR0/baseline_m4の定義，初期値，`maxiter=1000`を再現

新しいモデル仕様，外生変数，トレンド制約，予測設定は追加していない。

## 4. 使用したイベント変数

| 変数 | 期間 | 図中の扱い |
|---|---|---|
| `hike_dummy` | 2017年10月～2019年12月 | 指定期間に対応するモデル上の水準差 |
| `covid_main` | 2020年3月～2023年5月 | 指定期間に対応するモデル上の水準差 |
| `covid_wave1` | 2020年4月～2020年5月 | 指定期間に対応するモデル上の水準差 |
| `covid_2021` | 2021年1月～2021年9月 | 指定期間に対応するモデル上の水準差 |
| `post_stat_change` | 2022年8月以降 | 統計接続に伴う水準補正 |

イベント効果図のタイトルと注記では，因果効果・需要増減・価格弾力性を意味する表現を避け，「model-based level differences（モデル上の水準差）」とした。

## 5. 生成した図ファイル

### 図-2候補

```text
paper_jsce/figures/section4_tr0_components.png
```

内容は，(a)観測値・適合値，(b)トレンド成分，(c)季節成分，(d)残差の4パネルである。観測値は実線，適合値は破線とし，TR1等の比較仕様は表示していない。

### 図-3候補

```text
paper_jsce/figures/section4_tr0_event_effects.png
```

5イベントを1変数1パネルで表示した。各パネルには指定期間の境界を灰色破線で示し，`post_stat_change`は需要イベントではなく統計接続補正として扱っている。

### 画像仕様

- PNG，300 dpi
- `section4_tr0_components.png`：2167×1712 px
- `section4_tr0_event_effects.png`：2280×2302 px
- 白背景，黒線，破線・点線・線幅で区別
- 最終掲載幅での可読性を考慮したフォント・凡例サイズ

## 6. 既存CSVとの一致確認

再現実行したTR0の推定値を既存CSVと比較した。

| 確認項目 | 既存CSV | 再現実行 | 差 |
|---|---:|---:|---:|
| 観測数 | 287 | 287 | 0 |
| 対数尤度 | 584.0694369756319 | 584.0694369756319 | 0 |
| AIC | -1124.1388739512638 | -1124.1388739512638 | 0 |
| BIC | -1043.6302652045522 | -1043.6302652045522 | 0 |
| 係数最大絶対差 | — | — | 約`9.37e-17` |

収束状態は`converged=True`，`warnflag=0`であり，既存の`fixed_slope_coefficients.csv`および`fixed_slope_model_comparison.csv`の`baseline_m4`行と一致した。

## 7. 再推定の有無

図の成分（平滑化トレンド，季節成分，適合値，残差）が既存CSVには保存されていなかったため，既存Notebookと同一の`baseline_m4`仕様を再現実行して成分を取得した。この実行は新しい仕様の提案・モデル比較・再予測ではなく，既存結果の再現確認と投稿用図の整形を目的としたものである。

再実行では`output/`内の既存ファイルを上書きせず，図のみを`paper_jsce/figures/`へ保存した。`src/`およびNotebook自体も変更していない。

## 8. 第4章への掲載上の注意

1. 図-2はTR0の主分解図として使用できる。ただし，残差のLjung--Box検定では自己相関が残るため，「残差は白色雑音である」「モデルが全変動を完全に説明する」とは記述しない。
2. 図-3の各線は指定期間に対応するモデル上の水準差であり，イベントの因果効果ではない。
3. `post_stat_change`は旧統計と後続統計の接続に伴う水準補正であり，需要減少として解釈しない。
4. 図-2・図-3の掲載順，図番号，キャプションおよび本文参照は，`main.tex`へ反映する段階で確定する。
5. 白黒印刷時の線種・文字サイズは，最終PDFの二段組縮小状態で再確認する。
6. TR1，TR1b～TR1d，TR2との比較は第5章に置き，本図には混在させない。

## 9. 今回の変更とgit status

今回の作業で追加した図ファイルは次の2つである。

```text
paper_jsce/figures/section4_tr0_components.png
paper_jsce/figures/section4_tr0_event_effects.png
```

本メモ作成時点の`git status --short`は以下の通りである。Notebook，`src/`，`output/`，`docs/research_log/`には今回の変更はない。

```text
 M paper_jsce/README.md
 M paper_jsce/main.pdf
 M paper_jsce/main.tex
?? paper_jsce/data_event_table_plan.md
?? paper_jsce/data_source_connection_check.md
?? paper_jsce/figures/section4_tr0_components.png
?? paper_jsce/figures/section4_tr0_event_effects.png
?? paper_jsce/legacy_paper_mapping_note.md
?? paper_jsce/main_spec_decision_note.md
?? paper_jsce/section2_data_events_draft.md
?? paper_jsce/section3_methods_draft.md
?? paper_jsce/section4_figure_plan.md
?? paper_jsce/section4_figure_generation_note.md
?? paper_jsce/section4_result_source_note.md
?? paper_jsce/writing_plan.md
```
