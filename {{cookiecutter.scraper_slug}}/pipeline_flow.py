"""Prefect entrypoint for {{ cookiecutter.scraper_slug }} (primary scrape).

Replace the body of `{{ cookiecutter.primary_flow_name }}` with the real scraping logic. The stub:
  - emits a heartbeat to Slack on success
  - notifies on crash via the @flow(on_crashed=...) hook (SIGKILL/OOM)
  - notifies on any exception via try/except with `current_step` for context
  - notifies empty-data via `notify_empty` if there is nothing to write

The 5-wiring-points pattern is portfolio-standard. Keep it intact when
filling in real logic.
"""
from __future__ import annotations

import logging

from prefect import flow, get_run_logger
from prefect.client.schemas.objects import State

import notify

logger = logging.getLogger(__name__)


def _on_crashed(flow, flow_run, state: State) -> None:
    """on_crashed hook -- catches SIGKILL / OOM that try/except can't."""
    err = state.data if isinstance(state.data, BaseException) else RuntimeError(
        f"flow run {flow_run.id} crashed: {state.message}"
    )
    notify.notify_failure(err, step="prefect-on_crashed")


@flow(name="{{ cookiecutter.primary_flow_name }}", on_crashed=[_on_crashed])
def {{ cookiecutter.primary_flow_name }}() -> int:
    """Primary scrape entrypoint. Returns rows processed (or 0 if no-op)."""
    log = get_run_logger()
    current_step = "init"
    try:
        current_step = "scraping"
        log.info("[stub] {{ cookiecutter.scraper_slug }} primary flow -- replace with real logic")
        # TODO: real scraping logic goes here

        rows_processed = 0  # TODO: actual count from your scraping logic

        if rows_processed == 0:
            notify.notify_empty("Stub flow -- no real work configured yet")
            return 0

        notify.notify_success(rows_processed=rows_processed)
        return rows_processed
    except Exception as exc:
        notify.notify_failure(exc, step=current_step)
        raise


if __name__ == "__main__":
    {{ cookiecutter.primary_flow_name }}()
