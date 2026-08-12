# 第4章 図表準備方針：TR0 / `baseline_m4` 分解図

## 1. 確認範囲

`output/` 以下の既存PNG，TR0/TR1およびトレンド硬さ比較のNotebook，係数・診断CSVを確認した。図の再生成，Notebookの実行，推定・再予測，`main.tex` の編集は行っていない。

## 2. TR0単独図の有無

### 結論

**接続済み287か月系列に対するTR0 / `baseline_m4` 単独の分解図は，既存出力からは確認できない。**

現在の分解PNGはすべて複数仕様を同一軸に描画した比較図である。

- `output/sensitivity/fixed_slope_decomposition_main.png`：`baseline_m4` と `fixed_slope_m4` の2仕様
- `output/sensitivity/fixed_slope_decomposition_seasonal.png`：同2仕様の季節成分
- `output/sensitivity/fixed_slope_decomposition_exog.png`：同2仕様の5イベント効果
- `output/sensitivity/fixed_slope_decomposition_residuals.png`：同2仕様の残差
- `output/sensitivity/trend_rigidity_decomposition_main.png`：TR0，TR1，TR1b，TR1c，TR1d，TR2の6仕様
- `output/sensitivity/trend_rigidity_decomposition_seasonal.png`：6仕様の季節成分
- `output/sensitivity/trend_rigidity_decomposition_exog.png`：6仕様の5イベント効果
- `output/sensitivity/trend_rigidity_decomposition_residuals.png`：6仕様の残差

`fixed_slope_*` はTR0の系列を含むため挙動の照合には使用できるが，TR0単独の主結果図とは呼べない。`trend_rigidity_*` は第5章の頑健性確認向けであり，第4章の主図には使用しない。

### 使用しない既存図

`output/figures/decomposition_main.png` および `decomposition_effects.png` は，旧稿時点の系列・イベント構成に基づく図である。`post_stat_change` が含まれず，現行の後続統計接続後系列を表す図としては使用しない。`output/Decomposition_*.png` や `output/archive/legacy_figures/` 以下も同様に旧図として扱う。

## 3. 既存出力で使用可能な図

| 目的 | 既存ファイル | 使用可否 | 適切な位置づけ |
|---|---|---|---|
| TR0とTR1の適合値・トレンドの一致確認 | `fixed_slope_decomposition_main.png` | 条件付き | 第5章のTR0/TR1頑健性図。第4章主図には不使用 |
| TR0とTR1の季節成分比較 | `fixed_slope_decomposition_seasonal.png` | 条件付き | 第5章または補足 |
| TR0とTR1のイベント効果比較 | `fixed_slope_decomposition_exog.png` | 条件付き | 第5章の係数・分解補助図 |
| TR0とTR1の残差比較 | `fixed_slope_decomposition_residuals.png` | 条件付き | 第5章の診断補助図 |
| COVID期以降のトレンド仕様比較 | `trend_rigidity_trends_zoom.png` | 使用可能 | 第5章の補助図。イベント境界線の例としても参照 |
| TR0単独の主分解 | 該当PNGなし | 未確定 | 投稿用に別途整形が必要 |

これらのPNGはNotebook内で300 dpi保存されているが，色線・英語タイトル・比較仕様の凡例を含むため，そのまま投稿用の第4章図へ流用することは推奨しない。

## 4. 再描画に利用できる既存入力

### 4.1 系列とイベント設定

再描画時のデータ入力は次の既存ファイル・定義を使用する。

```text
data/processed/parcel_volume_connected.csv
notebooks/06_fixed_slope_ssm_sensitivity.ipynb
notebooks/07_trend_rigidity_sensitivity.ipynb
```

両Notebookは，接続済み系列を読み込み，`get_forecast_spec("baseline_m4")` と `add_period_dummies` により，次の5変数を作成する。

```text
hike_dummy, covid_main, covid_wave1, covid_2021, post_stat_change
```

イベント期間は第2章の定義と一致させる。図中の境界は，少なくとも次を候補とする。

- `hike_dummy`：2017年10月開始，2019年12月終了
- `covid_main`：2020年3月開始，2023年5月終了
- `covid_wave1`：2020年4月開始，2020年5月終了
- `covid_2021`：2021年1月開始，2021年9月終了
- `post_stat_change`：2022年8月開始

### 4.2 TR0の成分

`notebooks/06_fixed_slope_ssm_sensitivity.ipynb` の `compute_components` は，推定結果から次を作成する。

```text
outputs["baseline_m4"]["components"]["fitted"]
outputs["baseline_m4"]["components"]["trend"]
outputs["baseline_m4"]["components"]["seasonal"]
outputs["baseline_m4"]["components"]["effects"]
outputs["baseline_m4"]["components"]["residual"]
```

`notebooks/07_trend_rigidity_sensitivity.ipynb` では，対応するTR0名が `outputs["TR0_local_linear"]["components"]` である。CSVには係数・適合度・診断値は保存されているが，これら5種類の時系列成分を月別に保存したCSVは確認できない。したがって，係数CSVだけからトレンド・季節・残差を正確に再構成することはできない。

## 5. 再描画が必要な場合の最小手順（未実行）

新しい推定を追加するのではなく，既存Notebookで得たTR0の成分を図表用に整形する場合の手順は次の通りである。

