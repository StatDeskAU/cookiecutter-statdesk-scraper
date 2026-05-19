"""Warehouse mirror for {{ cookiecutter.scraper_slug }}.

Mirrors data from the local scraper-portfolio-pg into Supabase
`stats_warehouse.observations` (or whichever cross-portfolio table this
scraper feeds).

Replace `_fetch_source_rows()` and `_upsert_target()` with real logic.
Do NOT remove `prepare_threshold=None` from `_open_supabase()` -- the
Supavisor pooler rejects session-level prepared statements and will
fail on the second `cursor.executemany(...)` without it.
"""
from __future__ import annotations

import logging

import psycopg
from prefect import flow, get_run_logger
from prefect.client.schemas.objects import State
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

import notify
from config import load_config

logger = logging.getLogger(__name__)


def _supabase_conninfo() -> str:
    """Build a keyword-form conninfo string for the Supabase pooler.

    URI form mis-parses dotted usernames (the pooler format is
    `postgres.<project-ref>`) in some libpq builds; keyword form is
    always safe.
    """
    cfg = load_config().supabase
    if not cfg.is_configured():
        raise RuntimeError(
            "SUPABASE_PG_* env vars are not all set. Configure host/user/password/database "
            "via Dokploy worker env (or .env locally)."
        )
    return make_conninfo(
        host=cfg.host,
        port=cfg.port,
        dbname=cfg.database,
        user=cfg.user,
        password=cfg.password,
    )


def _open_supabase() -> psycopg.Connection:
    """Open a Supabase connection with the pooler-safe defaults.

    `prepare_threshold=None` disables psycopg3's automatic statement
    cache. Supavisor (transaction-mode pooler) rejects session-level
    prepared statements and will return
    `DuplicatePreparedStatement: prepared statement "_pg3_0" already exists`
    on the second `executemany(...)` without this kwarg.
    """
    return psycopg.connect(
        _supabase_conninfo(),
        row_factory=dict_row,
        autocommit=False,
        prepare_threshold=None,
    )


def _fetch_source_rows() -> list[dict]:
    """Replace with real source-DB query against scraper-portfolio-pg.

    Should return a list of dicts in the target row shape (ready for
    upsert). Empty list signals "nothing to mirror this run".
    """
    return []


def _upsert_target(sb: psycopg.Connection, rows: list[dict]) -> int:
    """Replace with real upsert logic against stats_warehouse.<table>.

    Pattern:
        INSERT INTO stats_warehouse.observations (...)
        VALUES (%(col1)s, %(col2)s, ...)
        ON CONFLICT (...) DO UPDATE SET ...

    Use cursor.executemany() in chunks of ~5000. Returns rows upserted.
    """
    return 0


def _on_crashed(flow, flow_run, state: State) -> None:
    err = state.data if isinstance(state.data, BaseException) else RuntimeError(
        f"flow run {flow_run.id} crashed: {state.message}"
    )
    notify.notify_failure(err, step="prefect-on_crashed-mirror")


@flow(name="{{ cookiecutter.scraper_short_name }}-warehouse-mirror", on_crashed=[_on_crashed])
def mirror() -> int:
    """Mirror new rows from scraper-portfolio-pg into Supabase."""
    log = get_run_logger()
    current_step = "init"
    try:
        current_step = "fetch_source"
        rows = _fetch_source_rows()

        if not rows:
            notify.notify_empty("Mirror found no new source rows to sync")
            return 0

        current_step = "upsert_target"
        with _open_supabase() as sb:
            n = _upsert_target(sb, rows)
            sb.commit()

        notify.notify_success(rows_processed=n)
        return n
    except Exception as exc:
        notify.notify_failure(exc, step=current_step)
        raise


if __name__ == "__main__":
    mirror()
