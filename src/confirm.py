"""Confirmatory stages 2-6, run once each in the pre-registered order (04_preregistration_confirmatory.md)."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GOP, RESULTS, SEED, B, normalize, arpabet, espeak_ipa, error_rate, load_jsonl, corr, cluster_resamples, corr_ci, paired, ci
from inventory import FAMILY, PHONE

REDO = Path(__file__).resolve().parent.parent
INV = json.loads((REDO / "results/data_inventory.json").read_text())
DEV = json.loads((REDO / "results/stage1_dev.json").read_text())
BEST = DEV["H2_dev"]["best_single_by_train_accuracy"]
WEAK = DEV["H7_dev"]["weakest_third"]
WHISPER = [n for n in DEV["panel"] if FAMILY[n] == "whisper"]
DRAWS = DEV["H3_matched_draws"]["whisper"]
ALIAS = {"parakeet": ["parakeet", "parakeet-tdt-0.6b"], "espeak-phone": ["espeak-phone"], "allosaurus-eng": ["allosaurus-eng"]}


def canon(name: str) -> str:
    return "parakeet" if name.startswith("parakeet") else name


def score_corpus(corpus: str, ids: list[str], texts: list[str]) -> tuple[pd.DataFrame, dict]:
    cfg = INV["corpora"][corpus]["configurations"]
    ipa = espeak_ipa(texts)
    refs_a = {u: arpabet(t) for u, t in zip(ids, texts)}
    refs_i = {u: ipa[normalize(t)] for u, t in zip(ids, texts)}
    cols, empties = {}, {}
    for name in INV["corpora"][corpus]["admitted"]:
        hyps = {}
        for f in cfg[name]["files"]:
            hyps.update(load_jsonl(GOP / f))
        assert set(ids) <= set(hyps), (corpus, name)
        c = canon(name); empties[c] = sum(1 for u in ids if not hyps[u].strip())
        cols[c] = [error_rate(refs_i[u], tuple(hyps[u].split())) if name in PHONE else error_rate(refs_a[u], arpabet(hyps[u])) for u in ids]
    E = pd.DataFrame(cols, index=ids)
    assert sorted(E.columns) == sorted(DEV["panel"]), (corpus, set(E.columns) ^ set(DEV["panel"]))
    return E, empties


def panel(E, members=None):
    return -E[members if members is not None else DEV["panel"]].to_numpy().mean(axis=1)


def stage2():
    man = pd.read_csv(GOP / "data/manifest.csv", dtype={"utt_id": str})
    test = man[man.split == "test"].reset_index(drop=True); assert len(test) == 2500
    test["spk"] = test.wav.str.extract(r"(SPEAKER\d+)")
    E, empties = score_corpus("so762", test.utt_id.tolist(), test.text.tolist())
    E.to_csv(REDO / "results/stage2_test_error_rates.csv", index_label="utt_id")
    Y = {a: test[a].to_numpy(float) for a in ["accuracy", "completeness", "fluency", "prosodic", "total"]}
    S = cluster_resamples(test.spk.to_numpy()); p = panel(E); y = Y["accuracy"]
    out = {"data": "SO762 test", "n": len(test), "speakers": int(test.spk.nunique()), "empty": empties,
           "primary_H2_panel_minus_hubert": paired(p, -E[BEST].to_numpy(), y, S),
           "H1_panel": {a: corr_ci(p, Y[a], S) for a in Y},
           "H7_weak_minus_hubert": paired(panel(E, WEAK), -E[BEST].to_numpy(), y, S),
           "H7_weak_panel": corr_ci(panel(E, WEAK), y, S)}
    X = np.column_stack([panel(E, d) for d in DRAWS]); same = panel(E, WHISPER)
    pts = np.array([corr(X[:, j], y) for j in range(X.shape[1])])
    d = np.array([np.mean([corr(X[i, j], y[i]) for j in range(X.shape[1])]) - corr(same[i], y[i]) for i in S])
    out["H3_whisper7_vs_matched_cross"] = {"same_family_r": corr(same, y), "cross_mean_r": float(pts.mean()), "fraction_draws_above": float(np.mean(pts > corr(same, y))),
                                          "delta_cross_minus_same": float(pts.mean() - corr(same, y)), "delta_ci95": ci(d)}
    tr_err = {n: DEV["per_listener"][n]["mean_error"] for n in DEV["panel"]}
    w = np.array([1 / tr_err[n] for n in DEV["panel"]]); w /= w.sum()
    M = E[DEV["panel"]].to_numpy()
    out["secondary_aggregation"] = {"median": paired(-np.median(M, 1), p, y, S), "min_error": paired(-M.min(1), p, y, S),
                                    "inverse_train_error_weights": paired(-(M * w).sum(1), p, y, S)}
    rng = np.random.default_rng(SEED)
    out["secondary_subset_curve"] = {k: float(np.mean([corr(panel(E, list(rng.choice(DEV["panel"], k, replace=False))), y) for _ in range(200)])) for k in (1, 2, 4, 8, 16, 28)}
    out["single_listeners"] = {n: corr(-E[n].to_numpy(), y) for n in DEV["panel"]}
    return out


def stage3():
    man = pd.read_csv(GOP / "data/manifest_erj.csv", dtype={"utt_id": str})
    E, empties = score_corpus("erj", man.utt_id.tolist(), man.text.tolist())
    p = panel(E); S = cluster_resamples(man.spk.to_numpy())
    T = {"segmental": man.seg_mean.to_numpy(float), "rhythm": man.rhy_mean.to_numpy(float), "intonation": man.int_mean.to_numpy(float)}
    masks = {a: ~np.isnan(v) for a, v in T.items()}

    def r_on(a, idx):
        sub = idx[masks[a][idx]]; return corr(p[sub], T[a][sub])
    full = np.arange(len(man)); dr = pd.DataFrame([{a: r_on(a, i) for a in T} for i in S])
    out = {"data": "ERJ", "n": {a: int(m.sum()) for a, m in masks.items()}, "speakers": int(man.spk.nunique()), "empty": empties,
           "r": {a: {"r": r_on(a, full), "ci95": ci(dr[a])} for a in T},
           "primary_H4_seg_minus_rhythm": {"delta": r_on("segmental", full) - r_on("rhythm", full), "ci95": ci(dr.segmental - dr.rhythm)},
           "seg_minus_intonation": {"delta": r_on("segmental", full) - r_on("intonation", full), "ci95": ci(dr.segmental - dr.intonation)}}
    seg = man[masks["segmental"]].assign(p=p[masks["segmental"]]).groupby("spk").agg(p=("p", "mean"), s=("seg_mean", "mean"))
    out["speaker_level_segmental_r"] = corr(seg.p, seg.s)
    return out


def stage4():
    man = pd.read_csv(GOP / "data/manifest_epadb.csv", dtype={"utt_id": str})
    sc = pd.read_csv(GOP / "results/epadb_scores.csv", dtype={"utt_id": str}).set_index("utt_id").loc[man.utt_id]
    E, empties = score_corpus("epadb", man.utt_id.tolist(), man.text.tolist())
    p = panel(E); y = sc.score_a1.to_numpy(float); S = cluster_resamples(man.spk.to_numpy())
    spk = pd.DataFrame({"spk": man.spk, "p": p, "y": y}).groupby("spk").mean()
    return {"data": "EpaDB", "n": len(man), "speakers": int(man.spk.nunique()), "empty": empties, "criterion": "annotator-1 phrase score",
            "primary_H1_panel_r": corr_ci(p, y, S), "panel_minus_hubert": paired(p, -E[BEST].to_numpy(), y, S), "speaker_level_r": corr(spk.p, spk.y)}


def stage5():
    man = pd.read_csv(GOP / "data/manifest_allsstar2.csv"); man["utt_id"] = man.utt_id.astype(str)
    E, empties = score_corpus("allsstar", man.utt_id.tolist(), man.text.tolist())
    raw = pd.read_csv(GOP / "data/allsstar/L2_response_score.csv")
    raw["speaker"] = raw.nativelanguage + "_" + raw.audio.str.extract(r"ALL_(\d+)_")[0].astype(int).astype(str)
    human = raw.groupby("speaker").percorrect.mean()

    def talker(score):
        return pd.Series(score, index=man.speaker.to_numpy()).groupby(level=0).mean()
    tp = talker(panel(E)); th = talker(-E[BEST].to_numpy()); tw = talker(panel(E, WHISPER))
    speakers = sorted(set(tp.index) & set(human.index)); assert len(speakers) == 100
    y = human.loc[speakers].to_numpy(float); a = tp.loc[speakers].to_numpy(); h = th.loc[speakers].to_numpy(); w = tw.loc[speakers].to_numpy()
    S = cluster_resamples(np.array(speakers))
    return {"data": "ALLSSTAR", "talkers": len(speakers), "utterances": len(man), "empty": empties, "criterion": "talker mean word-recognition accuracy over all listening conditions",
            "primary_H5_panel_r": corr_ci(a, y, S), "panel_minus_hubert": paired(a, h, y, S), "panel_minus_whisper7": paired(a, w, y, S),
            "talker_scores": {s: float(v) for s, v in zip(speakers, a)}}


def stage6():
    from opencc import OpenCC
    from pypinyin import Style, lazy_pinyin
    t2s = OpenCC("t2s")

    def syls(text):
        out = []
        for x in lazy_pinyin(re.sub(r"[^一-鿿]", "", t2s.convert(text)), style=Style.TONE3, errors="ignore"):
            m = re.match(r"([a-zü]+)([1-5]?)$", x)
            if m:
                out.append((m.group(1), m.group(2) or "5"))
        return out

    def matched_tone(ref, hyp):
        if not ref or not hyp:
            return float("nan")
        rb, hb = [b for b, _ in ref], [b for b, _ in hyp]
        D = [[0] * (len(hb) + 1) for _ in range(len(rb) + 1)]
        for i in range(len(rb) + 1): D[i][0] = i
        for j in range(len(hb) + 1): D[0][j] = j
        for i in range(1, len(rb) + 1):
            for j in range(1, len(hb) + 1):
                D[i][j] = min(D[i - 1][j - 1] + (rb[i - 1] != hb[j - 1]), D[i - 1][j] + 1, D[i][j - 1] + 1)
        i, j, m, wr = len(rb), len(hb), 0, 0
        while i and j:
            if D[i][j] == D[i - 1][j - 1] + (rb[i - 1] != hb[j - 1]):
                if rb[i - 1] == hb[j - 1]:
                    m += 1; wr += ref[i - 1][1] != hyp[j - 1][1]
                i, j = i - 1, j - 1
            elif D[i][j] == D[i - 1][j] + 1: i -= 1
            else: j -= 1
        return wr / m if m else float("nan")
    re_ = pd.read_csv(RESULTS / "icassp2027/ompal_rehyp.csv", dtype={"utt_id": str}, keep_default_na=False)
    human = json.loads((GOP / "data/ompal/non-native_scores.json").read_text())
    speaker_of = {p.stem: p.parent.name for p in (GOP / "data/ompal/wav").glob("*/*.wav")}
    tiers = sorted(re_.tier.unique()); assert len(tiers) == 8
    cov = re_.groupby("utt_id").tier.nunique(); utts = sorted(u for u in cov[cov == 8].index if u in human and u in speaker_of)

    def wmean(u, key):
        v = [w[key] for w in human[u].get("words", []) if key in w]; return float(np.mean(v)) if v else float("nan")
    tone_t = np.array([wmean(u, "tone") for u in utts]); cons_t = np.array([wmean(u, "phoneme_consonant") for u in utts])
    keep = ~np.isnan(tone_t) & ~np.isnan(cons_t); utts = [u for u, k in zip(utts, keep) if k]; tone_t, cons_t = tone_t[keep], cons_t[keep]
    refs = {u: syls(human[u]["text"]) for u in utts}
    re_ = re_[re_.utt_id.isin(utts)].copy(); re_["mt"] = [matched_tone(refs[u], syls(h)) for u, h in zip(re_.utt_id, re_.hyp)]
    agg = re_.groupby("utt_id").agg(cer=("cer", "mean"), segER=("segER", "mean"), toneER=("toneER", "mean"), mt=("mt", "mean")).loc[utts]
    spk = np.array([speaker_of[u] for u in utts]); S = cluster_resamples(spk)
    tone = -agg.toneER.to_numpy(); base = -agg.segER.to_numpy(); char = -agg.cer.to_numpy(); mt = -agg.mt.to_numpy(); ok = np.isfinite(mt)
    d = np.array([corr(tone[i], tone_t[i]) - corr(tone[i], cons_t[i]) for i in S])
    Sm = cluster_resamples(spk[ok])
    return {"data": "OMPAL (re-decoded transcripts of all 8 Mandarin listeners)", "n": len(utts), "speakers": int(len(np.unique(spk))), "listeners": tiers,
            "tone_channel": {"tone_r": corr_ci(tone, tone_t, S), "consonant_r": corr(tone, cons_t)},
            "primary_H6_tone_minus_consonant": {"delta": corr(tone, tone_t) - corr(tone, cons_t), "ci95": ci(d)},
            "base_channel": {"tone_r": corr(base, tone_t), "consonant_r": corr(base, cons_t)}, "char_channel": {"tone_r": corr(char, tone_t), "consonant_r": corr(char, cons_t)},
            "tone_minus_base_on_tone": paired(tone, base, tone_t, S),
            "base_matched_tone": {"n": int(ok.sum()), "tone_r": corr_ci(mt[ok], tone_t[ok], Sm), "consonant_r": corr(mt[ok], cons_t[ok]),
                                  "minus_full_tone_channel": paired(mt[ok], tone[ok], tone_t[ok], Sm)}}


if __name__ == "__main__":
    stages = {"2": stage2, "3": stage3, "4": stage4, "5": stage5, "6": stage6}
    for k in (sys.argv[1:] or list(stages)):
        res = stages[k](); res["stage"] = int(k); res["seed"] = SEED; res["bootstraps"] = B
        (REDO / f"results/stage{k}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
        print(f"stage {k} done", flush=True)
