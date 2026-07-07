# output配下の棚卸しと整理計画

作成日: 2026-07-07  
作業ブランチ: `feature/output-cleanup`

## 1. 調査目的

`output/` 配下には、現在の論文用成果物、予測評価の成果物、感度分析の成果物に加えて、初期Notebookで作成されたと思われる古いHTML・PNG・CSVが混在している。

今回の目的は、削除や移動を行う前に、以下を整理することである。

- 現在の分析で使っている可能性が高い成果物を誤って消さない
- 古い成果物や用途不明ファイルを archive 候補として分ける
- 論文用・予測評価用・感度分析用の出力を混在させない
- 次回、安全に `git mv` で整理できるようにする

この文書作成時点では、`output/` 配下のファイル削除・移動・リネーム・再生成は行っていない。

## 2. 現在のoutput構造

| directory | role | current assessment |
|---|---|---|
| `output/` | 初期分析由来と思われるPNG/HTML/CSVが直下に残っている | legacy成果物が多い。削除ではなくarchive移動候補 |
| `output/figures/` | 再現可能パイプラインの論文用図 | `scripts/run_analysis.py` と `README.md` で参照。維持 |
| `output/tables/` | 再現可能パイプラインの論文用表 | `scripts/run_analysis.py` と `README.md` で参照。維持 |
| `output/forecasts/` | 予測評価の予測値・指標・図・Plotly HTML | forecast notebooks/docsで参照。維持 |
| `output/sensitivity/` | covid_main、recent hike、fixed slope、trend rigidityなどの補助分析 | notebooks/docs/research logで参照。維持 |
| `output/logs/` | 実行メタデータ | 再現性確認用として維持 |
| `output/intermediate/` | 中間出力用ディレクトリ | 現状は `.gitkeep` のみ。維持 |

## 3. ファイル棚卸し

