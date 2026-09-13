"""Descriptive reference: inter-rater agreement on the SO762 test split accuracy ratings (five raters)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GOP, corr
REDO = Path(__file__).resolve().parent.parent
det = json.loads((GOP / "data/speechocean762/resource/scores-detail.json").read_text())
man = pd.read_csv(GOP / "data/manifest.csv", dtype={"utt_id": str}); test = man[man.split == "test"]
out = {}
for aspect in ("accuracy", "fluency", "total"):
    R = np.array([det[u][aspect] for u in test.utt_id], float); assert R.shape == (2500, 5)
    pair = [corr(R[:, i], R[:, j]) for i in range(5) for j in range(i + 1, 5)]
    rest = [corr(R[:, i], np.delete(R, i, axis=1).mean(1)) for i in range(5)]
    out[aspect] = {"mean_pairwise_r": float(np.mean(pair)), "mean_rater_vs_rest_r": float(np.mean(rest))}
(REDO / "results/human_agreement_test.json").write_text(json.dumps(out, indent=2) + "\n"); print(out)
