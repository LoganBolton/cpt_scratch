# Round 2 — food-delivery couriers

Open **`capital_one_oa_round2.ipynb`**. Same four-question shape as round 1, new data, new domain, new twists.

What's deliberately different from round 1, so you can't coast on muscle memory:

| | round 1 | round 2 |
|---|---|---|
| inputs | all CSV | JSON + CSV |
| outputs | CSV | JSON (Q1), CSV (Q2–Q4) |
| joins | 2 tables | 3 tables (`zones` lookup added) |
| dates | ISO everywhere | `last_service_date` is `DD/MM/YYYY` |
| Q1 stats | means only | includes a **median** |
| Q2 wrinkle | plain counts | a **rate over a filtered subset** (delivered orders only) + a zero-denominator case |
| Q3 imputation | mean, rounded to int | **median**, rounded to 2dp |
| Q3 categoricals | ordinal only | ordinal **in alphabetical order** + **one-hot** |
| Q3 scaling | StandardScaler, 5dp | **MinMax**, 4dp |
| Q4 objective | maximize recall | maximize **F1** |

Reset after a run:

```bash
rm -f q1/analysis_results.json q2/collected.csv q3/processed_*.csv q4/predictions.csv
```

Fresh data: change the seed in `generate_data.py` and re-run it.
