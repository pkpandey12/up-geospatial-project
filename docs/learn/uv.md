# uv

**What it is.** A fast Python package and project manager from Astral (written in Rust). It
replaces pip, pip-tools, virtualenv, pyenv and most of poetry: it installs Python itself,
creates the virtual environment, resolves and locks dependencies, and runs commands inside
the environment.

**Why here.** One tool, one lockfile, so `make setup` on your laptop, in CI and in a fresh
cloud container gives the same versions of every package.

## Concepts that matter

1. **`pyproject.toml`** declares what you *want* (ranges like `pandas>=3.0`).
   **`uv.lock`** records what you *got* (exact versions + hashes for every platform). Commit both.
2. **`.python-version`** pins the interpreter (3.12). uv downloads it if missing.
3. **`.venv/`** is the project's virtual environment. You rarely activate it: `uv run <cmd>`
   runs inside it and syncs first if needed.
4. **Dependency groups.** `[project] dependencies` = what the code needs at runtime;
   `[dependency-groups] dev` = tools (pytest, ruff, jupyter). `uv sync` installs both.
5. **`uv sync --locked`** fails if `uv.lock` doesn't match `pyproject.toml`. CI uses it so a
   forgotten lock update is caught. `--frozen` uses the lock without checking it (used in hooks
   for speed).
6. **Editable install.** The project itself (`src/up_siting`) is installed in editable mode, so
   `import up_siting` works everywhere and picks up your edits without reinstalling.
7. **`[project.scripts]`** creates commands: `validate-profiles` maps to
   `up_siting.profiles.validate:main`.

## Commands you'll run

```bash
uv sync                      # create/update .venv from the lock (make setup does this)
uv add rapidfuzz             # add a runtime dependency (updates pyproject + lock)
uv add --dev pytest-cov      # add a dev tool
uv remove rapidfuzz
uv lock --upgrade-package duckdb   # bump one package within its range
uv run pytest -k names       # run anything inside the environment
uv run python -c "import duckdb; print(duckdb.__version__)"
uv tree                      # who depends on what
```

## Common mistakes

- `pip install x` into the venv: it works until the next `uv sync` silently removes it. Use `uv add`.
- Editing `pyproject.toml` by hand and not re-locking → CI fails on `--locked`. Run `uv lock`.
- Activating some other venv/conda env and wondering why imports differ. Use `uv run`.
- Committing `.venv/`. It's ignored; it's machine-specific.

## Interview questions

- *Why commit a lockfile for an application but often not for a library?*
  (An app wants reproducible deploys; a library must work across its users' ranges, so its
  CI should test against ranges, not a single lock.)
- *What's the difference between a version range in pyproject and the lockfile?*
