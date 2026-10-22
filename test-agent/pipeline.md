When a user provides a dataset, the ML Debugger's flow would be:

1. **Validate input** – file loads correctly, expected format/schema present (CSV columns, image folder structure, tensor shapes), correct dtypes.
2. **Check integrity** – no NaN/Inf values, no duplicate rows, no empty or constant columns, no missing labels.
3. **Check the target** – valid label column, class imbalance detection.
4. **Check splits** – no train/val/test overlap, stratification correctness.
5. **Check distributions** – train vs. val shift, normalization fit on train-only.

Then it reports findings as structured JSON (`severity`, `evidence`, `suggested_fix`) that feeds into the other debugging agents.


