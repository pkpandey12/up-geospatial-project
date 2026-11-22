# make

**What it is.** A 1976 build tool that runs shell commands ("recipes") for named "targets",
optionally only when files are out of date. Here it's used as a **task runner**: one short,
discoverable command per workflow.

**Why here.** `make setup / test / lint / db-up` is the same on your machine, in CI and in the
README. Nobody needs to remember `uv run pytest -m 'not integration'`.

## Concepts that matter

1. **Target: prerequisites, then recipe.** `setup: check-tools env` runs those two first.
2. **`.PHONY`** marks targets that aren't files, so make always runs them.
3. **Recipes are indented with a TAB**, not spaces. The classic error is
   `*** missing separator`.
4. **Each recipe line runs in its own shell**: `cd` on one line doesn't carry to the next.
5. **`$$`** passes a literal `$` to the shell (`$$(uv --version)`); a single `$` is a make variable.
6. **`-include .env` + `?=` defaults + `export`** loads `KEY=value` lines as make variables,
   fills in defaults for anything missing, and exports them to commands. The defaults matter:
   exporting a variable that was never set exports an *empty string*, and docker compose lets
   shell variables override `.env`, so a fresh clone's first `make db-up` failed in CI until
   this was fixed.
   `ifdef UP_SITING_DEVCONTAINER` switches targets when running inside the Dev Container.
7. **`@`** hides the command echo; **`$(MAKE) target`** calls another target (used by `db-up`).
8. **Self-documenting help**: `## comment` after a target name is printed by `make help`.
9. **`.SHELLFLAGS := -eu -o pipefail -c`**: stop on errors, unset variables and failed pipes.

## Commands you'll run

```bash
make            # = make help
make setup test lint
make db-up db-psql db-down
make -n db-up   # dry run: print what it would do
```

## Common mistakes

- Spaces instead of a tab in a recipe.
- Expecting `cd somewhere` on one line to affect the next.
- Putting real logic in the Makefile. Keep recipes one-liners that call scripts/tools.

## Interview question

- *Why a Makefile in a Python project rather than just a README of commands?*
  (Executable documentation; CI and humans run the same entry points, and they don't drift.)
