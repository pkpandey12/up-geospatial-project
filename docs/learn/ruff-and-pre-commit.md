# ruff and pre-commit

**What they are.** **ruff** is a very fast Python linter *and* formatter (replaces flake8,
isort, pyupgrade, black). **pre-commit** is a framework that runs checks as git hooks before
each commit.

**Why here.** Style is decided by a tool, not in review; mistakes like unused imports,
undefined names and mutable defaults are caught in milliseconds, including inside notebooks.

## Concepts that matter

1. **Lint vs format.** `ruff check` finds problems (some auto-fixable with `--fix`);
   `ruff format` rewrites layout. CI runs `ruff format --check` (fail, don't fix).
2. **Rule sets** are chosen in `pyproject.toml` → `[tool.ruff.lint] select`. Ours: E/W
   (pycodestyle), F (pyflakes), I (import order), B (bugbear), UP (modern syntax),
   SIM (simplify), RUF.
3. **Per-file ignores** for notebooks (imports mid-notebook, long comment lines), and
   RUF001-003 off because ₹ and Devanagari are intentional here.
4. **`# noqa: F401`** silences one rule on one line. Use sparingly and say why (notebook 02
   does, for imports your TODO cells will use).
5. **pre-commit hooks** come from remote repos pinned by `rev` (whitespace, YAML, large files,
   private keys) or are `local` (ours run `uv run ruff`, so hook, `make lint` and CI share one
   version from `uv.lock`).
6. Hooks run only on **staged files**; `pre-commit run --all-files` checks everything.
   We don't use `pre-commit install` (it hard-codes one Python path, which breaks when you
   commit from both the host and the Dev Container). Instead `make setup` runs
   `git config core.hooksPath .githooks`, and `.githooks/pre-commit` calls
   `uv run pre-commit run`, which works on either side.
7. A hook that **modifies** files (formatter, whitespace fixer) fails the commit; review,
   `git add` the fixes and commit again.

## Commands you'll run

```bash
make lint                          # what CI runs
make format                        # fix what's fixable
uv run pre-commit run --all-files
uv run ruff rule B006              # explain a rule
git commit --no-verify             # skip hooks (emergencies only; CI will still catch it)
```

## Common mistakes

- Fighting the formatter. Accept its output; argue in `pyproject.toml` once, not per file.
- Blanket `# noqa` without a code.
- Forgetting `make setup` on a new clone, so hooks aren't enabled.

## Interview question

- *Why run the same checks in pre-commit and in CI?* (Pre-commit gives fast local feedback but
  is optional and skippable; CI is the enforced gate.)
