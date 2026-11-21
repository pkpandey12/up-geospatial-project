# pytest

**What it is.** Python's de facto test framework: plain `assert` statements in functions named
`test_*`, discovered automatically, with fixtures for setup and markers for grouping.

**Why here.** Every function you write has a test that defines "done". The data work adds its
own kind of test: assertions on real files (the LGD PDF fixture) and on notebook outputs.

## Concepts that matter

1. **Discovery.** Files `tests/test_*.py`, functions `test_*`. Config lives in
   `[tool.pytest.ini_options]` in `pyproject.toml`.
2. **Plain `assert`.** pytest rewrites asserts to show both sides on failure, so no
   `assertEqual` boilerplate.
3. **Fixtures** are setup functions injected by argument name (`def test_x(lgd_pdf):`).
   Shared ones live in `tests/conftest.py`. Built-ins you'll use: `tmp_path`, `monkeypatch`.
   `scope="module"` runs an expensive fixture (parsing the PDF) once per file.
4. **`parametrize`** runs one test over many inputs; ideal for boundaries
   (`size_class` at 0.99, 1, 2, 5).
5. **`pytest.raises(ValueError, match=...)`** asserts an error *and* its message.
6. **Markers** tag tests. Ours: `integration` (needs the DB; skipped by `make test`),
   `notebook`, and `todo` (yours).
7. **xfail.** `conftest.py` marks `todo` tests as *expected to fail with NotImplementedError*.
   While a stub raises, you see `x`; once you implement it, a wrong answer fails red and a
   right one passes. `--runxfail` (used by `make todo`) ignores the marker.
8. **Test the contract, not the implementation**: row counts, dtypes, invariants
   ("same rows in, same rows out"), error messages.

## Commands you'll run

```bash
make test                       # everything except integration
make todo                       # just your TODOs, honest pass/fail
uv run pytest tests/test_names.py -k map_to_lgd -x -vv   # one area, stop at first failure
uv run pytest --lf              # re-run last failures
uv run pytest -m integration    # needs make db-up
uv run pytest --pdb             # drop into the debugger on failure
```

## Common mistakes

- Tests that depend on each other's order or on files outside `tests/fixtures`.
- Asserting floats with `==`. Use `pytest.approx`.
- Fixtures that mutate shared data: return fresh copies (`copy.deepcopy`).
- A test that can't fail. Break the code on purpose once and watch it go red.

## Interview questions

- *How do you test a data pipeline step, beyond unit tests?* (Contract tests on schema, row
  counts and keys; fixture files from real sources; idempotency, where running twice gives
  the same result; data-quality tests in the warehouse, which is dbt tests later.)
- *What's a fixture and why prefer it over setUp/tearDown?*
