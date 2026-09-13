"""Post-hoc: partial correlations of PAL with fluency/prosodic/total controlling accuracy (SO762 test), and the reverse."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GOP, corr, cluster_resamples, ci
from confirm import DEV
REDO = Path(__file__).resolve().parent.parent
E = pd.read_csv(REDO / "results/errors_so762_test.csv", dtype={"utt_id": str}).set_index("utt_id")
man = pd.read_csv(GOP / "data/manifest.csv", dtype={"utt_id": str}); test = man[man.split == "test"].set_index("utt_id").loc[E.index]
p = -E[DEV["panel"]].to_numpy().mean(1); S = cluster_resamples(test.wav.str.extract(r"(SPEAKER\d+)")[0].to_numpy())
Y = {a: test[a].to_numpy(float) for a in ("accuracy", "fluency", "prosodic", "total")}
def resid(a, z):
    A = np.column_stack([np.ones_like(z), z]); return a - A @ np.linalg.lstsq(A, a, rcond=None)[0]
def partial(x, y, z, idx): return corr(resid(x[idx], z[idx]), resid(y[idx], z[idx]))
full = np.arange(len(p)); out = {"status": "post-hoc, not pre-registered", "controlling_accuracy": {}, "accuracy_controlling": {}}
for a in ("fluency", "prosodic", "total"):
    out["controlling_accuracy"][a] = {"partial_r": partial(p, Y[a], Y["accuracy"], full), "ci95": ci([partial(p, Y[a], Y["accuracy"], i) for i in S]), "zero_order_r": corr(p, Y[a])}
    out["accuracy_controlling"][a] = {"partial_r": partial(p, Y["accuracy"], Y[a], full), "ci95": ci([partial(p, Y["accuracy"], Y[a], i) for i in S])}
(REDO / "results/partial_correlations.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=1))
