"""Smoke-test that prefect.yaml parses + has the portfolio-shape essentials.

Deliberately uses raw `yaml.safe_load` (not `statdesk_prefect_tools.preflight
.yaml_schema`) so the test stays runnable with just `pip install -e .[dev]`
-- no `[ci]` extra required. Full schema validation lives in the preflight
CI job, which DOES install `[ci]`.
"""
from __future__ import annotations

from pathlib import Path

import yaml


PREFECT_YAML = Path(__file__).resolve().parent.parent / "prefect.yaml"


def test_prefect_yaml_parses_and_names_pipeline() -> None:
    data = yaml.safe_load(PREFECT_YAML.read_text(encoding="utf-8"))
    assert data["name"] == "{{ cookiecutter.scraper_short_name }}"
    assert "deployments" in data
    assert len(data["deployments"]) >= 1


def test_every_deployment_is_paused_and_on_default_pool() -> None:
    data = yaml.safe_load(PREFECT_YAML.read_text(encoding="utf-8"))
    for dep in data["deployments"]:
        assert dep["work_pool"]["name"] == "default", f"{dep['name']!r} is not on default pool"
        assert dep["paused"] is True, f"{dep['name']!r} is not paused"
        # PGDATABASE wired through to the worker
        assert "PGDATABASE" in dep["job_variables"]["env"]
