# Design protocol

Translation of `ja/03_design_protocol.md` (the version committed in `0525275`; wording only).

## 1. Measurement model

- Object: an utterance *u* in which a learner reads a known prompt *t*.
- Instrument: *K* recognizers ("listeners"), each returning a hypothesis *h_k(u)*.
- Unitization: prompt and hypothesis are converted to phone sequences by the **same** normalization and grapheme-to-phoneme conversion; the phoneme error rate *e_k(u)* ∈ [0, 1] is the Levenshtein distance divided by the reference length, capped at 1. An empty hypothesis scores 1.
- Readout: *p(u) = −(1/K) Σ_k e_k(u)*. **No weights are learned.** *p* is a relative scale, evaluated by correlation.
- Interpretation: larger *p(u)* means the prompt is more recoverable by dissimilar listeners.

English phonemization: lowercase; ASCII punctuation other than apostrophes to spaces; digits to spoken names one by one; whitespace collapsed; g2p_en per word to ARPAbet with stress digits removed. Phone recognizers (espeak-phone, allosaurus-eng) are compared token by token with an eSpeak (en-us) IPA reference; no inventory mapping is applied, which is recorded as a limitation.

Mandarin (OMPAL): traditional-to-simplified normalization; character error rate on the Han string; pinyin (TONE3) split into syllable-base and tone-symbol sequences with separate error rates. Tones are canonical lexical tones with the neutral tone as a fifth category; sandhi and polyphonic characters are not modeled.

## 2. Panel admission rule (fixed before any result was seen)

1. Openly downloadable weights; support for the target language or a universal phone inventory.
2. **One configuration per acoustic checkpoint**; decoder variants (e.g., language-model weight sweeps) of an admitted checkpoint are not admitted.
3. Artificially degraded inputs are not admitted.
4. Configurations whose checkpoint identity cannot be established from the inventory are not admitted.
5. Every configuration satisfying 1–4 is admitted; none is selected by performance.

The candidate inventory is the set of configurations whose transcripts existed before this study (`src/inventory.py` → `results/data_inventory.json`, which lists exclusions with reasons). Applied to the 34 speechocean762 configurations this excludes `w2v2lm_a0.5/a1.0/a2.0` (decoder variants of wav2vec2-base), `base.en@snr10` and `parakeet@snr10` (degraded inputs), and `xlsr-cv-en` (checkpoint not established), leaving **28** English listeners in 10 families defined a priori by architecture and training data.

## 3. Data roles and unlock order (fixed)

| Stage | Data | Use |
|---|---|---|
| Development | speechocean762 **train** (2,500 utterances, 125 speakers) | all decisions about readout, panel rule, statistics; exploratory analyses |
| Confirmation 1 | speechocean762 **test** | H1, H2, H3, H7; run once |
| Confirmation 2 | ERJ | H4 |
| Confirmation 3 | EpaDB | H1 replication |
| Confirmation 4 | ALLSSTAR | H5 |
| Confirmation 5 | OMPAL | H6 |

Rule: after a confirmatory dataset is analysed, readout, panel, and statistics are not changed. The analysis plan (`analysis-plan.md`) is committed before the confirmatory stages.

## 4. Statistics

Pearson *r* (utterance level; talker level for ALLSSTAR); speaker-clustered (talker-clustered) percentile bootstrap, B = 2,000, seed = 20260913, 95% intervals; paired differences computed on identical resamples. One primary comparison per hypothesis; secondary comparisons are exploratory and uncorrected.

## 5. Decision rules

- H2's "best single listener" is chosen by development-split accuracy correlation and held fixed.
- H3 "matched": cross-family draws of size *k* (one listener per family) whose mean development error rate and mean single-listener correlation lie within ±0.03 / ±0.02 of the same-family panel; 200 draws.
- H7 "weak listeners": the third of the panel with the highest development mean error rate.

## 6. Threats and countermeasures

| Threat | Countermeasure |
|---|---|
| Development choices leaking into confirmation | fixed unlock order; panel by rule, not by performance |
| Transcripts are retained outputs that cannot be re-decoded identically | inventory records model identity, row counts, and empty-output rates; empties score 1 |
| Prompt length or recording conditions drive correlations | correlations are within-corpus; reference phone count is reported |
| Overlap between rating aspects (accuracy vs. fluency) | ERJ separates segmental from prosodic ratings (H4) |
| Single-corpus overfitting | four external corpora and one human-listening criterion |
