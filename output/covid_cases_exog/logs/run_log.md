# 感染者数外生変数モデル 実行ログ

- 実行ブランチ: feature/covid-decay-event
- 宅配便入力: `data/processed/parcel_volume_connected.csv`
- 感染者数入力: `data/experimental/covid_cases/processed/monthly_cases.csv`
- 宅配便分析期間: 2002-04--2026-02（287か月）
- 感染者数月次入力: 2020-01--2023-05（41行）
- COVID外生変数対象期間: 2020-03--2023-05（結合後の対象月数39）
- 対象期間外の感染者数外生変数は0とした。
- log1p_cases_lag1を主仕様候補、lag0を感度確認として定義した。
- 既存のsrc、output/sensitivity、output/forecasts、paper_jsceは変更していない。

## 推定仕様

- 現行5変数モデル: hike_dummy, covid_main, covid_wave1, covid_2021, post_stat_change
- COVID期ダミー＋感染者数ラグ1＋統計接続ダミー
- COVID期ダミー＋感染者数ラグ0＋統計接続ダミー
- 感染者数ラグ1＋統計接続ダミー
- すべて既存のlocal linear trend＋12か月季節状態モデルを用い、感染者数係数を固定係数として推定した。

## 結果概要

- 推定成功: 4/4、収束判定True: 4/4
- 係数は指定された外生変数に対応するモデル上の水準差であり、感染者数係数を因果効果として解釈しない。
- AIC/BIC、残差診断、設計行列の相関・条件数を併せて確認し、単一指標だけで仕様を選択しない。

## 生成ファイル

- metrics/model_comparison.csv
- metrics/coefficients.csv
- metrics/design_diagnostics.csv
- logs/run_log.md

## 実行時のgit status --short

```text
?? data/experimental/
?? docs/interim_presentation/covid_cases_exog_result_note.md
?? notebooks/experimental/
?? output/covid_cases_exog/
?? scripts/experimental/run_covid_cases_exog.py
```
