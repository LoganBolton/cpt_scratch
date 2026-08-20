"""Local graders for OA simulation round 2. Imported by the notebook."""

import json
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
SOL = os.path.join(ROOT, ".solutions")


class Report:
    def __init__(self, title):
        self.title = title
        self.rows = []

    def check(self, name, ok, detail=""):
        self.rows.append((bool(ok), name, detail))
        return ok

    def show(self):
        print(f"=== {self.title} ===")
        for ok, name, detail in self.rows:
            print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))
        n_ok = sum(r[0] for r in self.rows)
        print(f"--- {n_ok}/{len(self.rows)} checks passed ---")
        return n_ok == len(self.rows)


def _csv(path):
    return pd.read_csv(path)


# ---------------------------------------------------------------- Q1
def grade_q1(path="q1/analysis_results.json"):
    r = Report("Round 2 / Question 1: basic analysis")
    path = os.path.join(ROOT, path)
    if not r.check("analysis_results.json exists", os.path.exists(path), path):
        return r.show()

    try:
        with open(path) as f:
            got = json.load(f)
    except Exception as e:
        r.check("file is valid JSON", False, str(e))
        return r.show()

    with open(os.path.join(SOL, "q1_truth.json")) as f:
        truth = json.load(f)

    r.check("top level is a JSON object", isinstance(got, dict), type(got).__name__)
    if not isinstance(got, dict):
        return r.show()
    extra = set(got) - set(truth)
    r.check("no unexpected keys", not extra, f"extra {sorted(extra)}")

    for key, want in truth.items():
        if key not in got:
            r.check(f"key '{key}' present", False)
            continue
        try:
            val = float(got[key])
        except (TypeError, ValueError):
            r.check(f"{key} is numeric", False, repr(got[key]))
            continue
        r.check(f"{key} == {want:.2f}", abs(val - want) < 0.005, f"got {val:.4f}")
    return r.show()


# ---------------------------------------------------------------- Q2
def grade_q2(path="q2/collected.csv"):
    r = Report("Round 2 / Question 2: feature collection")
    path = os.path.join(ROOT, path)
    if not r.check("collected.csv exists", os.path.exists(path), path):
        return r.show()

    got = _csv(path)
    exp = _csv(os.path.join(SOL, "q2_collected.csv"))

    if not r.check("file is tab-separated (>1 column parsed)", got.shape[1] > 1, f"{got.shape[1]} column(s)"):
        return r.show()

    missing = [c for c in exp.columns if c not in got.columns]
    if not r.check("all required columns present", not missing, f"missing {missing}"):
        return r.show()
    r.check(f"row count == {len(exp)}", len(got) == len(exp), f"got {len(got)}")

    got = got[exp.columns].sort_values("courier_id").reset_index(drop=True)
    exp = exp.sort_values("courier_id").reset_index(drop=True)

    for col in exp.columns:
        if col == "courier_id":
            r.check("courier_id set matches", set(got[col]) == set(exp[col]))
            continue
        if pd.api.types.is_numeric_dtype(exp[col]):
            a = pd.to_numeric(got[col], errors="coerce").to_numpy(dtype=float)
            b = exp[col].to_numpy(dtype=float)
            tol = 0.0005 if col == "on_time_rate" else 0.005
            bad = int(np.sum(~np.isclose(a, b, atol=tol, equal_nan=True)))
            r.check(f"{col} matches", bad == 0, f"{bad} mismatched rows")
        else:
            bad = int((got[col].astype(str) != exp[col].astype(str)).sum())
            r.check(f"{col} matches", bad == 0, f"{bad} mismatched rows")
    return r.show()


