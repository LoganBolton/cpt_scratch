"""Local graders for the Capital One OA simulation. Imported by the notebook."""

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
            mark = "PASS" if ok else "FAIL"
            print(f"[{mark}] {name}" + (f"  -> {detail}" if detail else ""))
        n_ok = sum(r[0] for r in self.rows)
        print(f"--- {n_ok}/{len(self.rows)} checks passed ---")
        return n_ok == len(self.rows)


# ---------------------------------------------------------------- Q1
def grade_q1(path="q1/analysis_results.csv"):
    r = Report("Question 1: basic analysis")
    path = os.path.join(ROOT, path)
    if not r.check("analysis_results.csv exists", os.path.exists(path), path):
        return r.show()

    got = pd.read_csv(path)
    exp = pd.read_csv(os.path.join(SOL, "q1_expected.csv"))

    r.check("columns are ['insight_type', 'value']", list(got.columns) == ["insight_type", "value"], str(list(got.columns)))
    if "insight_type" not in got.columns:
        return r.show()

    g = dict(zip(got["insight_type"], pd.to_numeric(got["value"], errors="coerce")))
    for _, row in exp.iterrows():
        key, want = row["insight_type"], float(row["value"])
        if key not in g:
            r.check(f"row '{key}' present", False)
            continue
        r.check(f"{key} == {want:.2f}", abs(g[key] - want) < 0.005, f"got {g[key]:.4f}")
    return r.show()


# ---------------------------------------------------------------- Q2
def grade_q2(path="q2/collected.csv"):
    r = Report("Question 2: feature collection")
    path = os.path.join(ROOT, path)
    if not r.check("collected.csv exists", os.path.exists(path), path):
        return r.show()

    got = pd.read_csv(path)
    exp = pd.read_csv(os.path.join(SOL, "q2_collected.csv"))

    missing = [c for c in exp.columns if c not in got.columns]
    if not r.check("all required columns present", not missing, f"missing {missing}"):
        return r.show()
    r.check(f"row count == {len(exp)}", len(got) == len(exp), f"got {len(got)}")

    got = got[exp.columns].sort_values("driver_id").reset_index(drop=True)
    exp = exp.sort_values("driver_id").reset_index(drop=True)

    for col in exp.columns:
        if col == "driver_id":
            r.check("driver_id set matches", set(got[col]) == set(exp[col]))
            continue
        if pd.api.types.is_numeric_dtype(exp[col]):
            a = pd.to_numeric(got[col], errors="coerce").to_numpy(dtype=float)
            b = exp[col].to_numpy(dtype=float)
            bad = int(np.sum(~np.isclose(a, b, atol=0.005, equal_nan=True)))
            r.check(f"{col} matches", bad == 0, f"{bad} mismatched rows")
        else:
            bad = int((got[col].astype(str) != exp[col].astype(str)).sum())
            r.check(f"{col} matches", bad == 0, f"{bad} mismatched rows")
    return r.show()