| path | file_type | inferred_role | referenced_by | suggested_action | reason |
|---|---|---|---|---|---|
| `output/figures/original_series.png` | PNG | 現行パイプラインの原系列図 | `README.md`, `scripts/run_analysis.py`, `docs/reproducibility_plan.md` | 残す | 論文・再現可能パイプライン用 |
| `output/figures/decomposition_main.png` | PNG | 現行SSM分解図 | `README.md`, `scripts/run_analysis.py` | 残す | 論文・再現可能パイプライン用 |
| `output/figures/decomposition_effects.png` | PNG | 現行SSMの外生効果図 | `README.md`, `scripts/run_analysis.py` | 残す | 論文・再現可能パイプライン用 |
| `output/tables/data_summary.csv` | CSV | データ概要表 | `scripts/run_analysis.py`, `docs/reproducibility_plan.md` | 残す | 現行パイプライン生成物 |
| `output/tables/event_dummy_summary.csv` | CSV | イベントダミー概要表 | `scripts/run_analysis.py`, `docs/reproducibility_plan.md` | 残す | 現行パイプライン生成物 |
| `output/tables/final_model_fit_summary.csv` | CSV | 最終SSM fit summary | `scripts/run_analysis.py`, `README.md` | 残す | 現行パイプライン生成物 |
| `output/tables/final_model_params.csv` | CSV | 最終SSM係数表 | `scripts/run_analysis.py`, `README.md` | 残す | 現行パイプライン生成物 |
| `output/tables/final_model_params.tex` | TeX | 論文用係数表 | `scripts/run_analysis.py`, `README.md`, `paper_2/` | 残す | 論文用 |
| `output/tables/model_comparison.csv` | CSV | 現行SSMモデル比較表 | `scripts/run_analysis.py`, `README.md` | 残す | 現行パイプライン生成物 |
| `output/tables/model_comparison.tex` | TeX | 論文用モデル比較表 | `scripts/run_analysis.py`, `README.md`, `paper_2/` | 残す | 論文用 |
| `output/forecasts/predictions/*.csv` | CSV | 予測評価の予測値 | `notebooks/forecasting/*`, `docs/forecast_*`, research logs | 残す | 現行予測評価の基礎データ |
| `output/forecasts/metrics/*.csv` | CSV | 予測評価の指標・比較表 | `notebooks/forecasting/*`, `docs/forecast_*`, research logs | 残す | 現行予測評価の主要成果物 |
| `output/forecasts/figures/*.png` | PNG | 予測評価図 | `notebooks/forecasting/*`, `docs/forecast_*` | 残す | 現行予測評価の図 |
| `output/forecasts/html/*.html` | HTML | Plotly予測診断 | `docs/forecast_results_summary.md`, `docs/forecast_evaluation_design_note.md` | 残す | ゼミ説明・診断用 |
| `output/sensitivity/covid_main_window_*` | CSV/PNG | covid_main終了時点感度分析 | `notebooks/04_covid_main_window_sensitivity.ipynb`, research logs | 残す | 現行補助分析 |
| `output/sensitivity/recent_hike_*` | CSV/PNG | 直近運賃値上げダミー補助分析 | `notebooks/05_recent_hike_sensitivity.ipynb` | 残す | 査読対応用補助分析 |
| `output/sensitivity/fixed_slope_*` | CSV/PNG | 固定傾きSSM補助分析 | `notebooks/06_fixed_slope_ssm_sensitivity.ipynb`, research logs | 残す | 査読対応用補助分析 |
| `output/sensitivity/trend_rigidity_*` | CSV/PNG | トレンド硬さ比較 | `notebooks/07_trend_rigidity_sensitivity.ipynb`, research logs | 残す | 現行補助分析 |
| `output/logs/run_metadata.json` | JSON | パイプライン実行メタデータ | `scripts/run_analysis.py` 周辺の再現性文脈 | 残す | 実行記録として有用 |
| `output/originalseries.png` | PNG | 旧原系列図 | `README.md`, `paper_2/paper_2 copy.tex`, `docs/reproducibility_plan.md` | 要確認 | 現行は `output/figures/original_series.png` へ移行済みだが旧参照が残る |
| `output/Decomposition_4.png` | PNG | 旧分解図の可能性 | `paper_2/paper_2 copy.tex`, `docs/reproducibility_plan.md` | 要確認 | 旧paper copyが参照。現行図への置換確認後にarchive候補 |
| `output/Decomposition_5.png` | PNG | 旧分解図の可能性 | `paper_2/paper_2 copy.tex`, `docs/reproducibility_plan.md` | 要確認 | 旧paper copyが参照。現行図への置換確認後にarchive候補 |
| `output/Decomposition.png` | PNG | 初期Notebook由来の旧分解図 | 明確な現行参照なし | `output/archive/legacy_figures/` へ移動候補 | 現行出力と命名規則が異なる |
| `output/Decomposition_2.png` | PNG | 初期Notebook由来の旧分解図 | 明確な現行参照なし | `output/archive/legacy_figures/` へ移動候補 | 現行出力と命名規則が異なる |
| `output/Decomposition_3.png` | PNG | 初期Notebook由来の旧分解図 | 明確な現行参照なし | `output/archive/legacy_figures/` へ移動候補 | 現行出力と命名規則が異なる |
| `output/Decomposition_STL.png` | PNG | STL分解の旧図 | 明確な現行参照なし | `output/archive/legacy_figures/` へ移動候補 | 現行SSM出力ではない可能性が高い |
| `output/output_plot.html` | HTML | 初期NotebookのPlotly図 | `notebooks/01_transport_amount.ipynb` | `output/archive/legacy_html/` へ移動候補 | 現行分析では `output/forecasts/html/` を使用 |
| `output/output_plot2.html` | HTML | 初期NotebookのPlotly図 | `notebooks/01_transport_amount.ipynb` | `output/archive/legacy_html/` へ移動候補 | 現行分析では `output/forecasts/html/` を使用 |
| `output/output_plot_4.html` | HTML | 初期NotebookのPlotly図 | `notebooks/01_transport_amount.ipynb` | `output/archive/legacy_html/` へ移動候補 | 現行分析では `output/forecasts/html/` を使用 |
| `output/output_plot_5.html` | HTML | 初期NotebookのPlotly図 | 明確な現行参照なし | `output/archive/legacy_html/` へ移動候補 | 用途不明だが削除よりarchiveが安全 |
| `output/output_plot_6.html` | HTML | 初期NotebookのPlotly図 | `notebooks/01_transport_amount.ipynb` | `output/archive/legacy_html/` へ移動候補 | 現行分析では `output/forecasts/html/` を使用 |
| `output/log_likelihood_surface.html` | HTML | 初期モデル探索の可視化 | 明確な現行参照なし | `output/archive/legacy_html/` へ移動候補 | 現行パイプライン出力ではない可能性 |
| `output/log_likelihood_surface_1.html` | HTML | 初期モデル探索の可視化 | 明確な現行参照なし | `output/archive/legacy_html/` へ移動候補 | 現行パイプライン出力ではない可能性 |
| `output/log_likelihood_surface_2.html` | HTML | 初期モデル探索の可視化 | 明確な現行参照なし | `output/archive/legacy_html/` へ移動候補 | 現行パイプライン出力ではない可能性 |
| `output/log_likelihood_surface_3.html` | HTML | 初期モデル探索の可視化 | 明確な現行参照なし | `output/archive/legacy_html/` へ移動候補 | 現行パイプライン出力ではない可能性 |
| `output/residual_comparison.html` | HTML | 初期Notebookの残差比較 | `notebooks/01_transport_amount.ipynb` | `output/archive/legacy_html/` へ移動候補 | 現行の残差診断とは別系統 |
| `output/trend_comparison.html` | HTML | 初期Notebookのトレンド比較 | `notebooks/01_transport_amount.ipynb` | `output/archive/legacy_html/` へ移動候補 | 現行の感度分析図とは別系統 |
| `output/result_ssm.csv` | CSV | 初期SSM結果の中間CSV | `notebooks/01_transport_amount.ipynb` | `output/archive/legacy_tables/` へ移動候補 | 現行SSM結果は `output/tables/` と `output/sensitivity/` に整理済み |
| `output/**/*.gitkeep` | placeholder | 空ディレクトリ維持 | Git管理用 | 残す | 削除不要 |

