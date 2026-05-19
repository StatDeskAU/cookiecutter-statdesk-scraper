"""Validate prefect.yaml against the portfolio-shape schema."""
from __future__ import annotations

from pathlib import Path

from statdesk_prefect_tools.preflight.yaml_schema import parse_prefect_yaml


def test_prefect_yaml_matches_portfolio_schema() -> None:
    """Smoke test: prefect.yaml round-trips through the Pydantic model.

    This catches drift between this scraper's manifest and the
    portfolio-wide shape (work_pool=default, PGDATABASE in job_variables,
    secret-block access_token, etc.) at unit-test time, before CI ever
    invokes statdesk-preflight.
    """
    yaml_path = Path(__file__).resolve().parent.parent / "prefect.yaml"
    parsed = parse_prefect_yaml(yaml_path.read_text(encoding="utf-8"))

    assert parsed.name == "{{ cookiecutter.scraper_short_name }}"
    assert len(parsed.deployments) >= 1
    for dep in parsed.deployments:
        assert dep.work_pool.name == "default"
        assert dep.paused is True, f"{dep.name!r} is not paused"
        assert dep.job_variables.env.PGDATABASE == "{{ cookiecutter.pg_database }}"
