# Jupyter notebooks and the EDA notebook pattern

**What it is.** JupyterLab runs notebooks: documents of markdown and code cells executed by a
*kernel* (here, the project's Python via `uv run`). Outputs are saved inside the `.ipynb`
(JSON) file.

**Why here.** EDA is a conversation with data. Notebooks keep the question, the code, the
evidence and the conclusion together. Reusable logic goes into `src/` with tests; the notebook
calls it.

## The pattern (worked example: `notebooks/eda/01_spine.ipynb`)

1. **Header cell**: purpose, inputs, outputs, how to run.
2. **One setup cell**: imports, paths from `up_siting.common.paths`, parameters overridable by
   environment variables (so tests can run the notebook on fixtures).
3. **Sections**, each:
   - a markdown cell stating **one question** ("Is the LGD code a clean primary key?"),
   - code cells that answer it, mostly DuckDB SQL over DataFrames,
   - an **assert cell** that turns the answer into a check. *Run All* stops at the first
     broken assumption.
4. **Write outputs**, then **read them back** and assert on the files.
5. **Findings** cell, copied to `docs/eda/NN_*.md` and the data-quality log.

## Concepts that matter

- **Hidden state.** Cells run in the order you click, not top to bottom. Before trusting a
  result: *Kernel → Restart and Run All*. `tests/test_notebooks.py` does this for 01.
- **Paths**: never absolute; use `up_siting.common.paths`.
- **Outputs in git**: 01 is committed *with* outputs so GitHub shows the evidence (a
  *Decision needed*: keep vs strip).
- **ruff lints notebooks** too (`make lint`).

## Commands you'll run

```bash
make lab                                           # JupyterLab at notebooks/eda
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/eda/01_spine.ipynb
```

## Common mistakes

- 300-line cells. One step per cell; move functions to `src/` once they're reused.
- `df.head()` as the only check. Write the assert.
- Copy-pasting a cell to "try something" and leaving both. Delete dead cells.

## Interview question

- *How do you make notebook-based analysis reproducible?* (Pinned environment, relative paths,
  parameters, restart-and-run-all in CI, asserts, logic in tested modules.)
