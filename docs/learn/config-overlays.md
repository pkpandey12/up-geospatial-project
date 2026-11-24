# Config overlays: keeping the partner's figures out of git

**What it is.** A *base* config that's safe to publish, plus an *overlay* file with the same
shape that's applied on top at load time and never committed. The same idea as Helm's
`values.yaml` + `values-prod.yaml`, Kustomize overlays, or dbt's `profiles.yml` living
outside the repo.

**Why here.** The partner's plant figures, prices and his good/avoid district list are
business-confidential, and the repo may go public. But the model needs them, and the public
values (from reports, with citations) still matter: they're the fallback and the check.

Code: `src/up_siting/profiles/overlay.py` (worked example), used by `load_profile(path,
private_dir)`. Tests: `tests/test_overlay.py`.

```
config/product_profiles/
  ethanol.yaml                         public, committed, every value cited
  private/ethanol.example.yaml         committed: SHAPE ONLY, placeholder numbers
  private/ethanol.yaml                 partner values, git-ignored
  private/ethanol.districts.yaml       sealed good/avoid list, git-ignored
```

## Concepts that matter

1. **Field-by-field merge.** The overlay sets only what the partner gave; everything else
   stays public. Nested mappings merge key by key.
2. **Lists merge by key, not position.** `raw_materials` merge on `id`, so "maize" in the
   overlay updates the public maize entry wherever it sits; a new id is appended.
3. **Provenance travels with the value.** Every overlaid value is tagged
   `source: partner` automatically, so every output can say which numbers were the
   partner's and which came from a report (and with what confidence).
4. **Defence in depth against leaks.** (a) `.gitignore` hides `**/private/*` except
   `*.example.yaml`; (b) the `no-private-files` pre-commit hook fails if a private file is
   staged anyway (`git add -f`); (c) a test in CI fails if any non-example file under
   `private/` is tracked.
5. **Public by default.** `load_profile(path)` without `private_dir` never reads the
   overlay; tests and CI never pass it. Notebooks opt in explicitly.
6. **Shape files.** `*.example.yaml` documents the format with obviously fake numbers and
   is tested to be a valid overlay, so it can't drift from the schema.

## Commands you'll run

```bash
cp config/product_profiles/private/ethanol.example.yaml config/product_profiles/private/ethanol.yaml
# edit the numbers, then:
uv run validate-profiles config/product_profiles --private --show-missing
git status        # private/ethanol.yaml must NOT appear
```

In a notebook:

```python
from up_siting.common.paths import PRODUCT_PROFILES_DIR
from up_siting.profiles.validate import load_profile

eth = load_profile(PRODUCT_PROFILES_DIR / "ethanol.yaml", PRODUCT_PROFILES_DIR / "private")
{p: v.source for p, v in eth.provenance.items()}  # which values are the partner's
```

## Common mistakes

- Printing partner values in a **committed notebook output**. Notebooks that load the
  overlay must show sources and confidence, not the private numbers, or be cleared before
  commit. (Outputs are kept in git, so this is the likeliest leak.)
- Copying a private value into the public YAML "temporarily".
- Partner data in a filename or commit message (the guard checks paths, not words).
- Before going public: scrub history too (`git log --all -- '*private*'` should be empty).

## Interview questions

- *How do you keep secrets and confidential config out of a repo while still versioning
  the shape?* (Base + overlay, ignore rules, pre-commit and CI guards, example files,
  secrets managers for credentials.)
- *Why merge lists by key instead of replacing them?* (Positional merges break silently
  when someone reorders or inserts an entry.)