1. 接続済み系列を読み込み，`baseline_m4` の既存イベント定義を適用する。
2. 既存Notebookの実行状態または保存済みの推定結果から，`baseline_m4`（または`TR0_local_linear`）の `components` を取得する。
3. TR0以外の系列を描画対象から除外する。
4. 観測値・適合値，トレンド，季節成分，5イベントの外生効果，残差を投稿用レイアウトへ再配置する。
5. `paper_jsce/figures/` 以下へ，例えば `section4_tr0_decomposition.png` として保存し，PNGの目視確認を行う。

ただし，現状は成分配列を保存したファイルが見つかっていない。Notebookを新たに最初から実行すると推定セルも再実行されるため，それは今回の「再描画のみ」の範囲を超える。まずは既存のNotebook実行状態・保存済みオブジェクト・別媒体の成分CSVがないかを人間が確認し，存在しない場合は，既存仕様を再実行して図だけを保存することについて別途合意を得る必要がある。

## 6. 第4章の推奨図構成

### 推奨：図を2枚に分ける

10ページ以内で可読性を確保するため，5要素すべてを縦長の1枚に詰め込むより，次の2枚に分ける方がよい。

#### 図-2（主図）：適合値と潜在成分

2段または4段の構成とする。

- (a) 観測値と適合値
- (b) トレンド成分
- (c) 季節成分
- (d) 残差

第4章の主張である「観測系列をトレンド・季節成分とイベント項に分解した」ことを読み取りやすい。残差は小パネルにするか，診断表へ回して3段構成としてもよい。

#### 図-3（補助主図）：外生イベント効果

5つのイベントを同一時系列軸で示す。

- `hike_dummy`
- `covid_main`
- `covid_wave1`
- `covid_2021`
- `post_stat_change`

5段の小パネルにすると変数ごとの水準差を区別しやすい。一方，紙幅が厳しい場合は，イベント係数を表-3で示し，図-3はCOVID関連3変数と`post_stat_change`に絞る案もある。その場合でも`hike_dummy`は表から除外しない。

### 1枚にまとめる場合

図-2を4～5段の縦長パネルにする案も可能であるが，A4二段組での縮小時に，イベント名・軸目盛・凡例が読めなくなる可能性が高い。採用する場合は，図中の文字を増やさず，イベント効果を1つのパネルに重ねるのではなく，イベントごとの小パネルを維持する。

## 7. 投稿用の見た目調整方針

### 白黒印刷

- 色の違いだけに依存せず，実線，破線，点線，一点鎖線および線幅で区別する。
- 観測値は黒の実線，適合値は黒の破線とする。
- トレンドは太めの実線，季節成分は標準線幅，残差は細めの実線とする。
- 5イベントは線種を変え，凡例は1箇所にまとめる。
- 背景の色塗りは原則避け，イベント境界を縦の灰色破線で示す。

### 軸・凡例・文字

- 横軸は年月（または年）とし，月次系列であることが分かる目盛間隔にする。
- 縦軸は「対数取扱個数」または `log(number_parcels)` とする。変数名を使う場合は論文本文と同様にアンダースコアを可視化する。
- 最終掲載幅で，目盛・凡例は少なくとも7～8 pt程度，パネルタイトルは8～9 pt程度を確保する。
- 凡例には`TR0`だけを表示し，`TR1`等の仕様名は第5章の比較図に限定する。
- 図注に「イベント項は指定期間に対応するモデル上の水準差であり，因果効果ではない」と記載する。

### イベント境界線

- 全パネルに境界線を入れると過密になるため，主図では`covid_main`の開始・終了と`post_stat_change`開始を薄い縦破線で示す程度に留める。
- 5イベントの開始・終了はイベント効果図に集約する。
- `covid_wave1`，`covid_2021`の境界は小パネル内で示し，境界線の意味を凡例または図注で説明する。
- 月ダミーの終了月の直後に境界線を置くか，終了月の位置に置くかを，図と第2章の定義で統一する。

## 8. 図表整形として実行できる範囲

成分配列が既存の実行状態または保存済み結果として利用可能であれば，TR0単独化，白黒化，線種・文字サイズ・軸ラベル・イベント境界線の調整は図表整形として実行できる。これは新しい分析仮定を追加する作業ではない。

現状で確認できるCSVは係数・モデル比較・診断値に限られ，成分配列は保存されていない。そのため，**現時点で直ちに実行できるのは既存PNGの所在確認と掲載可否判断まで**である。Notebookの推定セルを再実行して成分を得る作業は，再推定を伴う可能性があるため，今回の範囲では実行しない。

## 9. 次に実行すべき作業

1. Notebookの実行履歴，チェックポイントまたは別保存先にTR0成分配列が残っていないかを確認する。
2. 残っていれば，TR0単独の2枚構成（図-2：適合値・成分，図-3：イベント効果）として整形する。
3. 残っていなければ，共著者間で「既存仕様の再実行を図の再描画として許可するか」を決める。
4. 許可後にのみ，`paper_jsce/figures/` へ投稿用PNGを保存し，白黒印刷と縮小時の可読性を確認する。
5. 図の出典ファイル・生成条件・掲載版ファイル名を `section4_result_source_note.md` に追記してから，第4章本文と`main.tex`への反映を検討する。

本メモ作成では，`main.tex`，`src/`，`notebooks/`，`output/`および`docs/research_log/`を変更していない。
