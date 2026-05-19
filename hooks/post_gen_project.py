"""Post-generation hook.

Runs in the *generated* project's directory (cookiecutter's convention).
Two responsibilities:

  1. If `has_warehouse_mirror == "n"`, delete the mirror file + its test.
  2. Always: `git init -b <default_branch>` + initial commit.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


HAS_WAREHOUSE_MIRROR = "{{ cookiecutter.has_warehouse_mirror }}"
DEFAULT_BRANCH = "{{ cookiecutter.default_branch }}"
SCRAPER_SLUG = "{{ cookiecutter.scraper_slug }}"


def _remove(path: Path) -> None:
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _strip_warehouse_mirror(project_root: Path) -> None:
    """Drop mirror file + test when the scraper doesn't need a mirror."""
    if HAS_WAREHOUSE_MIRROR == "y":
        return
    for p in (
        project_root / "pipeline_warehouse_mirror.py",
        project_root / "tests" / "test_warehouse_mirror.py",
    ):
        if p.exists():
            print(f"[post_gen] removing {p.name} (has_warehouse_mirror=n)")
            _remove(p)


def _git_init(project_root: Path) -> None:
    """Initialise a git repo + initial commit. Best-effort -- skips if git absent."""
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")

    def run(*args: str) -> int:
        return subprocess.run(
            ["git", "-C", str(project_root), *args],
            check=False,
            env=env,
        ).returncode

    if shutil.which("git") is None:
        print("[post_gen] git not on PATH -- skipping git init")
        return

    if run("init", "-q", "-b", DEFAULT_BRANCH) != 0:
        print("[post_gen] git init failed -- skipping commit")
        return
    run("add", "-A")
    # Only commit if there's something staged
    has_staged = subprocess.run(
        ["git", "-C", str(project_root), "diff", "--cached", "--quiet"],
        check=False,
    ).returncode
    if has_staged != 0:
        run(
            "commit",
            "-q",
            "-m",
            f"Initial commit from cookiecutter-statdesk-scraper ({SCRAPER_SLUG})",
        )
        print(f"[post_gen] initial commit landed on branch {DEFAULT_BRANCH}")
    else:
        print("[post_gen] nothing staged -- skipping initial commit")


def main() -> int:
    project_root = Path.cwd()
    _strip_warehouse_mirror(project_root)
    _git_init(project_root)
    print(f"[post_gen] {SCRAPER_SLUG} scaffolded at {project_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
