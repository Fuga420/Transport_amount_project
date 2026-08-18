# 状態空間モデルと予測評価の定義確認メモ

作成日：2026-08-18  
対象：src/ssm_models.py、src/forecasting/ssm.py、src/forecasting/evaluation.py、src/forecasting/splits.py、src/forecasting/forecast_specs.py、src/data_loader.py、関連Notebookおよび既存出力  
方針：既存コードと既存出力の読み取りのみを行った。再推定・再予測および main.tex の変更は行っていない。

## 1. 状態空間モデルの実装事実

### 1.1 モデルクラスと状態の構成

主仕様の実装は、src/ssm_models.py の LocalLinearTrendSeasonalWithMultiFixedExog である。statsmodels.tsa.statespace.MLEModel を継承した独自モデルであり、月次季節周期を12とした場合の状態数は 2+(12-1)=13 である。状態はレベル、傾き、11個の季節状態からなる。観測方程式は実装上、概念的に

\[
 y_t=\mu_t+s_t+\boldsymbol{x}_t^{\mathsf T}\boldsymbol{\beta}+\varepsilon_t
\]

と表せる。y は load_connected_parcel_data が作成する \(\log(\mathrm{number\_parcels})\)、s_t は先頭の季節状態、\(\boldsymbol{x}_t\) はイベントダミーである。イベント係数は時点ごとの観測切片に加えられ、状態方程式の状態そのものには含められていない。

### 1.2 トレンドと季節成分

レベルと傾きは次のランダムトレンドとして実装されている。

\[
\begin{aligned}
 \mu_t&=\mu_{t-1}+\delta_{t-1}+\eta_{\mu,t},\\
 \delta_t&=\delta_{t-1}+\eta_{\delta,t}.
\end{aligned}
\]

季節成分は12か月周期のダミー変数型の状態であり、先頭の季節状態を過去11個の季節状態の負の和とする和ゼロ制約を持つ。残りの季節状態は1期ずつシフトされ、先頭の季節状態に季節ノイズが入る。この実装は、12個の独立な月ダミーを直接推定するものではない。

### 1.3 誤差・ノイズと推定分散

主仕様では、コード上の最初の4パラメータを次の共分散行列要素に対応させている。

| パラメータ名 | 実装上の格納先 | 内容 |
|---|---|---|
| obs_error | obs_cov[0,0] | 観測誤差の分散 |
| level_noise | state_cov[0,0] | レベルノイズの分散 |
| slope_noise | state_cov[1,1] | 傾きノイズの分散 |
| seasonal_noise | state_cov[2,2] | 季節ノイズの分散 |

最初の4パラメータは transform_params で二乗変換され、正の値に制約される。したがって、感度分析出力の baseline_m4 にある slope_noise = \(2.2557076995\times10^{-11}\)（本文の丸め値 \(2.26\times10^{-11}\)）は標準偏差ではなく、state_cov[1,1] に入る傾きノイズの分散である。CSVの std_error 列はこの分散パラメータの推定標準誤差であり、ノイズの標準偏差を表すものではない。

状態共分散は実装上、レベル・傾き・季節の3成分を対角要素として設定し、同時点の共分散パラメータは推定していない。したがって、本文では「各ノイズの分散を対角共分散行列の要素として推定した」と記述するのが安全である。独立性や正規分布を個々のノイズについて明示する記述は、独自クラスのコードにはなく、statsmodelsの尤度仮定に依存するため、現時点では断定しない。特に「独立な正規ノイズ」と書く場合は、使用バージョンのstatsmodelsの状態空間尤度に関する出典を併記して確認する必要がある。

固定傾き仕様では、Notebook内の LocalLinearTrendSeasonalFixedSlopeWithMultiFixedExog が傾きノイズの選択行を持たず、obs_error、level_noise、seasonal_noise の3分散を推定する。季節状態の遷移と初期化は主仕様と同じである。

### 1.4 初期状態

独自モデルの初期化は MLEModel(..., initialization='diffuse') であり、初期状態の平均や有限分散を個別に指定していない。本文では「初期状態はdiffuse initializationにより扱った」と記述できるが、初期状態をデータから別途推定した、または特定の事前分布を置いた、とは記述しない。

### 1.5 ソフトウェア、最適化、収束

実装はPython、NumPy、pandas、SciPy、statsmodelsを用いる。requirements.txt では、NumPy 2.2.6、pandas 2.2.3、SciPy 1.15.3、statsmodels 0.14.4 が指定されている。

