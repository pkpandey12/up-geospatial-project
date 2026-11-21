"""Smoke tests: the package imports and the repo layout is where the code expects it."""

import up_siting
from up_siting.common import paths


def test_version() -> None:
    assert up_siting.__version__


def test_repo_paths_exist() -> None:
    assert (paths.REPO_ROOT / "pyproject.toml").is_file()
    assert paths.PRODUCT_PROFILES_DIR.is_dir()
    assert paths.SEEDS_DIR.is_dir()
