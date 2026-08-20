# Capital One Data Science OA — practice simulation

Open **`capital_one_oa.ipynb`** and work through the four questions. Each has a solution cell and a grader
cell right below it.

```
capital_one_oa.ipynb   the assessment
generate_data.py       regenerates all datasets (new random data each edit of the seed)
grader.py              the checks each grader cell runs
q1/ q2/ q3/ q4/        input data; you write your output files here
.solutions/            answer key + a reference solution — don't open until you're done
```

Timing: the real OA is ~70 minutes for all four. Q3 and Q4 have an 8s / 4GB execution limit; the solution
cells print their runtime.

To reset after a run:

```bash
rm -f q1/analysis_results.csv q2/collected.csv q3/processed_*.csv q4/predictions.csv
```

To get a fresh dataset (different numbers, same structure), change `RNG = np.random.default_rng(42)` in
`generate_data.py` and re-run `python generate_data.py`.
