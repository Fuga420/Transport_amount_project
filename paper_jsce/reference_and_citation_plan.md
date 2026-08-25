# 参考文献リストと本文中引用の整備方針

## 0. 調査範囲と現状

本メモは、現行稿における参考文献と本文中引用の整理方針を定めるものである。`main.tex`、`references.bib`、旧稿の本文・参考文献、既存のデータ接続・モデル定義メモを確認した。今回は `main.tex` と `references.bib` を変更しない。

現行稿の本文には `\cite{...}` がまだなく、末尾で `\nocite{harvey1989,durbin2012,mlit2026}` を用いている。したがって、現状の参考文献リストは「本文で根拠を示した文献」ではなく、仮置きの文献を含む状態である。`paper_jsce/remaining_issues_action_plan.md` はリポジトリ内で確認できなかったため、同ファイルに依存する判断は行っていない。

現行の `references.bib` は次の3件である。

| キー | 現在の内容 | 判定 |
|---|---|---|
| `harvey1989` | Harvey, *Forecasting, Structural Time Series Models and the Kalman Filter*, Cambridge University Press, 1989 | 状態空間モデルの基本文献として有力。ただし旧稿の `harvey1990` との刊年・版の対応を要確認。 |
| `durbin2012` | Durbin and Koopman, *Time Series Analysis by State Space Methods*, 2nd ed., Oxford University Press, 2012 | 状態空間表現、カルマンフィルタ、尤度推定の根拠として使用候補。書誌情報を最終確認する。 |
| `mlit2026` | `Monthly Economic Cargo Statistics` とする英語の仮エントリ | `Placeholder bibliographic record` と明記された仮置きであり、削除して正式な国土交通省資料2件に置換する。 |

## 1. 旧稿から確認できる文献

旧稿の参考文献は `paper/paper.tex` の `thebibliography`、`paper_2/paper_2.tex` および `paper_2/paper_2 copy.tex` の `thebibliography` から抽出した。日本語の著者名・題名については、UTF-8として読める旧稿本文に基づいて記載している。URL、DOI、取得日は旧稿にないものが多いため、補完せず要確認とする。

