# 04 確認段階の事前登録（記入済み、2026-09-13）

以下は、開発段階（`06_stage1_dev_report.md`、SO762 train のみ）の後、確認データを開封する前に固定した内容である。この文書のコミット後、確認データを各 1 回だけ解析する。開封後の変更は「記録欄」に追記の形でのみ行う。

## 凍結したもの（全段階共通）

- 読み出し：`03_design_protocol.md` §1（`pipeline/common.py` の `normalize`, `arpabet`, `espeak_ipa`, `error_rate`、等重み平均、空仮説＝誤り 1、上限 1）。
- パネル：`03` §2 の規則で採用した構成。英語は 28 構成（`results/data_inventory.json` の各コーパスの `admitted`）。中国語は再デコード転写のある 8 構成。性能による選別なし。
- 統計：Pearson r、話者（ALLSSTAR は talker）クラスタ percentile bootstrap、B=2,000、seed=20260913、対応比較は同一再標本。
- 固定した比較対象：最良単一認識器 = `hubert-large`（開発データの accuracy 相関で選択）。弱い 1/3 = 開発データの平均誤り率上位 9 構成（`results/stage1_dev.json` の `H7_dev.weakest_third`）。H3 の matched cross-family draw = 開発データで採択した 200 組（`H3_matched_draws`）。
- 除外規則：転写が欠けた発話は解析から除外し件数を記録する（欠落 0 を確認済み）。評定が欠ける発話はその評定の解析からのみ除外。

## 段階ごとの主要比較と判定規則

| 段階 | データ | 主要比較（1 つ） | 判定 | 副次（探索的、補正なし） |
|---|---|---|---|---|
| 確認 1 | SO762 test（2,500 発話、125 話者） | H2：パネル平均 − hubert-large、accuracy に対する paired 差 | 区間下限 > 0 で支持 | H1（パネル r の区間）、H7（弱い 1/3 − hubert-large）、H3（Whisper-7 vs matched cross draw 平均）、他評定、集約規則（中央値、最小、train 誤り率逆数重み）、部分パネル曲線 |
| 確認 2 | ERJ（3,800 発話、190 話者） | H4：segmental r − rhythm r（同一話者再標本、各評定は自分の発話上） | 区間下限 > 0 で支持 | segmental − intonation、各 r の区間、話者レベル |
| 確認 3 | EpaDB（3,160 発話、50 話者） | H1 再現：phrase score との r | 区間下限 > 0 で支持 | 話者レベル、hubert-large との paired 差 |
| 確認 4 | ALLSSTAR（100 talker、15 文） | H5：talker 平均パネルスコアと全条件平均正答率の r | 区間下限 > 0 で支持 | hubert-large との paired 差、Whisper-7 との差 |
| 確認 5 | OMPAL（1,768 発話、46 話者、再デコード 8 構成） | H6：声調チャネル（−平均 toneER）の tone 評定との r − consonant 評定との r（paired） | 区間下限 > 0 で支持 | 音節基底チャネル、基底一致音節に限った声調誤り、文字チャネル |

## 実行者・日時・コミット

- 実行：Claude（ユーザーの指示による）、2026-09-13。
- 開封前コミット：この文書を含むコミット（`git log` 参照）。

## 記録欄（開封後に追記）

（各段階の結果と判定は `../confirmatory-record.md` に記録した。）
