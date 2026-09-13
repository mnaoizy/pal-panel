"""Per-listener mean error vs accuracy correlation on the development split (stage1_dev.json)."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
dev = json.loads((ROOT / "results/stage1_dev.json").read_text())
fam_order = ["gmm-hmm", "kaldi-hybrid", "conv-ctc", "ssl-ctc-librispeech", "ssl-ctc-other-domain", "whisper", "other-enc-dec", "transducer", "speech-llm", "phone-recognizer"]
markers = ["s", "D", "^", "o", "o", "v", "P", "X", "*", "h"]
fills = ["black", "black", "black", "black", "none", "black", "black", "black", "black", "none"]
plt.rcParams.update({"font.size": 8.5, "font.family": "serif"})
fig, ax = plt.subplots(figsize=(3.4, 2.5))
for fam, mk, fc in zip(fam_order, markers, fills):
    pts = [(v["mean_error"], v["accuracy"]) for v in dev["per_listener"].values() if v["family"] == fam]
    if pts:
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], marker=mk, s=28, facecolors=fc if fc == "none" else "black", edgecolors="black", linewidths=0.7, label=fam)
ax.axhline(dev["panel_equal_mean"]["accuracy"]["r"], color="black", linewidth=0.8, linestyle="--")
ax.text(0.02, dev["panel_equal_mean"]["accuracy"]["r"] + 0.008, "full panel", fontsize=7.5, transform=ax.get_yaxis_transform())
ax.set_xlabel("Mean phoneme error rate (training split)"); ax.set_ylabel("$r$ with accuracy rating")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(fontsize=6, frameon=False, ncol=2, loc="lower left", handletextpad=0.2, columnspacing=0.6)
fig.tight_layout(); fig.savefig(ROOT / "paper/figures/listeners.pdf"); print("ok")
