# 06 開発段階の結果（SO762 train split のみ）

パネル：採用規則を満たす 28 構成、等重み平均。発話 2500、話者 125。区間は話者クラスタ bootstrap（B=2000, seed=20260913）。**test split は読んでいない。**

## パネル平均と各評定の相関

| 評定 | r | 95% 区間 |
|---|---:|---|
| accuracy | 0.735 | [0.678, 0.777] |
| completeness | 0.104 | [0.033, 0.160] |
| fluency | 0.707 | [0.635, 0.761] |
| prosodic | 0.718 | [0.648, 0.773] |
| total | 0.748 | [0.687, 0.790] |

## 各認識器（accuracy との相関、平均誤り率、空出力数）

| 認識器 | family | 平均誤り率 | r(accuracy) | 空出力 |
|---|---|---:|---:|---:|
| hubert-large | ssl-ctc-librispeech | 0.247 | 0.695 | 0 |
| jasper | conv-ctc | 0.258 | 0.683 | 0 |
| vosk-small | kaldi-hybrid | 0.333 | 0.681 | 0 |
| wav2vec2-robust | ssl-ctc-librispeech | 0.232 | 0.679 | 0 |
| w2v2-xlsr-cv | ssl-ctc-other-domain | 0.226 | 0.673 | 0 |
| wav2vec2-base | ssl-ctc-librispeech | 0.314 | 0.669 | 0 |
| xlsr-1b-cv | ssl-ctc-other-domain | 0.248 | 0.660 | 0 |
| quartznet | conv-ctc | 0.256 | 0.653 | 1 |
| w2v2-swbd | ssl-ctc-other-domain | 0.312 | 0.648 | 0 |
| w2v2-large-lv60 | ssl-ctc-librispeech | 0.227 | 0.643 | 0 |
| espeak-phone | phone-recognizer | 0.384 | 0.642 | 0 |
| wavlm-large | ssl-ctc-librispeech | 0.299 | 0.631 | 0 |
| canary-1b | other-enc-dec | 0.160 | 0.625 | 0 |
| base.en | whisper | 0.211 | 0.607 | 0 |
| parakeet | transducer | 0.147 | 0.606 | 1 |
| tiny | whisper | 0.267 | 0.605 | 0 |
| tiny.en | whisper | 0.256 | 0.604 | 0 |
| small.en | whisper | 0.174 | 0.604 | 0 |
| distil-small.en | whisper | 0.183 | 0.603 | 0 |
| distil-large-v3 | whisper | 0.141 | 0.600 | 0 |
| crisperwhisper | whisper | 0.122 | 0.592 | 0 |
| atc-w2v2 | ssl-ctc-other-domain | 0.346 | 0.577 | 1 |
| moonshine-base | other-enc-dec | 0.265 | 0.570 | 187 |
| qwen2audio | speech-llm | 0.131 | 0.530 | 0 |
| seamless-m4t-v2 | other-enc-dec | 0.238 | 0.517 | 0 |
| sphinx-enus | gmm-hmm | 0.649 | 0.495 | 0 |
| allosaurus-eng | phone-recognizer | 0.702 | 0.476 | 0 |
| atc-xlsr | ssl-ctc-other-domain | 0.563 | 0.408 | 0 |

## H2（開発版）：パネル vs 同じ split で選んだ最良単一認識器

最良単一 = `hubert-large`（r=0.695）、パネル r=0.735、差 +0.039 [+0.024, +0.057]。単一認識器の選択が同じデータ上なので、この差は確認段階で固定した認識器で再検証する。

## H7（開発版）：弱い 1/3 のパネル vs 強い 1/3 のパネル

弱い 1/3（9 構成）r=0.714 [0.659, 0.755]、強い 1/3 r=0.689、弱パネル − 最良単一 = +0.019 [+0.002, +0.038]。

## 集約の効果（ランダム部分パネル、accuracy）

| k | 平均 r | 5–95 パーセンタイル |
|---:|---:|---|
| 1 | 0.604 | 0.408–0.695 |
| 2 | 0.666 | 0.612–0.714 |
| 4 | 0.701 | 0.676–0.720 |
| 8 | 0.721 | 0.706–0.736 |
| 16 | 0.730 | 0.723–0.738 |
| 28 | 0.735 | 0.735–0.735 |

## H3（開発版）：同一 family vs 規模・強さを揃えた cross-family

| family | k | 同一 family r | cross 平均 r | 差（cross−same） | 95% 区間 | 採択 draw |
|---|---:|---:|---:|---:|---|---:|
| ssl-ctc-other-domain | 5 | 0.699 | 0.719 | +0.020 | [+0.008, +0.032] | 200 |
| whisper | 7 | 0.676 | 0.721 | +0.045 | [+0.031, +0.060] | 200 |
| ssl-ctc-librispeech | 5 | 0.713 | 0.732 | +0.019 | [+0.008, +0.030] | 200 |

## 誤りの相関構造（探索）

family 内の平均相関 0.745、family 間 0.658、第 1 主成分の寄与 0.689。

## 時間的特徴（探索、二次チャネル設計のための観察）

| 評定 | r(−発話時間) | r(参照音素数) |
|---|---:|---:|
| accuracy | 0.578 | -0.176 |
| completeness | 0.014 | -0.019 |
| fluency | 0.705 | -0.211 |
| prosodic | 0.678 | -0.209 |
| total | 0.614 | -0.190 |

パネル平均と参照音素数の相関：0.033。

## 次の関門

読み出し仕様・パネル規則・統計手順をこの結果で変更しないと宣言し、`04_preregistration_confirmatory.md` を記入・コミットしてから SO762 test を 1 回だけ解析する。
