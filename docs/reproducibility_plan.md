# Reproducibility Plan

この文書は、このリポジトリを再現可能な時系列研究プロジェクトとして再構成するための計画である。
現時点では分析コード、notebook、論文原稿、既存の `output/` は変更せず、段階的に再現可能な生成ルートを整備する。

## 1. 新しいディレクトリ構成

```text
Transport_amount_project/
├── README.md
├── requirements.txt
├── pyproject.toml
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── features.py
│   ├── ssm_models.py
│   ├── analysis.py
│   ├── reporting.py
│   └── visualization.py
├── scripts/
│   └── run_analysis.py
├── notebooks/
│   ├── archive/
│   └── exploratory/
├── output/
│   ├── tables/
│   ├── figures/
│   ├── html/
│   └── intermediate/
├── paper_2/
│   ├── paper_2.tex
│   ├── abstract.tex
│   └── paper_2.pdf
└── tests/
    ├── test_data_loader.py
    ├── test_features.py
    └── test_ssm_models.py
```

基本方針は、最終結果を `scripts/run_analysis.py` から再生成できるようにすることである。
探索用 notebook は補助扱いとし、論文は `output/tables/` と `output/figures/` の生成物を参照する。

## 2. 既存ファイルの移行方針

`data/raw/` と `data/processed/` は現状の方向性を維持する。
主論文で使うデータと拡張分析用データを明確に分ける。

- `data/raw/Transport_amount_data.csv`: 主分析の元データ
- `data/raw/mlit_monthly_economy_cargo.csv`: 後続統計
- `data/processed/parcel_volume_connected.csv`: 拡張分析用の接続済みデータ

`src/data_loader.py`, `src/features.py`, `src/ssm_models.py`, `src/visualization.py` は維持しつつ、notebook 内にある推定・表出力ロジックを次のファイルへ移す。

- `src/analysis.py`: モデル推定、モデル比較、残差診断
- `src/reporting.py`: CSV と LaTeX 表の出力

既存 notebook はすぐに削除せず、まず `notebooks/archive/` に移して探索履歴として残す。
最終分析に必要な notebook がある場合は、軽量化したものを `notebooks/exploratory/` に置く。

既存の `output/` は消さず、新しい生成物を以下に出す。

- `output/figures/`
- `output/tables/`
- `output/html/`
- `output/intermediate/`

## 3. `scripts/run_analysis.py` の責務

`scripts/run_analysis.py` は、論文に必要な結果を一発で再生成する入口にする。

主な責務は次の通り。

1. 入力データを読む
2. 前処理する
3. イベントダミーを作る
4. 比較モデルを推定する
5. 最終モデルを推定する
6. 結果テーブルを `output/tables/` に保存する
7. 図を `output/figures/` に保存する
8. 実行条件、データ期間、ライブラリ版などのメタ情報を保存する

基本コマンドは以下を想定する。

```bash
python scripts/run_analysis.py
```

必要に応じて、最小限のオプションを追加する。

```bash
python scripts/run_analysis.py --data data/raw/Transport_amount_data.csv --out output
```

最初から複雑な CLI にせず、固定設定で確実に再現できることを優先する。

## 4. 出力すべき成果物

### `output/tables/`

```text
model_comparison.csv
model_comparison.tex
final_model_params.csv
final_model_params.tex
event_effect_summary.csv
event_effect_summary.tex
residual_diagnostics.csv
residual_diagnostics.tex
run_metadata.json
```

各成果物の内容は次を想定する。

- `model_comparison.csv`: モデル名、log likelihood、AIC、BIC、パラメータ数
- `final_model_params.csv`: 推定値、標準誤差、z値、p値
- `event_effect_summary.csv`: 各イベント係数、対数スケール、パーセント換算、対象期間
- `residual_diagnostics.csv`: Ljung-Box などの残差診断
- `run_metadata.json`: 実行日時、入力ファイル、データ期間、行数、Python/statsmodels/pandas/numpy 版

### `output/figures/`

```text
original_series.png
decomposition_main.png
decomposition_effects.png
observed_vs_fitted.png
trend_component.png
seasonal_component.png
residuals.png
```

論文に最低限対応させる図は次の3つとする。

- `original_series.png`
- `decomposition_main.png`
- `decomposition_effects.png`

## 5. 最小限の pytest 計画

最初のテストは、研究結果の数値そのものではなく、壊れやすい前処理とモデル入力を守ることを目的にする。

### `tests/test_data_loader.py`

- `number_parcels` がカンマ付き文字列でも float 化できる
- `y = log(number_parcels)` が作られる
- 欠損月があると `ValueError`
- 重複月があると `ValueError`
- 0 以下の目的変数で `ValueError`

### `tests/test_features.py`

- `hike_dummy` の開始月・終了月が正しく 1 になる
- 期間外が 0 になる
- `end=None` のダミーが開始月以降ずっと 1 になる
- `prepare_event_data` が `df`, `exog_data`, `exog_names` を同じ順序で返す

### `tests/test_ssm_models.py`

- 小さな人工時系列でモデルが初期化できる
- `param_names` 数と外生変数数が一致する
- `update()` 後に `obs_cov`, `state_cov`, `obs_intercept` の形が正しい
- 外生変数の長さが `endog` と違う場合は明示的にエラーにする

余裕があれば `tests/test_run_analysis.py` を追加し、短いサンプルデータを使って `run_analysis.py` が成果物を作る smoke test を行う。

## 6. `paper_2.tex` と生成物の対応

方針は、論文に手入力する数値を減らすことである。

図は最終的に以下へ対応させる。

```tex
../output/figures/original_series.png
../output/figures/decomposition_main.png
../output/figures/decomposition_effects.png
```

現在の参照先である `../output/originalseries.png`, `../output/Decomposition_4.png`, `../output/Decomposition_5.png` は、再現可能な生成ルートができた後で置き換える。

表は LaTeX 断片として生成し、`paper_2.tex` から読み込む。

```tex
\input{../output/tables/model_comparison.tex}
\input{../output/tables/final_model_params.tex}
\input{../output/tables/residual_diagnostics.tex}
```

CSV と LaTeX 断片の両方を出すことで、検証しやすさと論文への取り込みやすさを両立する。

```text
model_comparison.csv
model_comparison.tex
final_model_params.csv
final_model_params.tex
```

これにより、論文中の AIC、BIC、係数、p 値がコード実行結果と一致する。

## 7. 安全に進める小さなステップ

1. 現状確認用の再現性計画を文書化する
2. 新しい出力先だけ追加し、既存 `output/` は消さない
3. データ読み込みと特徴量作成だけを `run_analysis.py` にする
4. 最終モデルだけスクリプト化し、`final_model_params.csv` を出す
5. 比較モデルを追加し、`model_comparison.csv` を生成する
6. 図生成を差し替え、既存図と見た目・数値を比較する
7. `pytest` を追加し、まず `data_loader` と `features` だけを守る
8. 最後に `paper_2.tex` の参照先を新しい生成物へ変更する

おすすめの進め方は、既存成果物を残したまま、横に再現可能な生成ルートを作ることである。
古い notebook や図をすぐに整理すると正しい結果を見失いやすいため、まず新しい正規ルートを一本通す。
