"""Project-root resolution for data cache directories.

Notebooks and scripts should not need to know their own location relative to
the repository root in order to read from ``data/``.  This module provides a
single helper, :func:`project_root`, which walks up from the current working
directory until a ``pyproject.toml`` is found and returns that directory.

Data adapters use this helper to resolve relative ``cache_dir`` arguments, so
that ``FREDAdapter("EXCAUS", cache_dir="data/fred")`` behaves the same whether
invoked from a deeply nested notebook, a repo-root shell, or an entry-point
script.

The helper intentionally uses CWD (rather than a caller-supplied anchor) to
match the mental model of the user running commands — in Jupyter the CWD is
the notebook directory; in a shell it is wherever the user invoked ``uv run``.
"""

from __future__ import annotations

from pathlib import Path


_SENTINEL = "pyproject.toml"


def project_root(start: Path | None = None) -> Path:
    """Return the nearest ancestor directory that contains ``pyproject.toml``.

    Parameters
    ----------
    start : Path or None
        Directory to begin the upward search from.  Defaults to
        :func:`pathlib.Path.cwd`.

    Returns
    -------
    Path
        The first ancestor (inclusive of ``start``) containing a
        ``pyproject.toml``.  If none is found, ``start`` itself is returned
        — callers should treat this fallback as "no known project root".

    Notes
    -----
    The walk stops at the filesystem root.  Results are not cached; each call
    re-walks the filesystem.  In practice this is cheap and avoids surprises
    when CWD changes (e.g. between tests).
    """
    base = (start or Path.cwd()).resolve()
    for candidate in [base, *base.parents]:
        if (candidate / _SENTINEL).is_file():
            return candidate
    return base


def resolve_under_project_root(path: str | Path) -> Path:
    """Return ``path`` resolved against the project root when relative.

    Absolute paths are returned unchanged.  Relative paths are joined to
    :func:`project_root`.

    Parameters
    ----------
    path : str or Path
        Path-like value.

    Returns
    -------
    Path
        An absolute :class:`~pathlib.Path`.
    """
    p = Path(path)
    if p.is_absolute():
        return p
    return project_root() / p
