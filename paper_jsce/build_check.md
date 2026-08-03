# ビルド・様式確認記録

## 参照資料

- 土木学会論文集編集委員会「和文原稿作成例（2022年1月1日改訂）」：<https://committees.jsce.or.jp/jjsce/system/files/style_wabun_20220101_0.pdf>
- 土木学会論文集編集委員会「投稿要項」：<https://committees.jsce.or.jp/jjsce/node/71>
- 土木学会論文集編集委員会「原稿作成上の注意」：<https://committees.jsce.or.jp/jjsce/notes>
- 土木学会論文集編集委員会「PDFファイルの作成の手引」：<https://next.committees.jsce.or.jp/jjsce/ptebiki>

`docs/jsce_submission_rules_only.md` は作業領域内では確認できなかった。一方，2026年8月3日にユーザー指定の `C:\Users\fugat\Downloads\style_wabun_20220101_0.pdf` を直接確認した。公式公開版と同じ3ページの作成例であり，本文の余白，タイトル部，見出し，図表，REFERENCESおよび英文要旨の規定を本環境へ再照合した。参照PDFは作業ディレクトリへ複製していない。

## `main.tex` で反映した事項

| 項目 | 設定 |
|---|---|
| 用紙 | A4 |
| 本文余白 | 上19 mm，下24 mm，左右20 mm |
| タイトル部 | 1段組，左右30 mm相当の幅（本文より左右10 mmずつ狭い） |
| 本文 | 2段組，段間6 mm，和文10 pt相当 |
| タイトル | ゴシック体，20 pt相当 |
| 著者名 | 明朝体，12 pt相当 |
| 所属・和文要旨 | 明朝体，9 pt相当 |
| 見出し | 章：ゴシック体11 pt相当，節・項：ゴシック体10 pt相当 |
| 和文要旨 | 350字以内の仮文 |
| キーワード | 5語の仮置き，イタリック体 |
| 参考文献 | 原稿末尾に `REFERENCES` を置き，BibTeXで出力 |
| 英文要旨 | 最終部を1段組に戻し，左右30 mm相当の幅で配置。300語以内の仮文 |
| Received / Accepted | 初回投稿用の`?`を最終ページ右寄せで仮置き |

## ビルド確認

実行ディレクトリ：`paper_jsce/`

```powershell
uplatex main.tex
upbibtex main
uplatex main.tex
uplatex main.tex
dvipdfmx main.dvi
```

結果：2026年8月3日にTeX Live 2025で正常終了した。`main.pdf` はA4・3ページ・約94 KBであり，`pdffonts` により使用フォントがすべて埋め込み済みであることを確認した。

Computer Modernの利用可能な近傍サイズへの置換警告は出るが，未定義参照・コンパイルエラーは最終回のビルドでは出ていない。英文要旨を最終ページの2段組本文・REFERENCESの後に置くため，本文部には `multicols` を使用している。現時点の本文は章ごとの仮注記のみのため，英文要旨が独立した第3ページとなる。実際の原稿量・図表を入れた段階で，最終ページの左右段の高さと英文要旨直前の約10 mmの空白を目視調整する。

## VS Code / LaTeX Workshop

プロジェクト直下の `.vscode/settings.json` に，`uplatex -> upbibtex -> uplatex x2 -> dvipdfmx` を唯一のrecipeかつ既定recipeとして設定した。`main.tex` にある `% !TeX program = uplatex` がrecipeより優先されて1回だけ実行されないよう，LaTeX Workshopのmagic commentによるビルド指定は無効化している。

`.vscode/settings.json` はルート `.gitignore` の例外としてGit管理し，このrecipeをプロジェクト利用者間で共有する。その他の `.vscode/` 配下のローカル設定は引き続きGit管理しない。

自動ビルドおよび自動cleanは無効化し，保存中のファイル変更とビルドが競合しないようにした。VS Codeでは `paper_jsce/main.tex` を開いた状態で「Build LaTeX project」を実行する。補助ファイルの削除は，LaTeX Workshopの「Clean up auxiliary files」から手動で実行でき，`*.aux`，`*.bbl`，`*.blg`，`*.dvi`，`*.log`，`*.synctex.gz` のみを対象とする。clean方式は `latexmk` ではなくglob方式である。

## 投稿前に確認する事項

1. 投稿先が通常号か特集号かを確定し，対象小委員会の個別要項が通常号要項より優先しないか確認する。
2. 著者氏名，所属，正会員等の区分，連絡著者のE-mailアドレスを確定する。
3. カテゴリー「土木計画学（方法と技術）」の最新の投稿画面上の選択肢と，ページ目標10ページとの整合を確認する。公式の一般上限は20ページであり，10ページは本研究の自主目標である。
4. 原稿作成例はWordベースであり，このLaTeX環境は寸法と階層を近似したものである。和文フォントの実測値，1段48行・1行25字の達成状況，見出し前後の空き，キャプションの体裁をPDF上で目視確認する。
5. 図表は初出箇所と同じページに置き，図は下，表は上にキャプションを置く。図表内の文字はキャプションの9 ptより小さくしない。
6. 参考文献は出現順に整理し，和文文献には英訳を角括弧内で併記する。実際の引用に移行したら，`main.tex` の暫定的な `\\nocite` を削除する。
7. 投稿PDFでは全フォントを埋め込み，10 MB以下，通常の論文は20ページ以内とする。パスワード，しおり，サムネール，外部リンクは設定しない。
8. 和文本文では「，」「．」を使用し，機種依存文字・半角カタカナ・JIS第2水準を超える漢字を避ける。