推定は MLEModel.fit によるカルマンフィルタに基づく尤度最大化である。プロジェクト側では start_params、maxiter=1000、disp=False を指定しているが、最適化法の引数は明示していない。現在のstatsmodels 0.14.4では MLEModel.fit の既定法は lbfgs であるため、再現性の観点では使用バージョンと既定値を記録し、本文で最適化法を明示する場合はこの点を確認してから記載する。

初期値は主仕様で分散パラメータを [0.01, 0.01, 0.001, 0.001] とし、イベント係数について一部のCOVID関連係数に負の開始値を与え、それ以外を0とする。収束判定は独自の許容誤差ではなく、statsmodels結果オブジェクトの mle_retvals にある converged、warnflag、iterations を読み取っている。既存のTR0出力では converged=True、warnflag=0 である。一方、TR2については既存出力で converged=False、warnflag=2 であるため、未収束モデルのAIC/BICを正式なモデル選択根拠として扱わない。

## 2. 予測評価の定義確認

### 2.1 固定分割と推定期間

make_fixed_split_b によるfixed Bは、学習期間が2002年4月から2023年12月、評価期間が2024年1月から2026年2月である。学習は261か月、評価は26か月である。主仕様SSMは学習期間の y=log(number_parcels) と学習期間の外生ダミーを用いて fit_ssm で推定する。

COVID one-year splitは、学習期間が2002年4月から2021年2月、評価期間が2021年3月から2023年5月であり、評価月数は27か月である。学習期間で post_stat_change は常に0であるため、select_nonconstant_exog により同変数は推定から除外される。したがって、この設定では後続統計接続後の水準補正を学習できない。

### 2.2 対数尺度から原系列への戻し方

SSMの forecast_ssm は、対数尺度の予測値に対して

\[
 \widehat{q}_t=\exp(\widehat{y}_t)
\]

を直接適用し、原系列 number_parcels の尺度で予測値を作成する。予測分散を用いた対数正規分布のバイアス補正、例えば \(\exp(\widehat{y}_t+\widehat{\sigma}_t^2/2)\) は実装されていない。したがって、「原系列への単純逆変換を用いた」と記載できるが、「対数変換によるバイアスを補正した」とは記載しない。

SARIMA/SARIMAXおよびNeuralForecast系の既存関数も、確認できる範囲では予測後に np.exp を適用している。ただし、論文本文で全モデルについて同一の変換処理を断定する場合は、各モデルの実装版を最終確認する。

### 2.3 評価指標とMASEの分母

RMSE、MAE、MAPE、MASEはいずれも原系列の number_parcels 尺度で計算される。MASEは1期ナイーブではなく、月次季節性に合わせた12期差分を学習系列から作る。学習系列を \(q_1,\ldots,q_n\) とすると、実装上の分母は

\[
 d_{12}=\frac{1}{n-12}\sum_{t=13}^{n}|q_t-q_{t-12}|
\]

であり、評価期間の平均絶対誤差をこの値で割る。本文では「MASEは学習期間における12か月季節ナイーブ誤差を分母とした」と記述する。評価指標の計算に評価期間の真値を使うのは、予測値との誤差を算出する段階だけである。

### 2.4 評価期間の情報条件と平滑化

SSMの固定分割予測は forecast_type='conditional' である。予測時には、学習済みパラメータを固定し、学習系列と評価期間の外生ダミーを結合する一方、評価期間の目的変数は NaN として smooth に渡す。その後、評価期間を予測するため、評価期間の観測値を平滑化に入力していない。外生ダミーの列選択は学習期間の変動性だけで決めている。この範囲では、SSMについて「学習期間のみでパラメータを推定し、評価期間の目的変数を予測時に使用していない」と記述できる。

fixed Bの評価期間（2024年1月から2026年2月）では、主分析と同じ5変数を列として用い、各月の既知外生ベクトルは

\[
 (\mathrm{hike\_dummy},\mathrm{covid\_main},\mathrm{covid\_wave1},
 \mathrm{covid\_2021},\mathrm{post\_stat\_change})=(0,0,0,0,1)
\]

である。これは予測期間の事後的な取扱個数を与えることではなく、指定した期間ダミーの値を既知とする条件付き予測である。

なお、比較用のSARIMAXグリッド最良モデルは、Notebook上で収束した候補の評価RMSEにより選択されている。この選択は固定された評価期間の誤差をモデル選択にも用いるため、SSMのfixed B予測に対する「評価期間を一切使わない」という説明をSARIMAXグリッド最良モデルへそのまま拡張してはならない。論文本文では、同モデルを参考比較に留めるか、選択過程を明示する必要がある。

