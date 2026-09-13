"""Minimal, self-contained readout and statistics for the redo. No import from gop/src."""
from __future__ import annotations
import json, os, re, string
from functools import lru_cache
from pathlib import Path
import numpy as np

GOP = Path("/Volumes/Untitled/Prj/gop")
RESULTS = GOP / "results"
SEED, B = 20260913, 2000
os.environ.setdefault("PHONEMIZER_ESPEAK_LIBRARY", "/opt/homebrew/lib/libespeak-ng.dylib")
_PUNCT = {c: " " for c in string.punctuation if c != "'"}
_DIGITS = "zero one two three four five six seven eight nine".split()


def normalize(text: str) -> str:
    text = text.lower().strip().translate(str.maketrans(_PUNCT))
    text = re.sub(r"\d", lambda m: f" {_DIGITS[int(m.group())]} ", text)
    return re.sub(r"\s+", " ", text).strip()


_g2p = None


@lru_cache(maxsize=None)
def word_phones(word: str) -> tuple[str, ...]:
    global _g2p
    if _g2p is None:
        from g2p_en import G2p
        _g2p = G2p()
    return tuple(re.sub(r"\d", "", p) for p in _g2p(word) if p.strip() and p not in ("'", " "))


def arpabet(text: str) -> tuple[str, ...]:
    return tuple(p for w in normalize(text).split() for p in word_phones(w))


def espeak_ipa(texts: list[str]) -> dict[str, tuple[str, ...]]:
    from phonemizer.backend import EspeakBackend
    from phonemizer.separator import Separator
    uniq = sorted({normalize(t) for t in texts})
    out = EspeakBackend("en-us").phonemize(uniq, separator=Separator(phone=" ", word="| "), strip=True)
    return {t: tuple(x for x in (s.replace("|", "") for s in o.split()) if x) for t, o in zip(uniq, out)}


def error_rate(ref: tuple, hyp: tuple) -> float:
    """Levenshtein distance divided by reference length, capped at 1; empty hypothesis = 1."""
    if not ref:
        return 1.0
    if not hyp:
        return 1.0
    prev = list(range(len(hyp) + 1))
    for i, a in enumerate(ref, 1):
        cur = [i]
        for j, b in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (a != b)))
        prev = cur
    return min(prev[-1] / len(ref), 1.0)


def load_jsonl(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text().splitlines():
        r = json.loads(line)
        assert r["utt_id"] not in out, (path, r["utt_id"])
        out[r["utt_id"]] = r["hyp"]
    return out


def corr(x, y) -> float:
    x = np.asarray(x, float); y = np.asarray(y, float)
    x = x - x.mean(); y = y - y.mean()
    return float((x * y).sum() / np.sqrt((x * x).sum() * (y * y).sum()))


def cluster_resamples(groups, seed=SEED, reps=B) -> list[np.ndarray]:
    groups = np.asarray(groups, dtype=str)
    keys = np.unique(groups)
    blocks = {k: np.flatnonzero(groups == k) for k in keys}
    rng = np.random.default_rng(seed)
    return [np.concatenate([blocks[k] for k in rng.choice(keys, len(keys), replace=True)]) for _ in range(reps)]


def ci(values) -> list[float]:
    return [float(v) for v in np.nanpercentile(values, [2.5, 97.5])]


def corr_ci(score, target, samples) -> dict:
    return {"r": corr(score, target), "ci95": ci([corr(score[i], target[i]) for i in samples])}


def paired(score_a, score_b, target, samples) -> dict:
    d = np.array([corr(score_a[i], target[i]) - corr(score_b[i], target[i]) for i in samples])
    return {"r_a": corr(score_a, target), "r_b": corr(score_b, target), "delta": corr(score_a, target) - corr(score_b, target),
            "delta_ci95": ci(d), "p_delta_positive": float(np.mean(d > 0))}