## 4. 削除せず残すべきもの

以下は、現在の主要分析・論文用出力・補助分析・予測評価で使われている可能性が高いため、削除しない。

- `output/figures/`
  - `original_series.png`
  - `decomposition_main.png`
  - `decomposition_effects.png`
- `output/tables/`
  - `data_summary.csv`
  - `event_dummy_summary.csv`
  - `final_model_fit_summary.csv`
  - `final_model_params.csv`
  - `final_model_params.tex`
  - `model_comparison.csv`
  - `model_comparison.tex`
- `output/forecasts/`
  - `predictions/*.csv`
  - `metrics/*.csv`
  - `figures/*.png`
  - `html/*.html`
- `output/sensitivity/`
  - `covid_main_window_*`
  - `recent_hike_*`
  - `fixed_slope_*`
  - `trend_rigidity_*`
- `output/logs/run_metadata.json`
- 各ディレクトリの `.gitkeep`

## 5. archive移動候補

削除ではなく、まず `output/archive/` 配下へ移動するのが安全そうなもの。

### legacy figures

移動先案: `output/archive/legacy_figures/`

- `output/Decomposition.png`
- `output/Decomposition_2.png`
- `output/Decomposition_3.png`
- `output/Decomposition_STL.png`

以下は旧参照が残っているため、すぐ移動せず要確認。

- `output/originalseries.png`
- `output/Decomposition_4.png`
- `output/Decomposition_5.png`

### legacy HTML

移動先案: `output/archive/legacy_html/`

