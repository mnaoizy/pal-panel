"""Generate numbers.tex / numbers.json for the paper from results/ only."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
R = {k: json.loads((ROOT / f"results/{n}.json").read_text()) for k, n in
     {"inv": "data_inventory", "dev": "stage1_dev", "s2": "stage2", "s3": "stage3", "s4": "stage4", "s5": "stage5", "s6": "stage6"}.items()}
M = {}
def put(name, value, fmt): M[name] = format(value, fmt)
def trio(prefix, point, interval, fmt): put(prefix, point, fmt); put(prefix + "Lo", interval[0], fmt); put(prefix + "Hi", interval[1], fmt)
dev, s2, s3, s4, s5, s6 = R["dev"], R["s2"], R["s3"], R["s4"], R["s5"], R["s6"]
put("Panel", len(dev["panel"]), "d"); put("Seed", dev["seed"], "d"); put("Boot", dev["bootstraps"], ",d")
put("SoTrain", dev["n_utterances"], ",d"); put("SoTrainSpk", dev["n_speakers"], "d"); put("SoTest", s2["n"], ",d"); put("SoTestSpk", s2["speakers"], "d")
put("Families", len({v["family"] for v in dev["per_listener"].values()}), "d")
trio("DevAcc", dev["panel_equal_mean"]["accuracy"]["r"], dev["panel_equal_mean"]["accuracy"]["ci95"], ".3f")
put("DevTotal", dev["panel_equal_mean"]["total"]["r"], ".3f"); put("DevFlu", dev["panel_equal_mean"]["fluency"]["r"], ".3f"); put("DevComp", dev["panel_equal_mean"]["completeness"]["r"], ".3f")
put("DevBestR", dev["H2_dev"]["accuracy"]["r_b"], ".3f"); put("DevWeakR", dev["H7_dev"]["weak_panel"]["r"], ".3f"); put("DevStrongR", dev["H7_dev"]["strong_panel"]["r"], ".3f")
put("WeakN", len(dev["H7_dev"]["weakest_third"]), "d")
put("DevWithin", dev["error_correlation"]["mean_within_family"], ".2f"); put("DevAcross", dev["error_correlation"]["mean_across_family"], ".2f"); put("DevPc", 100 * dev["error_correlation"]["pc1_share"], ".0f")
for k in ("1", "4", "8", "28"): put(f"Curve{k}", dev["aggregation_curve_accuracy"][k]["mean_r"], ".3f")
put("DevWhisSame", dev["H3_dev"]["whisper"]["same_family_r"], ".3f"); put("DevWhisCross", dev["H3_dev"]["whisper"]["cross_family_mean_r"], ".3f")
trio("DevWhisDelta", dev["H3_dev"]["whisper"]["delta_cross_minus_same"], dev["H3_dev"]["whisper"]["delta_ci95"], "+.3f")
h2 = s2["primary_H2_panel_minus_hubert"]; trio("TestDelta", h2["delta"], h2["delta_ci95"], "+.3f"); put("TestPanelAcc", h2["r_a"], ".3f"); put("TestHubert", h2["r_b"], ".3f")
trio("TestAcc", s2["H1_panel"]["accuracy"]["r"], s2["H1_panel"]["accuracy"]["ci95"], ".3f")
for a, n in (("fluency", "TestFlu"), ("prosodic", "TestPros"), ("total", "TestTotal"), ("completeness", "TestComp")): put(n, s2["H1_panel"][a]["r"], ".3f")
trio("TestWeak", s2["H7_weak_panel"]["r"], s2["H7_weak_panel"]["ci95"], ".3f"); trio("TestWeakDelta", s2["H7_weak_minus_hubert"]["delta"], s2["H7_weak_minus_hubert"]["delta_ci95"], "+.3f")
h3 = s2["H3_whisper7_vs_matched_cross"]; put("TestWhisSame", h3["same_family_r"], ".3f"); put("TestWhisCross", h3["cross_mean_r"], ".3f"); trio("TestWhisDelta", h3["delta_cross_minus_same"], h3["delta_ci95"], "+.3f"); put("TestWhisFrac", 100 * h3["fraction_draws_above"], ".0f")
for key, n in (("median", "AggMedian"), ("min_error", "AggMin"), ("inverse_train_error_weights", "AggInv")):
    trio(n + "Delta", s2["secondary_aggregation"][key]["delta"], s2["secondary_aggregation"][key]["delta_ci95"], "+.3f"); put(n + "R", s2["secondary_aggregation"][key]["r_a"], ".3f")
for k in ("1", "4", "8", "28"): put(f"TestCurve{k}", s2["secondary_subset_curve"][k], ".3f")
put("Draws", len(dev["H3_matched_draws"]["whisper"]), "d"); put("WhisK", len([n for n in dev["panel"] if dev["per_listener"][n]["family"] == "whisper"]), "d")
put("ErjN", sum(s3["n"].values()), ",d"); put("ErjSpk", s3["speakers"], "d")
trio("ErjSeg", s3["r"]["segmental"]["r"], s3["r"]["segmental"]["ci95"], ".3f"); trio("ErjRhy", s3["r"]["rhythm"]["r"], s3["r"]["rhythm"]["ci95"], ".3f"); trio("ErjInt", s3["r"]["intonation"]["r"], s3["r"]["intonation"]["ci95"], ".3f")
trio("ErjSegRhy", s3["primary_H4_seg_minus_rhythm"]["delta"], s3["primary_H4_seg_minus_rhythm"]["ci95"], "+.3f"); trio("ErjSegInt", s3["seg_minus_intonation"]["delta"], s3["seg_minus_intonation"]["ci95"], "+.3f")
put("ErjSpkR", s3["speaker_level_segmental_r"], ".3f")
put("EpaN", s4["n"], ",d"); put("EpaSpk", s4["speakers"], "d"); trio("Epa", s4["primary_H1_panel_r"]["r"], s4["primary_H1_panel_r"]["ci95"], ".3f")
trio("EpaDelta", s4["panel_minus_hubert"]["delta"], s4["panel_minus_hubert"]["delta_ci95"], "+.3f"); put("EpaHubert", s4["panel_minus_hubert"]["r_b"], ".3f"); put("EpaSpkR", s4["speaker_level_r"], ".3f")
put("AllTalkers", s5["talkers"], "d"); put("AllUttPer", s5["utterances"] // s5["talkers"], "d"); put("AllUtt", s5["utterances"], ",d"); trio("All", s5["primary_H5_panel_r"]["r"], s5["primary_H5_panel_r"]["ci95"], ".3f")
trio("AllDelta", s5["panel_minus_hubert"]["delta"], s5["panel_minus_hubert"]["delta_ci95"], "+.3f"); put("AllHubert", s5["panel_minus_hubert"]["r_b"], ".3f")
trio("AllWhisDelta", s5["panel_minus_whisper7"]["delta"], s5["panel_minus_whisper7"]["delta_ci95"], "+.3f"); put("AllWhis", s5["panel_minus_whisper7"]["r_b"], ".3f")
put("OmN", s6["n"], ",d"); put("OmSpk", s6["speakers"], "d"); put("OmListeners", len(s6["listeners"]), "d")
trio("OmTone", s6["tone_channel"]["tone_r"]["r"], s6["tone_channel"]["tone_r"]["ci95"], ".3f"); put("OmToneCons", s6["tone_channel"]["consonant_r"], ".3f")
trio("OmDelta", s6["primary_H6_tone_minus_consonant"]["delta"], s6["primary_H6_tone_minus_consonant"]["ci95"], "+.3f")
put("OmBaseTone", s6["base_channel"]["tone_r"], ".3f"); put("OmBaseCons", s6["base_channel"]["consonant_r"], ".3f"); put("OmCharTone", s6["char_channel"]["tone_r"], ".3f"); put("OmCharCons", s6["char_channel"]["consonant_r"], ".3f")
trio("OmMatched", s6["base_matched_tone"]["tone_r"]["r"], s6["base_matched_tone"]["tone_r"]["ci95"], ".3f"); put("OmMatchedCons", s6["base_matched_tone"]["consonant_r"], ".3f")
trio("OmMatchedDelta", s6["base_matched_tone"]["minus_full_tone_channel"]["delta"], s6["base_matched_tone"]["minus_full_tone_channel"]["delta_ci95"], "+.3f")
for n, v in dev["per_listener"].items():
    slug = "".join(part.capitalize() for part in "".join(c if c.isalnum() else " " for c in n).split())
    put("Err" + slug, v["mean_error"], ".2f")
emp = dev["per_listener"]; put("MoonEmpty", 100 * emp["moonshine-base"]["empty"] / dev["n_utterances"], ".1f")
hum = json.loads((ROOT / "results/human_agreement_test.json").read_text())
put("HumPair", hum["accuracy"]["mean_pairwise_r"], ".3f"); put("HumRest", hum["accuracy"]["mean_rater_vs_rest_r"], ".3f")
# Published comparison values (documentary, not reproduced here): GOPT accuracy PCC as reported in the
# HMamba paper's Table 1 (0.714); HMamba Table 1 (0.807); transcript-guided DTW distance, sign-reversed
# (0.633, arXiv:2606.19910 Table 2); TextPA Gemini-2.0-flash (0.532).
put("PubGopt", 0.714, ".3f"); put("PubHmamba", 0.807, ".3f"); put("PubDtw", 0.633, ".3f"); put("PubTextpa", 0.532, ".3f")
rob = json.loads((ROOT / "results/robustness.json").read_text())
for corpus, pre in (("so762_test", "RobSo"), ("allsstar", "RobAll")):
    for key, suf in (("no_phone_recognizers", "NoPhone"), ("family_balanced", "FamBal")):
        v = rob[corpus][key]; put(pre + suf, v["r_a"], ".3f"); trio(pre + suf + "Delta", v["delta"], v["delta_ci95"], "+.3f")
put("RobFamilies", rob["so762_test"]["n_families"], "d")
pc = json.loads((ROOT / "results/partial_correlations.json").read_text())
for a, n in (("fluency", "PartFlu"), ("prosodic", "PartPros"), ("total", "PartTotal")):
    v = pc["controlling_accuracy"][a]; trio(n, v["partial_r"], v["ci95"], ".3f")
tex = "\\newcommand{\\N}[1]{\\csname N#1\\endcsname}\n" + "".join(f"\\expandafter\\def\\csname N{k}\\endcsname{{{v.replace(',', '{,}')}}}\n" for k, v in M.items())
(ROOT / "paper/numbers.tex").write_text(tex); (ROOT / "paper/numbers.json").write_text(json.dumps(M, indent=2) + "\n")
print(len(M), "macros")
