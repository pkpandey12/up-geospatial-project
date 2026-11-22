# GitHub Actions (CI)

**What it is.** GitHub's built-in automation. A *workflow* (`.github/workflows/ci.yml`) runs
*jobs* on fresh virtual machines (*runners*) when *events* happen (push, pull request,
schedule).

**Why here.** Every push proves the repo still installs from the lockfile, passes lint and
tests, and that the PostGIS container starts and passes its smoke test.

## Concepts that matter

1. **Workflow → jobs → steps.** Our jobs (`lint`, `test` ×3 OSes, `db-smoke`,
   `devcontainer`) run in parallel on separate machines; steps in a job run in order.
   A **matrix** (`os: [ubuntu-latest, macos-latest, windows-latest]`) runs one job definition
   on several runners.
2. **`uses:`** pulls a reusable action, pinned by version: `actions/checkout@v5`
   (get the code), `astral-sh/setup-uv@v7` (install uv, cache packages).
3. **`run:`** is a shell command. We call `make` targets, so CI runs exactly what you run.
4. **`uv sync --locked`** makes CI fail if `uv.lock` is stale.
5. **`concurrency`** cancels an older run when you push again to the same branch.
6. **`permissions: contents: read`**: least privilege for the job's token.
7. **`if: failure()` / `if: always()`**: dump DB logs only on failure; always clean up.
8. **Secrets** (`${{ secrets.X }}`) come later for deploys. Never echo them; never put them in
   the YAML.

## Commands you'll run

Nothing locally: push a branch and open the **Actions** tab. To reproduce a failure, run
the same `make` target on your machine.

## Common mistakes

- A workflow that passes in CI but differs from local commands. Keep steps as `make` calls.
- Unpinned actions (`@main`). Pin a major version at least; pin a commit SHA for
  third-party actions in security-sensitive repos.
- Tests that need network or local files that aren't committed.

## Interview question

- *What belongs in CI for a data pipeline repo beyond unit tests?* (Lock check, lint,
  a container smoke test, dbt compile/test against a throwaway DB, and data-contract tests
  on fixtures. Keep it fast enough that people don't bypass it.)
