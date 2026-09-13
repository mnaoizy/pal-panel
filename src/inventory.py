"""Catalogue every available transcript file per corpus and apply the a-priori panel rule (03 §2)."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from common import RESULTS, GOP

# Family labels assigned a priori from architecture x training data (03_design_protocol.md §2).
FAMILY = {
    "sphinx-enus": "gmm-hmm", "vosk-small": "kaldi-hybrid",
    "jasper": "conv-ctc", "quartznet": "conv-ctc",
    "wav2vec2-base": "ssl-ctc-librispeech", "w2v2-large-lv60": "ssl-ctc-librispeech", "wav2vec2-robust": "ssl-ctc-librispeech",
    "hubert-large": "ssl-ctc-librispeech", "wavlm-large": "ssl-ctc-librispeech",
    "w2v2-xlsr-cv": "ssl-ctc-other-domain", "xlsr-1b-cv": "ssl-ctc-other-domain", "w2v2-swbd": "ssl-ctc-other-domain",
    "atc-w2v2": "ssl-ctc-other-domain", "atc-xlsr": "ssl-ctc-other-domain",
    "tiny": "whisper", "tiny.en": "whisper", "base.en": "whisper", "small.en": "whisper",
    "distil-small.en": "whisper", "distil-large-v3": "whisper", "crisperwhisper": "whisper",
    "canary-1b": "other-enc-dec", "seamless-m4t-v2": "other-enc-dec", "moonshine-base": "other-enc-dec",
    "parakeet": "transducer", "parakeet-tdt-0.6b": "transducer", "qwen2audio": "speech-llm",
    "espeak-phone": "phone-recognizer", "allosaurus-eng": "phone-recognizer",
}
EXCLUDE = {  # configuration -> rule that excludes it
    "w2v2lm_a0.5": "decoder variant of wav2vec2-base (rule 2)", "w2v2lm_a1.0": "decoder variant of wav2vec2-base (rule 2)",
    "w2v2lm_a2.0": "decoder variant of wav2vec2-base (rule 2)", "w2v2lm@a2.0": "decoder variant of wav2vec2-base (rule 2)",
    "base.en@snr10": "artificially degraded input (rule 3)", "parakeet@snr10": "artificially degraded input (rule 3)",
    "xlsr-cv-en": "checkpoint identity not established in the inventory (rule 4)",
}
PHONE = {"espeak-phone", "allosaurus-eng"}
CORPORA = {"so762": ("hyp_", "train_hyp_"), "allsstar": ("allsstar2_hyp_",), "epadb": ("epadb_hyp_",), "erj": ("erj_hyp_",)}


def main():
    out = {"rule": "03_design_protocol.md section 2", "corpora": {}}
    for corpus, prefixes in CORPORA.items():
        configs = {}
        paths = sorted(RESULTS.glob("*.jsonl")) + (sorted((RESULTS / "icassp2027/external29").glob("*.jsonl")) if corpus in ("epadb", "erj") else [])
        for path in paths:
            for prefix in prefixes:
                m = re.fullmatch(re.escape(prefix) + r"(.+)\.jsonl", path.name)
                if m and (corpus != "so762" or not path.name.startswith(("allsstar", "epadb", "erj", "accent", "train_") if prefix == "hyp_" else ("x",))):
                    name = m.group(1)
                    lines = path.read_text().splitlines()
                    empty = sum(1 for l in lines if not json.loads(l)["hyp"].strip())
                    entry = configs.setdefault(name, {"files": [], "rows": 0, "empty": 0})
                    entry["files"].append(str(path.relative_to(GOP))); entry["rows"] += len(lines); entry["empty"] += empty
                    entry["sha256"] = entry.get("sha256", []) + [hashlib.sha256(path.read_bytes()).hexdigest()]
        for name, entry in configs.items():
            entry["family"] = FAMILY.get(name, "unassigned")
            entry["output_unit"] = "phones" if name in PHONE else "words"
            entry["admitted"] = name not in EXCLUDE and name in FAMILY
            entry["exclusion_reason"] = EXCLUDE.get(name) if name in EXCLUDE else (None if name in FAMILY else "no family assigned")
        out["corpora"][corpus] = {"configurations": configs, "admitted": sorted(n for n, e in configs.items() if e["admitted"]),
                                  "n_admitted": sum(e["admitted"] for e in configs.values())}
    Path(__file__).resolve().parent.parent.joinpath("results/data_inventory.json").write_text(json.dumps(out, indent=2) + "\n")
    for corpus, c in out["corpora"].items():
        print(corpus, "admitted", c["n_admitted"], "of", len(c["configurations"]))


if __name__ == "__main__":
    main()
