# {{ cookiecutter.scraper_slug }} — Notes for Claude

Scaffolded from `cookiecutter-statdesk-scraper`. Inherits the StatDeskAU portfolio conventions documented in `Developer/CLAUDE.md`.

## Topology

- Python 3.12, hatchling, Pydantic v2, Click, psycopg 3.
- Source under `src/{{ cookiecutter.package_name }}/`.
- Prefect 3.x deployments on the shared `default` work pool (executed by the prefect-worker on Dokploy VPS).
- Production PG is `scraper-portfolio-pg` on the VPS; database `{{ cookiecutter.pg_database }}`.
{% if cookiecutter.has_warehouse_mirror == "y" -%}
- Warehouse mirror writes to Supabase `stats_warehouse.observations` via the pooler. `pipeline_warehouse_mirror.py` ships with `prepare_threshold=None` already wired -- do NOT remove it.
{% endif %}

## Deployments

`prefect.yaml` defines:

- `{{ cookiecutter.scraper_short_name }}-primary` — paused, cron `{{ cookiecutter.primary_cron }}`, entrypoint `pipeline_flow.py:{{ cookiecutter.primary_flow_name }}`.
{% if cookiecutter.has_warehouse_mirror == "y" -%}
- `{{ cookiecutter.scraper_short_name }}-warehouse-mirror` — paused, cron `{{ cookiecutter.mirror_cron }}`, entrypoint `pipeline_warehouse_mirror.py:mirror`.
{% endif %}

## Auto-deploy

Pushes to `{{ cookiecutter.default_branch }}` trigger `.github/workflows/deploy.yml` -> `preflight` -> `tests` -> `prefect deploy --all` -> Slack notify. PRs run preflight + tests only.

The `preflight` job enforces the 10 portfolio guards via `statdesk-preflight`. See `Developer/prefect-worker/docs/DEPLOY_AUTOMATION.md` for the operator runbook + troubleshooting.

## Lessons baked in

- `prepare_threshold=None` on every `psycopg.connect(...)` for Supabase
- `make_conninfo(host=..., user=..., password=...)` instead of URI form (dotted usernames mis-parse)
- `[ci]` extra isolates the preflight tool from `[dev]`
- Slack notify uses raw `curl` in a separate `notify` job so it survives pip-install failures
- `statdesk-prefect-tools` pinned to an immutable commit SHA (not a tag) for supply-chain hygiene

If preflight fires on one of these, the docs/troubleshooting matrix is the place to look first.
