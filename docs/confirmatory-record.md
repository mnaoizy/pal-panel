# Confirmatory record

Each stage was run once in the planned order (`src/confirm.py`, seed 20260913, B = 2,000). During stage 1 the interval helper produced NaN for the completeness aspect (zero-variance resamples); it was changed to ignore undefined resamples (`nanpercentile`) and stage 1 was recomputed on identical inputs. Point estimates and all decision-relevant values were unchanged.

| Stage | Primary comparison | Result | Decision |
|---|---|---|---|
| 1 speechocean762 test | H2: PAL − `hubert-large` (accuracy) | +0.038 [+0.021, +0.056] (PAL 0.671, single 0.633) | supported |
| 2 ERJ | H4: segmental − rhythm | +0.440 [+0.366, +0.516] | supported |
| 3 EpaDB | H1: *r* with phrase score | 0.415 [0.301, 0.491] | supported |
| 4 ALLSSTAR | H5: *r* with human word recovery | 0.576 [0.404, 0.713] | supported |
| 5 OMPAL | H6: tone − consonant | +0.196 [+0.099, +0.293] | supported |

## Secondary results (exploratory)

- speechocean762 test: PAL *r* = 0.671 [0.602, 0.725] accuracy; 0.648 fluency; 0.663 prosodic; 0.690 total; 0.200 completeness.
- H7: weak third 0.649 [0.588, 0.700]; difference from `hubert-large` +0.016 [−0.001, +0.034] (a similar correlation; no equivalence margin was pre-specified).
- H3: Whisper-7 0.621; matched cross-family draws mean 0.649; difference +0.028 [+0.013, +0.042]; all 200 draws above Whisper-7.
- Aggregation rules (difference from the equal-weight mean): median −0.019 [−0.026, −0.012]; minimum error −0.089 [−0.154, −0.032]; inverse development-error weights −0.005 [−0.011, +0.001].
- Random subsets (accuracy, mean of 200 draws): k = 1: 0.542; 4: 0.637; 8: 0.656; 28: 0.671.
- ERJ: segmental 0.597 [0.558, 0.632]; rhythm 0.157 [0.079, 0.235]; intonation 0.073 [0.005, 0.139]; segmental − intonation +0.524 [+0.451, +0.597]; speaker-level segmental 0.778.
- EpaDB: difference from `hubert-large` +0.114 [+0.077, +0.152]; speaker level 0.695.
- ALLSSTAR: `hubert-large` 0.476, difference +0.100 [+0.001, +0.200]; Whisper-7 0.548, difference +0.028 [−0.001, +0.058].
- OMPAL: tone channel 0.389 [0.308, 0.459] with tone ratings, 0.192 with consonant ratings; syllable-base channel 0.257 / 0.270; character channel 0.370 / 0.245; base-matched tone errors 0.475 [0.402, 0.532] with tone, 0.120 with consonant, +0.086 [+0.028, +0.143] over the full tone channel.

## Post-plan analyses (not in the plan)

- Robustness (`src/robustness.py`): dropping the two phone recognizers changes the speechocean762 test and ALLSSTAR correlations by −0.001 [−0.003, +0.001] and −0.003 [−0.012, +0.006]; equal weight per family instead of per listener changes them by +0.000 [−0.005, +0.005] and −0.006 [−0.025, +0.014].
- Partial correlations (`src/partial.py`): controlling for accuracy, PAL's correlations with fluency, prosody, and total fall from 0.648, 0.663, 0.690 to 0.272 [0.195, 0.347], 0.312, and 0.233.
- Inter-rater agreement on the test split (`src/human_agreement.py`): mean pairwise 0.618; each rater vs. the mean of the other four 0.732 (accuracy).

## Deviations from the plan

- The NaN fix above (no effect on decisions).
- The corpora had been used by the authors in earlier work; "after protocol commitment" is a guarantee about this pipeline, not a first exposure.
