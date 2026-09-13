"""Stage 1 (development): SO762 train split only. The test split is not read."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import GOP, RESULTS, SEED, B, arpabet, espeak_ipa, error_rate, load_jsonl, corr, cluster_resamples, corr_ci, paired, ci
from inventory import FAMILY, PHONE

REDO = Path(__file__).resolve().parent.parent
ASPECTS = ["accuracy", "completeness", "fluency", "prosodic", "total"]


def main():
    inv = json.loads((REDO / "results/data_inventory.json").read_text())
    admitted = inv["corpora"]["so762"]["admitted"]
    man = pd.read_csv(GOP / "data/manifest.csv", dtype={"utt_id": str})
    train = man[man.split == "train"].reset_index(drop=True)
    assert len(train) == 2500
    train["spk"] = train.wav.str.extract(r"(SPEAKER\d+)")
    ids = train.utt_id.tolist()
    ipa = espeak_ipa(train.text.tolist())
    refs_arpa = {u: arpabet(t) for u, t in zip(ids, train.text)}
    refs_ipa = {u: ipa[__import__("common").normalize(t)] for u, t in zip(ids, train.text)}
    matrix, empties = {}, {}
    for name in admitted:
        hyps = {}
        for f in inv["corpora"]["so762"]["configurations"][name]["files"]:
            hyps.update(load_jsonl(GOP / f))
        assert set(ids) <= set(hyps), name
        empties[name] = sum(1 for u in ids if not hyps[u].strip())
        if name in PHONE:
            matrix[name] = [error_rate(refs_ipa[u], tuple(hyps[u].split())) for u in ids]
        else:
            matrix[name] = [error_rate(refs_arpa[u], arpabet(hyps[u])) for u in ids]
        print("scored", name, flush=True)
    E = pd.DataFrame(matrix, index=ids)
    E.to_csv(REDO / "results/errors_so762_train.csv", index_label="utt_id")
    Y = {a: train[a].to_numpy(float) for a in ASPECTS}
    samples = cluster_resamples(train.spk.to_numpy())
    listeners = sorted(E.columns)
    panel = -E[listeners].to_numpy().mean(axis=1)
    per_listener = {n: {"mean_error": float(E[n].mean()), "empty": empties[n], "family": FAMILY[n],
                        **{a: corr(-E[n].to_numpy(), Y[a]) for a in ASPECTS}} for n in listeners}
    result = {"stage": "1 development (SO762 train split only; test split unread)", "seed": SEED, "bootstraps": B,
              "n_utterances": len(train), "n_speakers": int(train.spk.nunique()), "panel": listeners, "per_listener": per_listener,
              "panel_equal_mean": {a: corr_ci(panel, Y[a], samples) for a in ASPECTS}}
    # H2 (development version): panel vs best single listener chosen on this same split (in-sample choice)
    best = max(listeners, key=lambda n: per_listener[n]["accuracy"])
    result["H2_dev"] = {"best_single_by_train_accuracy": best, "accuracy": paired(panel, -E[best].to_numpy(), Y["accuracy"], samples)}
    # H7 (development version): weakest third vs strongest third by mean error
    order = sorted(listeners, key=lambda n: per_listener[n]["mean_error"])
    third = len(order) // 3
    strong, weak = order[:third], order[-third:]
    result["H7_dev"] = {"weakest_third": weak, "strongest_third": strong,
                        "weak_panel": corr_ci(-E[weak].to_numpy().mean(1), Y["accuracy"], samples),
                        "strong_panel": corr_ci(-E[strong].to_numpy().mean(1), Y["accuracy"], samples),
                        "weak_minus_best_single": paired(-E[weak].to_numpy().mean(1), -E[best].to_numpy(), Y["accuracy"], samples)}
    # Aggregation curve: random subsets of size k (accuracy), 200 draws each
    rng = np.random.default_rng(SEED)
    curve = {}
    for k in (1, 2, 4, 8, 16, len(listeners)):
        rs = [corr(-E[list(rng.choice(listeners, k, replace=False))].to_numpy().mean(1), Y["accuracy"]) for _ in range(200)]
        curve[k] = {"mean_r": float(np.mean(rs)), "p5_p95": [float(v) for v in np.percentile(rs, [5, 95])]}
    result["aggregation_curve_accuracy"] = curve
    # H3 (development version): same-family panels vs cross-family panels of equal size, matched on mean error and mean single r
    fam_members = {}
    for n in listeners:
        fam_members.setdefault(FAMILY[n], []).append(n)
    families = sorted(fam_members)
    h3 = {}
    for fam, members in fam_members.items():
        if len(members) < 4:
            continue
        k = len(members)
        same = -E[members].to_numpy().mean(1)
        pi_star = float(np.mean([per_listener[n]["mean_error"] for n in members]))
        rho_star = float(np.mean([per_listener[n]["accuracy"] for n in members]))
        accepted, attempts = [], 0
        while len(accepted) < 200 and attempts < 200000:
            attempts += 1
            fs = rng.choice(families, k, replace=False)
            draw = [str(rng.choice(fam_members[f])) for f in fs]
            if abs(np.mean([per_listener[n]["mean_error"] for n in draw]) - pi_star) <= 0.03 and \
               abs(np.mean([per_listener[n]["accuracy"] for n in draw]) - rho_star) <= 0.02:
                accepted.append(draw)
        if len(accepted) < 20:
            h3[fam] = {"k": k, "accepted": len(accepted), "attempts": attempts, "note": "insufficient matched draws"}
            continue
        result.setdefault("H3_matched_draws", {})[fam] = accepted
        X = np.column_stack([-E[d].to_numpy().mean(1) for d in accepted])
        pts = np.array([corr(X[:, j], Y["accuracy"]) for j in range(X.shape[1])])
        d = np.array([np.mean([corr(X[i, j], Y["accuracy"][i]) for j in range(X.shape[1])]) - corr(same[i], Y["accuracy"][i]) for i in samples])
        h3[fam] = {"k": k, "same_family_r": corr(same, Y["accuracy"]), "cross_family_mean_r": float(pts.mean()),
                   "cross_p5_p95": [float(v) for v in np.percentile(pts, [5, 95])], "delta_cross_minus_same": float(pts.mean() - corr(same, Y["accuracy"])),
                   "delta_ci95": ci(d), "accepted": len(accepted), "attempts": attempts}
    result["H3_dev"] = h3
    # Exploratory: error-correlation structure within vs across families
    C = np.corrcoef(-E[listeners].to_numpy().T)
    within, across = [], []
    for i, a in enumerate(listeners):
        for j, b in enumerate(listeners):
            if j <= i:
                continue
            (within if FAMILY[a] == FAMILY[b] else across).append(C[i, j])
    result["error_correlation"] = {"mean_within_family": float(np.mean(within)), "mean_across_family": float(np.mean(across)),
                                   "pc1_share": float((np.linalg.eigvalsh(C)[::-1] / len(listeners))[0])}
    # Exploratory: prompt length and file duration (for a later non-segmental channel)
    import soundfile as sf
    dur = np.array([sf.info(GOP / w).duration for w in train.wav])
    nph = np.array([len(refs_arpa[u]) for u in ids])
    result["exploratory_timing"] = {"neg_duration_r": {a: corr(-dur, Y[a]) for a in ASPECTS},
                                    "reference_phone_count_r": {a: corr(nph, Y[a]) for a in ASPECTS},
                                    "panel_r_with_phone_count": corr(panel, nph)}
    (REDO / "results/stage1_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    # Report
    L = ["# 06 開発段階の結果（SO762 train split のみ）", "",
         f"パネル：採用規則を満たす {len(listeners)} 構成、等重み平均。発話 {len(train)}、話者 {train.spk.nunique()}。区間は話者クラスタ bootstrap（B={B}, seed={SEED}）。**test split は読んでいない。**", "",
         "## パネル平均と各評定の相関", "", "| 評定 | r | 95% 区間 |", "|---|---:|---|"]
    for a in ASPECTS:
        v = result["panel_equal_mean"][a]; L.append(f"| {a} | {v['r']:.3f} | [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] |")
    L += ["", "## 各認識器（accuracy との相関、平均誤り率、空出力数）", "", "| 認識器 | family | 平均誤り率 | r(accuracy) | 空出力 |", "|---|---|---:|---:|---:|"]
    for n in sorted(listeners, key=lambda n: -per_listener[n]["accuracy"]):
        p = per_listener[n]; L.append(f"| {n} | {p['family']} | {p['mean_error']:.3f} | {p['accuracy']:.3f} | {p['empty']} |")
    h2 = result["H2_dev"]["accuracy"]
    L += ["", "## H2（開発版）：パネル vs 同じ split で選んだ最良単一認識器", "",
          f"最良単一 = `{best}`（r={h2['r_b']:.3f}）、パネル r={h2['r_a']:.3f}、差 {h2['delta']:+.3f} [{h2['delta_ci95'][0]:+.3f}, {h2['delta_ci95'][1]:+.3f}]。単一認識器の選択が同じデータ上なので、この差は確認段階で固定した認識器で再検証する。", "",
          "## H7（開発版）：弱い 1/3 のパネル vs 強い 1/3 のパネル", ""]
    h7 = result["H7_dev"]
    L += [f"弱い 1/3（{len(weak)} 構成）r={h7['weak_panel']['r']:.3f} [{h7['weak_panel']['ci95'][0]:.3f}, {h7['weak_panel']['ci95'][1]:.3f}]、強い 1/3 r={h7['strong_panel']['r']:.3f}、弱パネル − 最良単一 = {h7['weak_minus_best_single']['delta']:+.3f} [{h7['weak_minus_best_single']['delta_ci95'][0]:+.3f}, {h7['weak_minus_best_single']['delta_ci95'][1]:+.3f}]。", "",
          "## 集約の効果（ランダム部分パネル、accuracy）", "", "| k | 平均 r | 5–95 パーセンタイル |", "|---:|---:|---|"]
    for k, v in curve.items():
        L.append(f"| {k} | {v['mean_r']:.3f} | {v['p5_p95'][0]:.3f}–{v['p5_p95'][1]:.3f} |")
    L += ["", "## H3（開発版）：同一 family vs 規模・強さを揃えた cross-family", "", "| family | k | 同一 family r | cross 平均 r | 差（cross−same） | 95% 区間 | 採択 draw |", "|---|---:|---:|---:|---:|---|---:|"]
    for fam, v in h3.items():
        if "note" in v:
            L.append(f"| {fam} | {v['k']} | – | – | – | {v['note']} | {v['accepted']} |")
        else:
            L.append(f"| {fam} | {v['k']} | {v['same_family_r']:.3f} | {v['cross_family_mean_r']:.3f} | {v['delta_cross_minus_same']:+.3f} | [{v['delta_ci95'][0]:+.3f}, {v['delta_ci95'][1]:+.3f}] | {v['accepted']} |")
    ec = result["error_correlation"]; et = result["exploratory_timing"]
    L += ["", "## 誤りの相関構造（探索）", "", f"family 内の平均相関 {ec['mean_within_family']:.3f}、family 間 {ec['mean_across_family']:.3f}、第 1 主成分の寄与 {ec['pc1_share']:.3f}。", "",
          "## 時間的特徴（探索、二次チャネル設計のための観察）", "",
          "| 評定 | r(−発話時間) | r(参照音素数) |", "|---|---:|---:|"]
    for a in ASPECTS:
        L.append(f"| {a} | {et['neg_duration_r'][a]:.3f} | {et['reference_phone_count_r'][a]:.3f} |")
    L += ["", f"パネル平均と参照音素数の相関：{et['panel_r_with_phone_count']:.3f}。", "",
          "## 次の関門", "", "読み出し仕様・パネル規則・統計手順をこの結果で変更しないと宣言し、`04_preregistration_confirmatory.md` を記入・コミットしてから SO762 test を 1 回だけ解析する。"]
    (REDO / "06_stage1_dev_report.md").write_text("\n".join(L) + "\n")
    print(json.dumps({"panel": result["panel_equal_mean"], "H2": result["H2_dev"], "H7": {k: v for k, v in h7.items() if k.endswith("panel")}, "curve": curve, "H3": h3}, indent=1))


if __name__ == "__main__":
    main()
