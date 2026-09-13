"""Recompute the pre-specified primary comparisons from the released error-rate matrices.

Inputs: results/errors_*.csv (released) and the corpora's ratings, read from a local copy of
the corpora (set PAL_DATA to the directory holding the manifests; default: the gop workspace).
Prints each primary comparison and asserts equality with results/stage*.json.
"""
import json, os, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import corr, cluster_resamples, ci, paired
REDO = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("PAL_DATA", "/Volumes/Untitled/Prj/gop"))
dev = json.loads((REDO / "results/stage1_dev.json").read_text()); panel = dev["panel"]; best = dev["H2_dev"]["best_single_by_train_accuracy"]
def errors(name): return pd.read_csv(REDO / f"results/errors_{name}.csv", dtype={"utt_id": str}).set_index("utt_id")
def close(a, b, tol=1e-9): assert abs(a - b) < tol, (a, b)
# 1 SO762 test: PAL - best single (accuracy)
E = errors("so762_test"); man = pd.read_csv(DATA / "data/manifest.csv", dtype={"utt_id": str}).set_index("utt_id").loc[E.index]
S = cluster_resamples(man.wav.str.extract(r"(SPEAKER\d+)")[0].to_numpy()); y = man.accuracy.to_numpy(float)
r = paired(-E[panel].to_numpy().mean(1), -E[best].to_numpy(), y, S); s2 = json.loads((REDO / "results/stage2.json").read_text())
close(r["delta"], s2["primary_H2_panel_minus_hubert"]["delta"]); close(r["delta_ci95"][0], s2["primary_H2_panel_minus_hubert"]["delta_ci95"][0]); print("SO762 test  H2 delta", round(r["delta"], 3), [round(v, 3) for v in r["delta_ci95"]])
# 2 ERJ: segmental - rhythm
E = errors("erj"); man = pd.read_csv(DATA / "data/manifest_erj.csv", dtype={"utt_id": str}).set_index("utt_id").loc[E.index]
p = -E[panel].to_numpy().mean(1); S = cluster_resamples(man.spk.to_numpy()); T = {a: man[c].to_numpy(float) for a, c in (("seg", "seg_mean"), ("rhy", "rhy_mean"))}
def ron(a, i): sub = i[~np.isnan(T[a][i])]; return corr(p[sub], T[a][sub])
full = np.arange(len(man)); d = [ron("seg", i) - ron("rhy", i) for i in S]; s3 = json.loads((REDO / "results/stage3.json").read_text())
close(ron("seg", full) - ron("rhy", full), s3["primary_H4_seg_minus_rhythm"]["delta"]); print("ERJ         H4 delta", round(ron("seg", full) - ron("rhy", full), 3), [round(v, 3) for v in ci(d)])
# 3 EpaDB
E = errors("epadb"); man = pd.read_csv(DATA / "data/manifest_epadb.csv", dtype={"utt_id": str}).set_index("utt_id").loc[E.index]
sc = pd.read_csv(DATA / "results/epadb_scores.csv", dtype={"utt_id": str}).set_index("utt_id").loc[E.index]
p = -E[panel].to_numpy().mean(1); rr = corr(p, sc.score_a1.to_numpy(float)); s4 = json.loads((REDO / "results/stage4.json").read_text()); close(rr, s4["primary_H1_panel_r"]["r"]); print("EpaDB       H1 r    ", round(rr, 3))
# 4 ALLSSTAR
E = errors("allsstar"); man = pd.read_csv(DATA / "data/manifest_allsstar2.csv"); man["utt_id"] = man.utt_id.astype(str); man = man.set_index("utt_id").loc[E.index]
raw = pd.read_csv(DATA / "data/allsstar/L2_response_score.csv"); raw["speaker"] = raw.nativelanguage + "_" + raw.audio.str.extract(r"ALL_(\d+)_")[0].astype(int).astype(str)
human = raw.groupby("speaker").percorrect.mean(); tp = pd.Series(-E[panel].to_numpy().mean(1), index=man.speaker.to_numpy()).groupby(level=0).mean()
sp = sorted(set(tp.index) & set(human.index)); rr = corr(tp.loc[sp].to_numpy(), human.loc[sp].to_numpy()); s5 = json.loads((REDO / "results/stage5.json").read_text()); close(rr, s5["primary_H5_panel_r"]["r"]); print("ALLSSTAR    H5 r    ", round(rr, 3))
# 5 OMPAL
E = pd.read_csv(REDO / "results/errors_ompal.csv", dtype={"utt_id": str}); human = json.loads((DATA / "data/ompal/non-native_scores.json").read_text())
agg = E.groupby("utt_id").toneER.mean(); utts = list(agg.index)
def wmean(u, key): v = [w[key] for w in human[u].get("words", []) if key in w]; return float(np.mean(v)) if v else float("nan")
tone_t = np.array([wmean(u, "tone") for u in utts]); cons_t = np.array([wmean(u, "phoneme_consonant") for u in utts]); tone = -agg.to_numpy()
rr = corr(tone, tone_t) - corr(tone, cons_t); s6 = json.loads((REDO / "results/stage6.json").read_text()); close(rr, s6["primary_H6_tone_minus_consonant"]["delta"]); print("OMPAL       H6 delta", round(rr, 3))
print("all five primary comparisons reproduced from released error rates")
