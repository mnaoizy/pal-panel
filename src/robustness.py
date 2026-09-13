"""Post-hoc robustness checks requested after review (not pre-registered): drop the two phone recognizers;
family-balanced mean (equal weight per family, then across families). SO762 test uses the saved error matrix;
ALLSSTAR is re-scored from the same transcripts."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GOP, corr, cluster_resamples, paired
from inventory import FAMILY
from confirm import score_corpus, DEV
REDO = Path(__file__).resolve().parent.parent
panel = DEV["panel"]; phones = ["espeak-phone", "allosaurus-eng"]; lex = [n for n in panel if n not in phones]
fams = sorted({FAMILY[n] for n in panel})
def balanced(E):
    return -np.mean([E[[n for n in panel if FAMILY[n] == f]].to_numpy().mean(1) for f in fams], axis=0)
out = {"status": "post-hoc robustness, computed after the pre-registered analyses at a reviewer's request"}
E = pd.read_csv(REDO / "results/errors_so762_test.csv", dtype={"utt_id": str}).set_index("utt_id")
man = pd.read_csv(GOP / "data/manifest.csv", dtype={"utt_id": str}); test = man[man.split == "test"].set_index("utt_id").loc[E.index]
y = test.accuracy.to_numpy(float); S = cluster_resamples(test.wav.str.extract(r"(SPEAKER\d+)")[0].to_numpy())
full = -E[panel].to_numpy().mean(1)
out["so762_test"] = {"no_phone_recognizers": paired(-E[lex].to_numpy().mean(1), full, y, S), "family_balanced": paired(balanced(E), full, y, S), "n_families": len(fams)}
aman = pd.read_csv(GOP / "data/manifest_allsstar2.csv"); aman["utt_id"] = aman.utt_id.astype(str)
EA, _ = score_corpus("allsstar", aman.utt_id.tolist(), aman.text.tolist())
raw = pd.read_csv(GOP / "data/allsstar/L2_response_score.csv")
raw["speaker"] = raw.nativelanguage + "_" + raw.audio.str.extract(r"ALL_(\d+)_")[0].astype(int).astype(str)
human = raw.groupby("speaker").percorrect.mean()
def talker(v): return pd.Series(v, index=aman.speaker.to_numpy()).groupby(level=0).mean()
sp = sorted(set(talker(-EA[panel].to_numpy().mean(1)).index) & set(human.index)); ya = human.loc[sp].to_numpy(float); SA = cluster_resamples(np.array(sp))
fa = talker(-EA[panel].to_numpy().mean(1)).loc[sp].to_numpy()
out["allsstar"] = {"no_phone_recognizers": paired(talker(-EA[lex].to_numpy().mean(1)).loc[sp].to_numpy(), fa, ya, SA),
                   "family_balanced": paired(talker(balanced(EA)).loc[sp].to_numpy(), fa, ya, SA)}
(REDO / "results/robustness.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: {kk: (round(vv["r_a"], 3), round(vv["delta"], 3), [round(x, 3) for x in vv["delta_ci95"]]) for kk, vv in v.items() if isinstance(vv, dict)} for k, v in out.items() if isinstance(v, dict)}, indent=1))