- `output/output_plot.html`
- `output/output_plot2.html`
- `output/output_plot_4.html`
- `output/output_plot_5.html`
- `output/output_plot_6.html`
- `output/log_likelihood_surface.html`
- `output/log_likelihood_surface_1.html`
- `output/log_likelihood_surface_2.html`
- `output/log_likelihood_surface_3.html`
- `output/residual_comparison.html`
- `output/trend_comparison.html`

### legacy CSV / tables

移動先案: `output/archive/legacy_tables/`

- `output/result_ssm.csv`

## 6. 削除候補

現時点で「即削除してよい」と断定できるファイルはない。

理由は以下の通り。

- 古いHTMLやPNGでも、初期Notebookや旧TeXから参照されているものがある
- 用途不明ファイルも、過去の分析過程を説明するために必要になる可能性がある
- Git履歴だけに頼らず、まず archive へ移す方が安全

削除を検討する場合は、少なくとも一度 archive 移動してから、一定期間問題がないことを確認した後に行う。

## 7. 推奨整理方針

1. `output/archive/` を作成する
2. 古い直下HTMLを `output/archive/legacy_html/` へ移動する
3. 古い直下PNGを `output/archive/legacy_figures/` へ移動する
4. 古い直下CSVを `output/archive/legacy_tables/` へ移動する
5. 現行の `output/figures/`, `output/tables/`, `output/forecasts/`, `output/sensitivity/` は維持する
6. `paper_2/paper_2 copy.tex` と `README.md` の旧参照を確認してから、`output/originalseries.png`, `output/Decomposition_4.png`, `output/Decomposition_5.png` をarchive対象にする
7. 削除は最後の段階にし、まずは `git mv` によるarchive移動に留める

## 8. 次に実行する場合の安全な手順

実際に整理する次回作業では、以下の順序が安全である。

1. `git status --short` で作業ツリーを確認する
2. `output/archive/legacy_figures/`, `output/archive/legacy_html/`, `output/archive/legacy_tables/` を作成する
3. 移動対象を1カテゴリずつ `git mv` で移動する
4. 移動後に `rg` で旧パス参照を確認する
5. `README.md`, `paper_2/paper_2 copy.tex`, `notebooks/01_transport_amount.ipynb` の扱いを判断する
6. 現行パイプラインの `scripts/run_analysis.py` が `output/figures/` と `output/tables/` を問題なく使うことを確認する
7. archive移動後、ゼミ・論文・Notebookで必要な図や表が消えていないか目視確認する
8. 問題がなければarchive移動をcommitする
9. 削除候補は別commit・別作業として扱う

次回の実行候補例:

```powershell
New-Item -ItemType Directory -Force output/archive/legacy_figures
New-Item -ItemType Directory -Force output/archive/legacy_html
New-Item -ItemType Directory -Force output/archive/legacy_tables
git mv output/Decomposition.png output/archive/legacy_figures/
git mv output/output_plot.html output/archive/legacy_html/
git mv output/result_ssm.csv output/archive/legacy_tables/
```

ただし、今回の作業では上記コマンドは実行していない。

## 9. 手動確認が必要な点

- `paper_2/paper_2 copy.tex` が現在も必要なファイルか
- `output/originalseries.png`, `output/Decomposition_4.png`, `output/Decomposition_5.png` を現行図で置換済みとみなしてよいか
- `notebooks/01_transport_amount.ipynb` を歴史的Notebookとして扱い、出力をarchiveしてよいか
- `output/log_likelihood_surface*.html` に現在も参照したい分析結果が残っているか
- `output/output_plot*.html` がゼミ・論文・口頭説明でまだ使われる可能性があるか

## 10. まとめ

現行の主要成果物は、概ね以下に整理されている。

- 論文用: `output/figures/`, `output/tables/`
- 予測評価用: `output/forecasts/`
- 補助分析用: `output/sensitivity/`

一方で、`output/` 直下には初期Notebook由来とみられる古いPNG/HTML/CSVが残っている。これらはすぐ削除せず、まず `output/archive/` へ移動する方針が安全である。
