"""Slack notify helpers — portfolio-standard pattern.

Reads `SLACK_WEBHOOK_URL` from env. Graceful no-op when unset (so local
dev runs identically to production without the webhook set).

Wired at 5 points in {{ cookiecutter.scraper_slug }}'s Prefect flows:

  1. @flow(on_crashed=[_on_crashed]) for SIGKILL/OOM
  2. try/except around the flow body, calling notify_failure with step
  3. per-stage failure guard
  4. empty-data branch (notify_empty)
  5. success branch (notify_success)
"""
from __future__ import annotations

import logging
import os
import traceback

import requests

logger = logging.getLogger(__name__)

PIPELINE_NAME = "{{ cookiecutter.scraper_short_name }}"


def send_slack(message: str, *, is_error: bool = False) -> bool:
    """Post `message` to SLACK_WEBHOOK_URL. Never raises."""
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        logger.warning("[notify] SLACK_WEBHOOK_URL unset -- skipping (%s)", message[:80])
        return False
    try:
        resp = requests.post(url, json={"text": message}, timeout=10)
        if resp.status_code != 200:
            logger.warning("[notify] Slack returned %s: %s", resp.status_code, resp.text[:200])
            return False
        return True
    except Exception as exc:  # noqa: BLE001  -- notifications must never crash the pipeline
        logger.warning("[notify] Slack POST failed: %s", exc)
        return False


def notify_success(*, rows_processed: int = 0, summary: str = "") -> bool:
    msg = f":white_check_mark: *{PIPELINE_NAME}* run SUCCESS"
    if rows_processed:
        msg += f"  -- rows processed: {rows_processed:,}"
    if summary:
        msg += f"\n```\n{summary}\n```"
    return send_slack(msg)


def notify_failure(error: BaseException, *, step: str = "") -> bool:
    icon = ":x:"
    header = f"{icon} *{PIPELINE_NAME}* run FAILED"
    if step:
        header += f" at step `{step}`"
    tb = traceback.format_exception(type(error), error, error.__traceback__)
    body = "".join(tb)[-500:]  # last 500 chars; full trace lives in container logs
    return send_slack(f"{header}\n```\n{body}\n```", is_error=True)


def notify_empty(reason: str) -> bool:
    return send_slack(
        f":information_source: *{PIPELINE_NAME}* completed with no work\n{reason}"
    )
