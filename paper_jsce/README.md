# 土木学会論文集向け和文論文ドラフト

`main.tex` は，土木学会論文集の和文原稿作成例を参考にした暫定的なLaTeX作業環境です。公式配布のWord原稿作成例をLaTeX化したものではなく，投稿直前には最新版の公式資料と照合してください。

現時点では，本文を執筆せず，章構成，和文・英文要旨の仮文，参考文献処理，および図表の配置先だけを用意しています。
最終ページの`Received`・`Accepted`欄は初回投稿用の`?`の仮置きです。

## 著者情報の仮置き

著者名は寺嶋風雅，赤羽根悠吾，冬木拓実，樋口知之の仮配置である。所属，会員区分，E-mail，Corresponding Authorは未確定のため，`main.tex` では要確認と明示している。英文著者名のローマ字表記（Fuga TERASHIMA，Yugo AKABANE，Takumi FUYUKI，Tomoyuki HIGUCHI）は仮置きであり，投稿前に本人・所属の正式表記を確認する。

## 構成

- `main.tex`：和文原稿の最小ドラフト
- `references.bib`：暫定的なBibTeXデータベース
- `figures/`：投稿用図の配置先
- `tables/`：投稿用表の配置先
- `build_check.md`：ビルド結果，様式対応，未確認事項

## ビルド

TeX Liveの`uplatex`，`upbibtex`，`dvipdfmx`を使用します。`paper_jsce/` をカレントディレクトリとして，次を実行してください。

```powershell
uplatex main.tex
upbibtex main
uplatex main.tex
uplatex main.tex
dvipdfmx main.dvi
```

生成される `main.pdf` は作業用確認PDFです。投稿前には，`build_check.md` の確認項目を満たしていることを確認してください。

## 執筆時の注意

- 和文本文では句読点として「，」「．」を用います。
- 図は下，表は上にキャプションを置き，初出の本文と同じページに配置します。
- `post_stat_change` は需要イベントではなく，統計接続に伴う水準補正として記述します。
- 予測評価は構造分解を補う限定的検証とし，Autoformer等の詳細は本文に入れません。
