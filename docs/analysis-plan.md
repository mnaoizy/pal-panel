# Confirmatory analysis plan

Translation of `ja/04_preregistration_confirmatory.md` as committed in `0525275` (2026-09-13 20:44 JST), after the development stage and before the confirmatory stages were run. Later changes are recorded in `confirmatory-record.md` as additions, not edits.

## Frozen for all stages

- Readout: `src/common.py` (`normalize`, `arpabet`, `espeak_ipa`, `error_rate`), equal-weight mean, empty hypothesis = 1, cap 1.
- Panel: configurations admitted by the rule in `design-protocol.md` §2; 28 English listeners (per-corpus `admitted` lists in `results/data_inventory.json`); 8 Mandarin listeners with re-decoded transcripts. No performance-based selection.
- Statistics: Pearson *r*; speaker- (or talker-) clustered percentile bootstrap, B = 2,000, seed 20260913; paired comparisons on shared resamples.
- Fixed comparators: best single listener = `hubert-large` (development accuracy correlation); weak third = the nine highest-error listeners on the development split (`results/stage1_dev.json`, `H7_dev.weakest_third`); H3 matched cross-family draws = the 200 draws accepted on the development split (`H3_matched_draws`).
- Exclusions: utterances without transcripts are dropped and counted (none); utterances without a rating are excluded only from that rating's analysis.

## Primary comparison and decision rule per stage

| Stage | Data | Primary comparison | Decision | Secondary (exploratory, uncorrected) |
|---|---|---|---|---|
| 1 | speechocean762 test (2,500 utt., 125 speakers) | H2: PAL − `hubert-large`, paired difference on accuracy | lower CI bound > 0 | H1 (interval of PAL's *r*), H7 (weak third − `hubert-large`), H3 (Whisper-7 vs. matched cross-family draws), other aspects, aggregation rules (median, minimum, inverse development-error weights), subset curve |
| 2 | ERJ (3,800 utt., 190 speakers) | H4: segmental *r* − rhythm *r* (same speaker resamples; each aspect on its own rated utterances) | lower bound > 0 | segmental − intonation, per-aspect intervals, speaker level |
| 3 | EpaDB (3,160 utt., 50 speakers) | H1 replication: *r* with the phrase score | lower bound > 0 | speaker level; paired difference vs. `hubert-large` |
| 4 | ALLSSTAR (100 talkers, 15 sentences each) | H5: talker-mean PAL vs. all-condition word-recognition accuracy | lower bound > 0 | paired differences vs. `hubert-large` and vs. Whisper-7 |
| 5 | OMPAL (1,768 utt., 46 speakers, 8 re-decoded listeners) | H6: tone-channel *r* with tone ratings − *r* with consonant ratings (paired) | lower bound > 0 | syllable-base channel, base-matched tone errors, character channel |

Executed by the authors' assistant on 2026-09-13; results in `confirmatory-record.md`.