## 3. 第3章に追記できる記述案

> 状態ベクトルはレベル、傾きおよび11個の季節状態から構成し、季節周期を12か月とした。季節状態には和がゼロとなるダミー変数型の遷移を与え、観測誤差、レベルノイズ、傾きノイズおよび季節ノイズの分散を共分散行列の対角要素として推定した。初期状態はdiffuse initializationにより扱った。推定はstatsmodelsのMLEModelに基づく尤度最大化であり、分散パラメータは正値制約のため二乗変換した。
>
> ここで、コード上の slope_noise は傾きノイズの標準偏差ではなく、状態共分散行列に入る分散パラメータである。各ノイズの分布や独立性については、本文では共分散行列の設定範囲を超えて断定せず、対角共分散を仮定した状態空間表現として記述する。

## 4. 第6章に追記できる記述案

> 予測モデルは学習期間の対数系列を用いて推定し、予測された対数値を指数関数で原系列へ戻した。予測分散を用いた対数正規バイアス補正は行っていない。評価は原系列の取扱個数尺度で行い、MASEの分母には学習期間の12か月季節ナイーブ誤差を用いた。
>
> 状態空間モデルの評価は、予測期間の外生ダミーを既知として与える条件付き予測である。固定分割では評価期間の目的変数を欠測として予測状態を計算しており、評価後に得られた観測値は誤差指標の算出にのみ用いた。したがって、この結果は外生ダミーを未知とする無条件の将来予測性能を直接示すものではない。COVID one-year設定では、post_stat_change が学習期間で一定であったため推定から除外され、同ダミーによる接続後の水準補正を学習できない点に留意する。

## 5. 現時点で未確認・本文に書くべきでない事項

次の事項は、現状のコードと出力だけでは断定しない。

1. 観測誤差・各状態ノイズが「互いに独立な正規分布」に従うという断定。コードから確実に言えるのは、対角共分散を設定し、同時点の共分散パラメータを推定していないことである。
2. 最適化法をプロジェクト側で明示指定したという記述。現状はstatsmodelsの既定法に依存しているため、本文で L-BFGS と固定的に書く場合はバージョンと既定値を併記する。
3. statsmodelsの収束判定が特定の勾配ノルムや尤度差の閾値に基づくという記述。実装は converged と warnflag を結果から読み取るだけで、独自閾値を設定していない。
4. \(2.26\times10^{-11}\) を傾きノイズの標準偏差、または標準誤差とする記述。これは state_cov[1,1] の分散推定値である。
5. SSM予測に対する対数正規バイアス補正の実施。実装は指数関数の単純逆変換である。
6. MASEの分母を1期ナイーブ誤差とする記述。実装は12期差分の学習期間平均絶対誤差である。
7. SARIMAXグリッド最良モデルを、評価期間をモデル選択に使わない完全な外部テスト結果として扱う記述。既存Notebookでは候補の評価RMSEで選択している。
8. COVID one-year設定で後続統計ダミーの効果を推定・予測したという記述。学習期間で一定のため、同変数は除外されている。

## 6. 確認に用いた主なファイル

- モデル定義：src/ssm_models.py
- SSM推定・予測：src/forecasting/ssm.py
- 指標計算：src/forecasting/evaluation.py
- 固定分割：src/forecasting/splits.py
- イベント期間：src/forecasting/forecast_specs.py、src/features.py
- 対数変換：src/data_loader.py
- 固定B Notebook：notebooks/forecasting/03_ssm_forecast.ipynb、notebooks/forecasting/10_fixed_slope_ssm_forecast.ipynb
- COVID one-year Notebook：notebooks/forecasting/11_covid_one_year_forecast.ipynb
- 既存メトリクス：output/forecasts/metrics/fixed_b_ssm_slope_comparison.csv、output/forecasts/metrics/covid_one_year_forecast_metrics.csv
- 既存収束情報：output/forecasts/metrics/ssm_fit_summary.csv、output/forecasts/metrics/covid_one_year_fit_summary.csv
- 既存分散・係数：output/sensitivity/fixed_slope_coefficients.csv

## 7. Git状態

調査後の git status --short は次のとおりである。

~~~text
 M paper_jsce/main.pdf
 M paper_jsce/main.tex
?? paper_jsce/reviewer_comment_response_plan.md
?? paper_jsce/model_and_forecast_definition_check.md
~~~

既存の main.tex、main.pdf、reviewer_comment_response_plan.md の変更状態は今回の調査で変更していない。
