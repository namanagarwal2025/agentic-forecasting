"""Tests for :mod:`aieng.forecasting.paths`."""

from pathlib import Path

from aieng.forecasting.paths import project_root, resolve_under_project_root


def test_project_root_finds_ancestor_with_pyproject(tmp_path: Path) -> None:
    """When ``pyproject.toml`` exists higher up, that directory is returned."""
    root = tmp_path / "proj"
    nested = root / "a" / "b" / "c"
    nested.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'x'\n")

    assert project_root(start=nested) == root.resolve()


def test_project_root_falls_back_to_start_when_no_sentinel(tmp_path: Path) -> None:
    """Without any ancestor pyproject, ``start`` itself is returned."""
    nested = tmp_path / "noproject" / "deep"
    nested.mkdir(parents=True)

    assert project_root(start=nested) == nested.resolve()


def test_project_root_handles_start_is_the_root(tmp_path: Path) -> None:
    """Start directory itself counts — walk is inclusive of ``start``."""
    root = tmp_path / "proj"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname = 'x'\n")

    assert project_root(start=root) == root.resolve()


def test_resolve_under_project_root_preserves_absolute(tmp_path: Path) -> None:
    """Absolute paths are returned unchanged."""
    abs_path = tmp_path / "somewhere" / "data"
    assert resolve_under_project_root(abs_path) == abs_path


def test_resolve_under_project_root_joins_relative(tmp_path: Path, monkeypatch) -> None:
    """Relative paths are anchored to ``project_root()``."""
    root = tmp_path / "proj"
    (root / "sub").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    monkeypatch.chdir(root / "sub")

    resolved = resolve_under_project_root("data/fred")
    assert resolved == root.resolve() / "data" / "fred"
