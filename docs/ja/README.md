# PAL（日本語文書）

この文書群は、これまでの研究の経緯・結果・原稿を**参照しない**前提で書かれている。前提として認めるのは次の2点だけ。

1. アイデア：アーキテクチャ・学習データ・デコード方式の異なる複数の音声認識器（ASR）を並べ、既知のプロンプトを読んだ学習者音声を各認識器に転写させる。
2. データ：`01_premises.md` に列挙した音声コーパス・人間の評定・既に得られている転写。

過去の相関値・パネル選定・図表・査読コメントは、この領域の設計判断には使わない（`03_design_protocol.md` の「既知にしない情報」を参照）。

| ファイル | 内容 |
|---|---|
| `01_premises.md` | 認める前提（アイデア、データ、計算資源）と、意図的に未知とする情報 |
| `02_questions_hypotheses.md` | 研究設問と反証可能な仮説 |
| `03_design_protocol.md` | 測定モデル、読み出し仕様、パネル採用規則、データの役割と開封順、統計手順、判定規則 |
| `04_preregistration_confirmatory.md` | 確認段階の事前登録テンプレート（開封前に記入・コミットする） |
| `05_workplan.md` | 段階と関門 |
| `06_stage1_dev_report.md` | 開発段階（SO762 train split のみ）の実行結果（`pipeline/stage1_dev.py` が生成） |
| `paper/` | 新原稿（`make_numbers.py` → `numbers.tex`、`build.py` → `output/pal_icassp2027.pdf`） |
| `src/` | 既存コードに依存しない最小実装（`confirm.py` が確認段階） |
| `results/` | 生成物（JSON） |

実行：
```sh
GOP=/Volumes/Untitled/Prj/gop
$GOP/.venv/bin/python src/inventory.py
OPENBLAS_NUM_THREADS=1 $GOP/.venv/bin/python src/stage1_dev.py
```
