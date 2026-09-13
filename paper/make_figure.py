"""ALLSSTAR talker scatter from redo/results/stage5.json (panel talker scores) and the human criterion."""
import json, sys
from pathlib import Path
import csv, re
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
s5 = json.loads((ROOT / "results/stage5.json").read_text())
acc = {}
with open("/Volumes/Untitled/Prj/gop/data/allsstar/L2_response_score.csv") as f:
    for row in csv.DictReader(f):
        spk = row["nativelanguage"] + "_" + str(int(re.search(r"ALL_(\d+)_", row["audio"]).group(1)))
        acc.setdefault(spk, []).append(float(row["percorrect"]))
human = {k: float(np.mean(v)) for k, v in acc.items()}
x = np.array([v for v in s5["talker_scores"].values()]); y = np.array([human[s] for s in s5["talker_scores"]])
b, a = np.polyfit(x, y, 1)
plt.rcParams.update({"font.size": 9.2, "font.family": "serif"})
fig, ax = plt.subplots(figsize=(3.4, 2.3))
ax.scatter(x, y, s=14, facecolors="none", edgecolors="black", linewidths=0.7)
xs = np.linspace(x.min(), x.max(), 50); ax.plot(xs, a + b * xs, color="black", linewidth=1)
ax.set_xlabel("Panel score (mean $-$PER, 28 listeners)"); ax.set_ylabel("Human word recovery (%)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(ROOT / "paper/figures/allsstar.pdf")
print("r =", np.corrcoef(x, y)[0, 1], "n =", len(x))
