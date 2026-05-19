"""Sanity tests for the warehouse mirror stub.

These tests run without a live Supabase connection -- they only verify
that the static patterns the preflight guards check are in place:

  - `prepare_threshold=None` on the Supabase connect call
  - `make_conninfo(...)` (keyword form) instead of a URI literal

Replace / extend once the real mirror logic lands; do NOT delete these
checks -- they're cheap defense against accidental regressions of the
two most expensive Supabase-pooler gotchas in the portfolio.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


MIRROR_PATH = Path(__file__).resolve().parent.parent / "pipeline_warehouse_mirror.py"


@pytest.fixture(scope="module")
def mirror_source() -> str:
    return MIRROR_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def mirror_tree(mirror_source: str) -> ast.Module:
    return ast.parse(mirror_source)


def _find_psycopg_connect_calls(tree: ast.Module) -> list[ast.Call]:
    calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # psycopg.connect(...)
            if isinstance(func, ast.Attribute) and func.attr == "connect":
                if isinstance(func.value, ast.Name) and func.value.id == "psycopg":
                    calls.append(node)
    return calls


def test_supabase_connect_sets_prepare_threshold_none(mirror_tree: ast.Module) -> None:
    """The Supavisor pooler rejects session-level prepared statements.

    Without `prepare_threshold=None`, the second `cursor.executemany`
    against the pooler raises `DuplicatePreparedStatement`.
    """
    calls = _find_psycopg_connect_calls(mirror_tree)
    assert calls, "no psycopg.connect(...) calls found in pipeline_warehouse_mirror.py"
    for call in calls:
        kwargs = {kw.arg for kw in call.keywords if kw.arg}
        assert "prepare_threshold" in kwargs, (
            f"psycopg.connect at line {call.lineno} is missing prepare_threshold=None"
        )


def test_no_uri_form_supabase_conninfo(mirror_source: str) -> None:
    """Reject `postgresql://...supabase...` URI literals.

    The bundled libpq mis-parses dotted Supabase pooler usernames
    (`postgres.<project-ref>`) in URI form. `make_conninfo()` is safe.
    """
    lowered = mirror_source.lower()
    assert "postgresql://" not in lowered or "supabase" not in lowered, (
        "Supabase connection in URI form -- use make_conninfo(host=..., user=..., password=...) instead"
    )
