# COVID-19新規陽性者数 前処理確認ログ

## 入力

- 入力ファイル：`data/experimental/covid_cases/raw/newly_confirmed_cases_daily.csv`
- 取得ログ：`output/covid_cases_exog/logs/data_acquisition_log.md`
- 行数（ヘッダー除く）：1,209
- 列数（raw CSV）：49
- 日付範囲：2020-01-16–2023-05-08

## 全国値と都道府県合計

- `ALL`を全国新規陽性者数として読み込んだ。
- 都道府県47列の合計との差分非ゼロ日数：0
- 差分の最大絶対値：0
- 今回のraw CSVでは、日次の`ALL`と都道府県合計は一致した。これは集計定義の同一性を保証するものではなく、取得値の照合結果である。

## 月次化と外生変数

- `Date`を暦月（`YYYY-MM`）へ変換し、日次`ALL`を月内で合計した。
- COVID対象期間は2020年3月～2023年5月とした。
- 対象期間外の`cases_exog`を0とした。これは対象期間を外生変数として明示的に限定し、期間外をモデル入力に混入させないためである。
- `log1p_cases = log(1 + cases_exog)`、`log1p_cases_lag0`（同月）、`log1p_cases_lag1`（1か月ラグ）を作成した。
- 2023年5月8日のrawレコードは削除せず、2023年5月の月次合計に含めた。公式ページの最終集計日との対応は後続分析前に確認する。

## 保存ファイル

- processed CSV：`data/experimental/covid_cases/processed/monthly_cases.csv`
- 図：`output/covid_cases_exog/figures/monthly_cases_series.png`
- 本ログ：`output/covid_cases_exog/logs/preprocessing_log.md`
- 月次行数：41（COVID対象月数：39）

## 未実施

状態空間モデル推定、ラグ選択、ハイパーパラメータ選択、再予測、因果効果の推定は行っていない。

## 実行時のgit status --short

```text
?? data/experimental/
?? notebooks/experimental/
?? output/covid_cases_exog/
```