| キー | 著者・タイトル・年（旧稿記載） | 旧稿での使われ方 | 現行稿での扱い |
|---|---|---|---|
| `akahane2024` | 赤羽根悠悟（2024）「日本国内におけるトラック輸送量の時系列予測と分析」，中央大学理工学部卒業論文 | 宅配便取扱個数の長期月次系列とSARIMAによる先行検討の説明 | 現行稿の問題設定・旧稿からの位置づけに引用候補。学位論文の正式な学位種別、公開URL、著者表記を要確認。 |
| `akaike1974` | Akaike, H. (1974). “A new look at the statistical model identification.” *IEEE Transactions on Automatic Control*, 19(6), 716--723. | AICの説明 | AICを本文で定義・使用する場合に継承候補。誌名、巻号、頁は旧稿記載を基に最終確認。 |
| `alqatawna2023` | Alqatawna, A., Abu-Salih, B., Obeid, N., and Almiani, M. (2023). “Incorporating time-series forecasting techniques to predict logistics companies' staffing needs and order volume.” *Computation*, 11(7), 141. | SARIMAX・物流需要予測の背景 | 現行稿では予測手法の詳細を扱わないため、SARIMAXを本文で1文だけ紹介する場合に限る。採用するなら誌面・DOIを要確認。 |
| `brodersen2015` | Brodersen et al. (2015). “Inferring causal impact using Bayesian structural time-series models.” *The Annals of Applied Statistics*, 9(1), 247--274. | 旧稿ではコメントアウトされた因果推論文献 | 本研究は因果効果を識別しないため削除候補。因果推論を導入しない限り引用しない。 |
| `cleveland1990` | Cleveland, Cleveland, McRae, and Terpenning (1990). “STL: A seasonal-trend decomposition procedure based on Loess.” *Journal of Official Statistics*, 6(1), 3--73. | 旧稿のSTL分解図・比較の説明 | 現行稿の主仕様は状態空間モデルであり、STLを本文で扱わないため削除候補。 |
| `durbin2012` | Durbin, J. and Koopman, S. J. (2012). *Time Series Analysis by State Space Methods*, 2nd ed. Oxford University Press. | 状態空間モデルの標準文献 | 現行稿の第3章で継承する。出版社・版・刊年を確認後に使用。 |
| `elsokkary2022` | Elsokkary et al. (2022). “Crowdsourced last mile delivery: Collaborative workforce assignment.” *SSRN Electronic Journal*. | ラストワンマイルの課題背景 | 現行稿で労働力不足等を具体的に述べる場合のみ候補。SSRN番号、URL、公開日を要確認。 |
| `ghareeb2023` | Ghareeb (2023). “Time series forecasting of stock price for maritime shipping company in COVID-19 period using multi-step long short-term memory (LSTM) networks.” *Proceedings of the 17th International Conference on Business Excellence 2023*, 1728--1747. | 旧稿コピーでLSTM予測の例として記載 | Autoformer・深層学習を現行本文で扱わないため削除候補。 |
| `harvey1990` | Harvey, A. C. (1990). *Forecasting, Structural Time Series Models and the Kalman Filter*. Cambridge University Press. | 旧稿ではコメントアウトを含む状態空間モデルの基本文献 | 現行の `harvey1989` と同一書の版・刊年を確認し、キーを一つに統一する。両方を併記しない。 |
| `hyndman2021` | Hyndman, R. J. and Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd ed. OTexts. | 旧稿ではコメントアウトされた予測の基礎文献 | MASEや予測評価の一般説明に使う場合の補助候補。URLとアクセス日を要確認。 |
| `kaplan2011` | Kaplan, Türkay, Karas{"o}zen, and Biegler (2011). “Optimization of supply chain systems with price elasticity of demand.” *INFORMS Journal on Computing*, 23(4), 557--568. | 価格弾力性・供給網最適化の背景 | 現行稿は運賃改定の因果的価格弾力性を推定しないため、原則削除候補。 |
| `kitagawa2005` | 北川源四郎（2005）『時系列解析入門』，岩波書店 | 状態空間・時系列解析の日本語入門文献 | 第3章の日本語の基本文献として候補。書名・刊年・版を出版社情報で確認する。 |
| `kunitomo1985` | 国友直人（1985）『時系列モデル入門』，東京大学出版会 | 時系列モデル一般の導入 | 北川・Durbin--Koopmanと役割が重なるため、本文の説明量に余裕がある場合のみ候補。書誌情報を要確認。 |
| `lim2021` | Lim and Zohren (2021). “Time-series forecasting with deep learning: a survey.” *Philosophical Transactions of the Royal Society A*, 379(2194), 20200209. | 深層学習予測の背景 | 現行稿では深層学習手法を比較対象にしないため削除候補。 |
| `morganti2014` | Morganti et al. (2014). “The impact of e-commerce on final deliveries: alternative parcel delivery services in France and Germany.” *Transportation Research Procedia*, 4, 178--190. | EC拡大とラストワンマイルの背景 | 第1章でECと宅配便の関係を具体的に述べる場合に限る。日本の系列への直接の根拠ではないため、表現を一般論に留める。DOI等を要確認。 |
| `oum1992` | Oum, Waters, and Yong (1992). “Concepts of price elasticities of transport demand and recent empirical estimates.” *Journal of Transport Economics and Policy*, 26(2), 139--154. | 運賃・価格弾力性の背景 | 現行稿は価格弾力性を推定しないため削除候補。 |
| `ramos2024` | Ramos, Valladão, and Street (2024). *Time Series Analysis by State Space Learning*. arXiv:2408.09120. | 状態空間学習の補足 | 現行稿の実装・推定は古典的状態空間モデルであり、本文で扱わないため削除候補。採用する場合はarXivの正式題名・著者表記を要確認。 |
| `seabold2010` | Seabold, S. and Perktold, J. (2010). “Statsmodels: Econometric and statistical modeling with Python.” In *9th Python in Science Conference*. | statsmodels利用のソフトウェア根拠 | 第3章で使用ソフトウェアを明記する場合に継承候補。会議録の頁、URL、DOIの有無を要確認。 |
| `taylor2018` | Taylor and Letham (2018). “Forecasting at scale.” *The American Statistician*, 72(1), 37--45. | Prophetの背景 | 現行稿でProphetを詳述しないため削除候補。 |
| `tomiyama2024` | 富山貴史・瀬貫雄介・菊池明飛・Sun Shurong・北原知就・伊豆永洋一（2024）「状態空間モデルを用いたECサイトにおけるセール効果の分析」，『計算機統計学』37(1)，43--52 | ECサイトに対する状態空間モデルの関連研究 | 第1章で日本語の関連研究として紹介する場合に候補。著者表記、掲載誌の正式表記、DOIを要確認。 |
| `valis2017` | Vališ, Mazurkiewicz, and Forbelská (2017). “Modelling of a Transport Belt Degradation Using State Space Model.” IEEE IEEM, 136--140. | 状態空間モデルの応用例 | 宅配便取扱個数と直接関係せず、現行稿で紹介予定がないため削除候補。 |
| `vilko2024` | Vilko and Hallikas (2024). “Impact of COVID-19 on logistics sector companies.” *International Journal of Industrial Engineering and Operations Management*, 6(1), 25--42. | COVID-19と物流企業の背景 | 第1章で物流部門全体の背景を述べる場合の任意候補。掲載誌・URL・DOIを要確認。因果効果の根拠としては使わない。 |
| `wang2020` | 旧稿のエントリは著者・題名等が空欄 | 内容不明の未完エントリ | 削除候補。出典を特定できるまで引用しない。 |
| `wago2008` | 和合肇訳（2008）『状態空間時系列分析入門』，シーエーピー出版 | `paper_2`で状態空間時系列の日本語参考書として使用 | 北川・Durbin--Koopmanとの重複を確認し、採用する場合のみ正式な原著者・書名・版を要確認。 |

## 2. 現行稿で追加が必要な文献候補

以下は、現行本文の記述に対応する候補である。正式な書誌情報を確認できるまでは `references.bib` に追加しない。

| キー案 | 種別 | 正式書誌情報の候補 | URL・アクセス日 | 未確認事項 |
|---|---|---|---|---|
| `harvey1989`（または `harvey1990`） | 書籍 | A. C. Harvey, *Forecasting, Structural Time Series Models and the Kalman Filter*, Cambridge University Press | 出版社・図書館書誌を要確認 | 1989年版と旧稿の1990年表記の関係、表記（大文字・版）を統一する。 |
| `durbin2012` | 書籍 | J. Durbin and S. J. Koopman, *Time Series Analysis by State Space Methods*, 2nd ed., Oxford University Press | 出版社・図書館書誌を要確認 | 現行エントリの版、刊年、都市表記を最終確認する。 |
| `kitagawa2005` | 書籍 | 北川源四郎『時系列解析入門』，岩波書店 | 岩波書店の書誌URL・アクセス日を要確認 | 旧稿の著者名・タイトルが正式書誌と一致するか。 |
| `wago2008` | 書籍（翻訳） | 和合肇訳『状態空間時系列分析入門』，シーエーピー出版 | 出版社書誌・アクセス日を要確認 | 原著者・原題、翻訳版の刊年、正式な書名を確認する。 |
| `seabold2010` | 会議論文 | S. Seabold and J. Perktold, “Statsmodels: Econometric and statistical modeling with Python,” *9th Python in Science Conference* | SciPy proceedingsのURL・アクセス日を要確認 | 頁、会議開催地、公開URLの有無。本文ではソフトウェアの出典としてのみ使用する。 |
| `hyndman2006` | 学術論文 | R. J. Hyndman and A. B. Koehler, “Another look at measures of forecast accuracy,” *International Journal of Forecasting*, 22(4), 679--688 | DOI・出版社URL・アクセス日を要確認 | MASEの原典として採用するか、誌名・巻号・頁・DOIを確認する。 |
| `hyndman2021` | オンライン教科書 | R. J. Hyndman and G. Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed. | `https://otexts.com/fpp3/` とアクセス日を要確認 | MASEの定義の補助として使う場合のみ採用する。 |
| `akaike1974` | 学術論文 | H. Akaike, “A new look at the statistical model identification,” *IEEE Transactions on Automatic Control*, 19(6), 716--723 | IEEE XploreのURL・DOI・アクセス日を要確認 | AICを本文で説明する場合に使用する。 |
| `schwarz1978` | 学術論文 | G. Schwarz, “Estimating the dimension of a model,” *The Annals of Statistics*, 6(2), 461--464 | Project Euclid等のURL・DOI・アクセス日を要確認 | BICの原典を引用するか、AIC/BICを単に比較指標として記すかを決める。 |
| `mlit_truck_transport` | 政府統計 | 国土交通省「トラック輸送情報」内の宅配便貨物取扱個数 | 国土交通省の正式統計ページURL・アクセス日を要確認 | 統計表の正式名称、担当部署、対象事業者、公開期間、取得日。 |
| `mlit_monthly_economic` | 政府統計 | 国土交通省「国土交通月例経済」（交通分野）の宅配便貨物取扱個数 | 国土交通省の正式ページURL・アクセス日を要確認 | 統計表の正式名称、後続統計としての位置づけ、単位、対象事業者。 |
| `mhlw_covid5rui` | 政府公表資料 | 厚生労働省「新型コロナウイルス感染症の感染症法上の位置づけの変更について」 | 厚生労働省の正式ページURL・アクセス日を要確認 | 2023年5月8日の5類移行を示す正式資料、公開日・ページ題名。 |
| `akahane2024` | 学位論文 | 赤羽根悠悟（2024）「日本国内におけるトラック輸送量の時系列予測と分析」 | 大学リポジトリ等のURL・アクセス日を要確認 | 論文種別、所属、公開状況、著者名のローマ字表記。 |
| `tomiyama2024` | 学術論文 | 富山ら（2024）「状態空間モデルを用いたECサイトにおけるセール効果の分析」 | 学会・出版社のURL、DOI、アクセス日を要確認 | 著者名の正式表記、掲載誌・巻号・頁。 |
| `morganti2014` / `vilko2024` | 学術論文 | EC・ラストワンマイルまたはCOVID-19と物流企業に関する旧稿由来文献 | 出版社URL・アクセス日を要確認 | 第1章の背景文をどこまで具体化するかを決め、必要な文献だけ残す。 |

## 3. 本文中引用の挿入位置

現行稿の本文は、主張を弱めた表現が多く、すべての一般論に引用を付す必要はない。統計資料・既存研究・方法論の出典が必要な箇所を優先する。

| 章 | 本文中の記述 | 引用すべき文献 | 理由 | 要確認事項 |
|---|---|---|---|---|
| 第1章 | 宅配便取扱個数、EC拡大、ラストワンマイル等を物流背景として述べる箇所 | `morganti2014`、必要に応じて `elsokkary2022`、`vilko2024` | 背景の一般論に根拠を与える。ただし日本の宅配便系列への直接的根拠とは区別する。 | 旧稿の主張を現行稿で残すか、より一般的な表現に弱めるか。 |
| 第1章 | 旧稿が宅配便取扱個数の長期系列を構築しSARIMAで分析したという位置づけ | `akahane2024` | 旧稿・先行検討の出典を明示する。旧稿の数値や古いイベント定義は再利用しない。 | 学位論文の公開URLと正式な学位種別。 |
| 第1章 | 状態空間モデルでトレンド・季節性・イベント期間の水準差を分ける意義 | `harvey1989`、`durbin2012`、`kitagawa2005`、必要に応じて `tomiyama2024` | 方法論の背景と、関連する応用研究を区別して示す。 | どの文献が本研究の直接の関連研究かを確定する。 |
| 第2章 | 旧統計「トラック輸送情報」の名称、期間、対象範囲、単位 | `mlit_truck_transport` | 原統計の正式出典である。 | 統計表の正式タイトル、URL、取得日、対象事業者の記載箇所。 |
| 第2章 | 後続統計「国土交通月例経済」（交通分野）の名称、切替月、対象範囲 | `mlit_monthly_economic` | 接続系列の後半の原統計を示す。 | 正式な統計表名、公開ページ、単位、対象事業者。 |
| 第2章 | COVID期ダミーの終点を5類移行時期までとする説明 | `mhlw_covid5rui` | 2023年5月の制度上の節目の公的根拠を示す。 | 厚生労働省資料の正式タイトル、公開日、URL。期間ダミー自体はモデル上の操作的定義であることを併記する。 |
| 第2章 | 2018年4月の旧統計内の集計方法変更 | `mlit_truck_transport` | 同じ原統計の注記・脚注を根拠にする。 | 変更の正確な内容、該当表の脚注、引用ページ。 |
| 第3章 | 状態空間表現、局所線形トレンド、カルマンフィルタ、尤度推定 | `harvey1989`、`durbin2012`、必要に応じて `kitagawa2005` | 数式と方法の標準的な出典である。 | Harveyの刊年・キーを旧稿と統一する。 |
| 第3章 | 12か月の季節状態、和ゼロ制約、diffuse initialization | `durbin2012`、`harvey1989` | 状態初期化・季節状態の一般的な方法論を支える。 | 現在の実装の特殊な季節遷移と文献の定義が一致する範囲を確認する。 |
| 第3章 | statsmodelsのMLEModelを使用した尤度最大化 | `seabold2010` | 使用ソフトウェアの出典を明示する。 | パッケージ版、会議録頁、公式ドキュメントURL。本文ではコード名・CSV名を出さない。 |
| 第3章 | AIC・BICをモデル比較指標として用いる説明 | `akaike1974`、必要に応じて `schwarz1978` | 情報量基準の原典を示す。 | TR2は未収束のため正式比較に使わないことを本文で明記する。 |
| 第6章 | RMSE、MAE、MAPE、MASEと、12か月季節ナイーブ誤差をMASE分母とする定義 | `hyndman2006`、補助的に `hyndman2021` | MASEの分母・指標定義の根拠を示す。 | 旧稿にないMASE原典を正式確認する。 |
| 第6章 | 無条件予測と、評価期間の外生ダミーを既知とする条件付き予測の区別 | `durbin2012`（方法論の補助） | 予測情報条件の説明を状態空間予測の文脈に置く。 | 本文の条件付き予測は本研究の評価設計であり、文献の定義を過度に一般化しない。 |
| 第7章 | 統計接続の非同質性、イベントダミーの非因果性、残差自己相関 | 第2章・第4章の原統計引用、方法論引用を再参照 | 新しい結果ではなく、既に引用した出典と分析上の留保をまとめる。 | 第7章に同じ引用を重複して付す必要性を最終確認する。 |

## 4. `references.bib` に最終的に残す文献案

### 優先して残す候補

次の文献は、現行本文の主張に直接対応するため、正式情報を確認できたものから残す。

1. `harvey1989` または `harvey1990`：状態空間モデル・局所線形トレンドの基本文献。旧稿との刊年差を解消し、一方のキーだけを使用する。
2. `durbin2012`：状態空間モデル、カルマンフィルタ、尤度推定。
3. `seabold2010`：statsmodelsをソフトウェア出典として引用する場合。
4. `akaike1974`：AICを本文で定義する場合。BICの原典を引用するなら `schwarz1978` も追加する。
5. `hyndman2006`：MASEの定義を引用する場合。一般的な予測指標の説明を補う場合のみ `hyndman2021` を追加する。
6. `mlit_truck_transport`、`mlit_monthly_economic`：旧統計・後続統計の政府資料。現行の `mlit2026` はこの2件に置換する。
7. `mhlw_covid5rui`：COVID-19の5類移行時期を公的資料で示す場合。

### 現行の問題設定を説明する場合の条件付き候補

`akahane2024`、`kitagawa2005`、`tomiyama2024` は、第1章・第3章で実際に言及する場合に残す。EC・物流背景を具体的に書く場合のみ `morganti2014` または `vilko2024` を採用し、一般論だけに留める場合は無理に増やさない。`wago2008` と `kunitomo1985` は、北川・Durbin--Koopmanと役割が重なるため、紙幅と日本語文献の必要性を見て一方または両方を選択する。

### 削除・置換候補

- `mlit2026`：仮置きの英語タイトルと `Placeholder` 注記を含むため、正式な政府資料キーへ置換する。
- `cleveland1990`：現行稿でSTLを扱わないため削除する。
- `brodersen2015`：因果推論を行わないため削除する。
- `lim2021`、`taylor2018`、`ghareeb2023`、`ramos2024`：深層学習・Prophet・State Space Learningの詳細を本文に入れないため削除する。
- `kaplan2011`、`oum1992`：価格弾力性を推定・議論しないため削除する。
- `valis2017`：宅配便系列との関係が薄く、現行稿で使用しないため削除する。
- `wang2020`：書誌情報が空欄であり、出典を特定できるまで削除する。
- `alqatawna2023`：SARIMAXの参考比較を本文に1文残す場合だけ継承し、それ以外は削除する。

## 5. 本文に入れる引用コマンド案

現在の `jplain` と上付き番号の設定を前提に、本文では次のような位置に引用を置く。キーは `references.bib` の確定後に合わせる。

```tex
状態空間モデルの標準的な表現\cite{harvey1989,durbin2012}を用いる。
```

```tex
日本語の時系列解析の整理については北川\cite{kitagawa2005}を参照されたい。
```

```tex
推定には状態空間モデル実装の出典\cite{seabold2010}を付す。
```

```tex
AICおよびBICは情報量基準\cite{akaike1974,schwarz1978}として用いる。
```

```tex
MASEは季節ナイーブ誤差を分母とする定義\cite{hyndman2006}に従う。
```

```tex
旧統計の出典は国土交通省資料\cite{mlit_truck_transport}，後続統計の出典は同省資料\cite{mlit_monthly_economic}とする。
```

```tex
COVID-19の5類移行時期は厚生労働省の公表資料\cite{mhlw_covid5rui}を参照する。
```

旧稿の位置づけを明示する箇所では、次のようにする。

```tex
先行する宅配便取扱個数の分析\cite{akahane2024}を踏まえ、現行稿では統計接続後の補正とトレンド仕様の頑健性を扱う。
```

本文への引用を開始した後は、末尾の `\nocite{...}` を削除し、実際に本文で使用した文献だけを参考文献リストに出す。SARIMAXの参考比較を削除するなら、`alqatawna2023` の引用も不要である。

## 6. `references.bib` 反映前の確認事項

- Harveyの1989年版・1990年表記を、出版社または図書館書誌で確認し、キーと刊年を一つに統一する。
- `durbin2012` の版、刊年、出版社、必要ならISBNを確認する。
- 旧稿由来の日本語文献（`akahane2024`、`kitagawa2005`、`wago2008`、`tomiyama2024`）の著者名、題名、所属・出版社、学位種別、巻号頁を原資料で確認する。
- `seabold2010` の会議録頁、公開URL、DOIの有無を確認する。ソフトウェアのバージョンは本文または再現性メモで別途管理し、文献情報に混在させない。
- `hyndman2006` と、必要な場合の `schwarz1978` の正式な誌名、巻号、頁、DOIを確認する。
- 「トラック輸送情報」と「国土交通月例経済（交通分野）」について、統計表の正式名称、担当部署、対象範囲、単位、URL、取得日を確認する。旧統計の2018年4月注記も同じ資料の脚注で根拠付ける。
- 5類移行の根拠資料は、厚生労働省等の公的ページの題名、公開日（2023年5月8日を含む）、URL、取得日を確認する。
- `mlit2026` の仮エントリを残さない。正式資料を確認できない場合は、いったん引用自体を保留し、英語の仮題を参考文献に出さない。
- URLとアクセス日は推測で補わず、最終稿で実際に参照したページに合わせる。
- `references.bib` はUTF-8で保存し、日本語の文字化け、未閉じ括弧、未エスケープ文字、重複キーを検査する。
- 本文の引用キーとBibTeXキーの一対一対応、未引用文献の削除、`\nocite` の除去を確認する。
- JSCEの指定する参考文献書式（著者順、年、誌名、巻号頁、URL表記）と `jplain` の出力が一致するか、最終PDFで確認する。

## 7. `main.tex` 反映前の確認事項

- 第1章の背景・関連研究に、実際に残す文献だけを付す。旧稿の古い期間・数値・因果的表現は引用しても移植しない。
- 第2章の統計名・対象範囲・2018年4月の注記・COVID終点の説明に、それぞれ原資料の引用を置く。イベント期間そのものは操作的定義であり、公的資料の引用だけで因果性を補強しない。
- 第3章の観測方程式、局所線形トレンド、季節状態、diffuse initialization、MLEModelの説明に方法論・ソフトウェアの引用を置く。実装で確認できない分布や独立性を文献から推測して追記しない。
- AIC/BICの引用を置く場合も、未収束のTR2について情報量基準を正式な優劣比較に使わないという本文の留保を維持する。
- 第6章のMASE定義に原典を付す。単純逆変換、バイアス補正なし、学習期間限定推定、既知ダミーによる条件付き予測は本研究の実装事実として記載し、文献の一般論と混同しない。
- 本文でコード名、CSV名、Notebook名を出さず、引用は方法・データ・既存研究の出典に限定する。
- `\nocite` を削除した後に、参考文献が本文の引用順・表記と整合するかを `uplatex -> upbibtex -> uplatex -> uplatex -> dvipdfmx` で確認する。
- 著者情報、所属、E-mail、Received/Acceptedなどの未確定情報とは分けて、参考文献の要確認事項を最終チェックリストで管理する。

## 8. 今月投稿を前提とした最小対応案

1. 原統計2件とCOVID-19 5類移行の公的資料を確定する。
2. `harvey1989`（または `harvey1990`）、`durbin2012`、`seabold2010`、`akaike1974`、`hyndman2006` の書誌情報を確定する。
3. 第1章に `akahane2024` と、必要最小限の背景文献を追加する。
4. 第3章・第6章の方法記述に対応する引用を追加し、`\nocite` と未使用文献を削除する。
5. `mlit2026` を正式な政府資料キーに置換し、未確認の文献は本文・参考文献からいったん外す。
6. 最終ビルド後に、引用番号、参考文献の文字化け、URL・取得日、10ページ以内の紙幅を確認する。

## 9. このメモ作成時点の変更状況

この作業で作成・変更するファイルは本メモのみである。`main.tex`、`references.bib`、`src/`、`notebooks/`、`output/`、`docs/` は変更していない。