# ---------------------------------------------------------------- Q3
def grade_q3(train_path="q3/processed_train.csv", test_path="q3/processed_test.csv"):
    r = Report("Round 2 / Question 3: preprocessing")
    train_path, test_path = os.path.join(ROOT, train_path), os.path.join(ROOT, test_path)
    if not r.check("processed_train.csv exists", os.path.exists(train_path)):
        return r.show()
    if not r.check("processed_test.csv exists", os.path.exists(test_path)):
        return r.show()

    raw_tr = _csv(os.path.join(ROOT, "q3/data/train.csv"))
    raw_te = _csv(os.path.join(ROOT, "q3/data/test.csv"))
    tr, te = _csv(train_path), _csv(test_path)

    if not r.check("output is tab-separated", tr.shape[1] > 1 and te.shape[1] > 1):
        return r.show()
    r.check("train row count preserved", len(tr) == len(raw_tr), f"{len(tr)} vs {len(raw_tr)}")
    r.check("test row count preserved", len(te) == len(raw_te), f"{len(te)} vs {len(raw_te)}")

    def align(raw, proc):
        if "courier_id" in proc.columns and len(proc) == len(raw):
            order = pd.Series(range(len(proc)), index=proc["courier_id"])
            proc = proc.iloc[order.reindex(raw["courier_id"]).to_numpy()].reset_index(drop=True)
        return proc

    tr_a, te_a = align(raw_tr, tr), align(raw_te, te)

    # a) median imputation of avg_delivery_minutes, fit on train
    med = round(float(raw_tr["avg_delivery_minutes"].median()), 2)
    r.check(
        "avg_delivery_minutes has no missing values",
        tr["avg_delivery_minutes"].notna().all() and te["avg_delivery_minutes"].notna().all(),
    )
    for label, raw, proc in [("train", raw_tr, tr_a), ("test", raw_te, te_a)]:
        m = raw["avg_delivery_minutes"].isna().to_numpy()
        if m.any():
            filled = pd.to_numeric(proc.loc[m, "avg_delivery_minutes"], errors="coerce").to_numpy(dtype=float)
            r.check(
                f"{label} gaps filled with TRAIN median rounded to 2dp ({med})",
                np.allclose(filled, med, atol=0.001),
                f"got {np.unique(filled)[:5]}",
            )

    # b1) city ordinal, alphabetical, 0..k-1
    cities = sorted(raw_tr["city"].unique())
    want_map = {c: i for i, c in enumerate(cities)}
    got_city = pd.to_numeric(tr_a["city"], errors="coerce")
    if r.check("city is numeric", got_city.notna().all()):
        r.check(
            f"city encoded alphabetically 0..{len(cities) - 1}",
            np.array_equal(got_city.to_numpy(dtype=int), raw_tr["city"].map(want_map).to_numpy()),
            f"expected {want_map}",
        )
        got_city_te = pd.to_numeric(te_a["city"], errors="coerce")
        r.check(
            "test city uses the same mapping",
            np.array_equal(got_city_te.to_numpy(dtype=int), raw_te["city"].map(want_map).to_numpy()),
        )

    # b2) vehicle_type one-hot
    vtypes = sorted(raw_tr["vehicle_type"].unique())
    want_cols = [f"vehicle_type_{v}" for v in vtypes]
    have = [c for c in want_cols if c in tr.columns]
    if r.check(f"one-hot columns present ({len(want_cols)})", len(have) == len(want_cols), f"missing {set(want_cols) - set(have)}"):
        r.check("original vehicle_type column dropped", "vehicle_type" not in tr.columns)
        oh = tr_a[want_cols].apply(pd.to_numeric, errors="coerce")
        r.check("one-hot values are 0/1", set(np.unique(oh.to_numpy())) <= {0, 1})
        r.check("exactly one 1 per row", bool((oh.sum(axis=1) == 1).all()))
        idx = oh.to_numpy().argmax(axis=1)
        decoded = np.array(vtypes)[idx]
        r.check("one-hot matches the source vehicle_type", np.array_equal(decoded, raw_tr["vehicle_type"].to_numpy()))
        r.check("test has the same one-hot columns", all(c in te.columns for c in want_cols))

    # c) min-max scaling of total_earnings, train-fit, 4 decimals
    lo, hi = raw_tr["total_earnings"].min(), raw_tr["total_earnings"].max()
    want_tr = (raw_tr["total_earnings"] - lo) / (hi - lo)
    want_te = (raw_te["total_earnings"] - lo) / (hi - lo)
    got_tr = pd.to_numeric(tr_a["total_earnings"], errors="coerce")
    got_te = pd.to_numeric(te_a["total_earnings"], errors="coerce")
    r.check("train total_earnings min-max scaled to [0,1]", np.allclose(got_tr, want_tr, atol=1e-3),
            f"min={got_tr.min():.4f} max={got_tr.max():.4f}")
    r.check("test scaled with TRAIN min/max (no leakage)", np.allclose(got_te, want_te, atol=1e-3),
            f"got min={got_te.min():.4f} vs leak-free {want_te.min():.4f}")

    pat = re.compile(r"^-?\d+\.\d{4}$")
    for label, fp in [("train", train_path), ("test", test_path)]:
        col = pd.read_csv(fp, dtype=str)["total_earnings"].astype(str)
        bad = int((~col.map(lambda x: bool(pat.match(x)))).sum())
        r.check(f"{label} total_earnings written with exactly 4 decimals", bad == 0,
                f"{bad} bad rows e.g. {col.iloc[0]}")

    # d) target mapping
    for label, proc, raw in [("train", tr_a, raw_tr), ("test", te_a, raw_te)]:
        want = (raw["courier_tier"] == "Gold").astype(int)
        got = pd.to_numeric(proc["courier_tier"], errors="coerce")
        r.check(f"{label} courier_tier mapped Standard->0 / Gold->1",
                np.array_equal(got.to_numpy(), want.to_numpy()))
    return r.show()


# ---------------------------------------------------------------- Q4
def grade_q4(path="q4/predictions.csv"):
    r = Report("Round 2 / Question 4: classifier")
    path = os.path.join(ROOT, path)
    if not r.check("predictions.csv exists", os.path.exists(path)):
        return r.show()

    got = pd.read_csv(path)
    y_true = _csv(os.path.join(SOL, "q4_test_labels.csv"))["courier_tier"].to_numpy()

    r.check("single column named 'courier_tier'", list(got.columns) == ["courier_tier"], str(list(got.columns)))
    if "courier_tier" not in got.columns:
        return r.show()
    y_pred = pd.to_numeric(got["courier_tier"], errors="coerce").to_numpy()
    if not r.check(f"row count == {len(y_true)}", len(y_pred) == len(y_true), f"got {len(y_pred)}"):
        return r.show()
    r.check("all predictions in {0, 1}", set(np.unique(y_pred)) <= {0, 1})

    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    print(f"\nFirst-10-rows preview (accuracy): {np.mean(y_pred[:10] == y_true[:10]):.2f}")
    print(f"Full test set  ->  precision: {precision:.4f}   recall: {recall:.4f}   F1: {f1:.4f}")
    r.check("F1 >= 0.85 (target)", f1 >= 0.85, f"{f1:.4f}")
    r.check("recall >= 0.80 (floor)", recall >= 0.80, f"{recall:.4f}")
    return r.show()