# ---------------------------------------------------------------- Q3
def grade_q3(train_path="q3/processed_train.csv", test_path="q3/processed_test.csv"):
    r = Report("Question 3: preprocessing")
    train_path, test_path = os.path.join(ROOT, train_path), os.path.join(ROOT, test_path)
    if not r.check("processed_train.csv exists", os.path.exists(train_path)):
        return r.show()
    if not r.check("processed_test.csv exists", os.path.exists(test_path)):
        return r.show()

    raw_tr = pd.read_csv(os.path.join(ROOT, "q3/data/train.csv"))
    raw_te = pd.read_csv(os.path.join(ROOT, "q3/data/test.csv"))
    tr = pd.read_csv(train_path)
    te = pd.read_csv(test_path)

    # align on driver_id when it survived preprocessing, otherwise trust row order
    def align(raw, proc):
        if "driver_id" in proc.columns and len(proc) == len(raw):
            order = pd.Series(range(len(proc)), index=proc["driver_id"])
            proc = proc.iloc[order.reindex(raw["driver_id"]).to_numpy()].reset_index(drop=True)
        return proc

    tr_aligned, te_aligned = align(raw_tr, tr), align(raw_te, te)

    r.check("train row count preserved", len(tr) == len(raw_tr), f"{len(tr)} vs {len(raw_tr)}")
    r.check("test row count preserved", len(te) == len(raw_te), f"{len(te)} vs {len(raw_te)}")

    # a) age
    fill = int(round(raw_tr["age"].mean()))
    r.check("age has no missing values", tr["age"].notna().all() and te["age"].notna().all())
    m = raw_tr["age"].isna().to_numpy()
    if m.any():
        filled = pd.to_numeric(tr_aligned.loc[m, "age"], errors="coerce").to_numpy(dtype=float)
        r.check(
            f"missing train ages filled with rounded train mean ({fill})",
            np.allclose(filled, fill, atol=0.01),
            f"got {np.unique(filled)[:5]}",
        )
    m_te = raw_te["age"].isna().to_numpy()
    if m_te.any():
        filled = pd.to_numeric(te_aligned.loc[m_te, "age"], errors="coerce").to_numpy(dtype=float)
        r.check(
            f"missing test ages filled with TRAIN mean ({fill}, no leakage)",
            np.allclose(filled, fill, atol=0.01),
            f"got {np.unique(filled)[:5]}",
        )

    # b) ordinal encoding
    for col in ["second_language", "car_model"]:
        vals = pd.to_numeric(tr[col], errors="coerce")
        ok_num = vals.notna().all()
        r.check(f"{col} is numeric", ok_num)
        if not ok_num:
            continue
        s = set(vals.astype(int))
        k = raw_tr[col].nunique()
        r.check(f"{col} encoded as 0..{k - 1}", s == set(range(k)), f"got {sorted(s)[:8]}")
        te_vals = set(pd.to_numeric(te[col], errors="coerce").dropna().astype(int))
        r.check(f"{col} test codes consistent with train", te_vals <= set(range(k)), f"got {sorted(te_vals)[:8]}")

    # c) standard scaling fit on train only
    mu, sigma = raw_tr["net_worth_of_tips"].mean(), raw_tr["net_worth_of_tips"].std(ddof=0)
    want_tr = (raw_tr["net_worth_of_tips"] - mu) / sigma
    want_te = (raw_te["net_worth_of_tips"] - mu) / sigma
    got_tr = pd.to_numeric(tr_aligned["net_worth_of_tips"], errors="coerce")
    got_te = pd.to_numeric(te_aligned["net_worth_of_tips"], errors="coerce")
    r.check("train tips standard-scaled", np.allclose(got_tr, want_tr, atol=1e-3), f"mean={got_tr.mean():.4f} std={got_tr.std(ddof=0):.4f}")
    r.check(
        "test tips scaled with TRAIN stats (no leakage)",
        np.allclose(got_te, want_te, atol=1e-3),
        f"mean={got_te.mean():.4f} (leak-free target {want_te.mean():.4f})",
    )

    # 5-decimal formatting
    pat = re.compile(r"^-?\d+\.\d{5}$")
    for label, fp in [("train", train_path), ("test", test_path)]:
        df = pd.read_csv(fp, dtype=str)
        col = df["net_worth_of_tips"].astype(str)
        bad = int((~col.map(lambda x: bool(pat.match(x)))).sum())
        r.check(f"{label} tips written with exactly 5 decimals", bad == 0, f"{bad} bad rows e.g. {col.iloc[0]}")

    # d) driver_class
    for label, df, raw in [("train", tr_aligned, raw_tr), ("test", te_aligned, raw_te)]:
        want = (raw["driver_class"] == "B class").astype(int)
        got = pd.to_numeric(df["driver_class"], errors="coerce")
        r.check(f"{label} driver_class mapped A->0 / B->1", np.array_equal(got.to_numpy(), want.to_numpy()))
    return r.show()


# ---------------------------------------------------------------- Q4
def grade_q4(path="q4/predictions.csv"):
    r = Report("Question 4: classifier")
    path = os.path.join(ROOT, path)
    if not r.check("predictions.csv exists", os.path.exists(path)):
        return r.show()

    got = pd.read_csv(path)
    y_true = pd.read_csv(os.path.join(SOL, "q4_test_labels.csv"))["driver_class"].to_numpy()

    r.check("column named 'driver_class'", list(got.columns) == ["driver_class"], str(list(got.columns)))
    if "driver_class" not in got.columns:
        return r.show()
    y_pred = pd.to_numeric(got["driver_class"], errors="coerce").to_numpy()
    if not r.check(f"row count == {len(y_true)}", len(y_pred) == len(y_true), f"got {len(y_pred)}"):
        return r.show()
    r.check("all predictions in {0, 1}", set(np.unique(y_pred)) <= {0, 1})

    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    print(f"\nFirst-10-rows preview score (accuracy): {np.mean(y_pred[:10] == y_true[:10]):.2f}")
    print(f"Full test set  ->  precision: {precision:.4f}   recall: {recall:.4f}   f1: {f1:.4f}")
    r.check("recall >= 0.85 (target)", recall >= 0.85, f"{recall:.4f}")
    r.check("precision >= 0.80 (target)", precision >= 0.80, f"{precision:.4f}")
    return r.show()
