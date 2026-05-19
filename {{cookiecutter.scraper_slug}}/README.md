# {{ cookiecutter.scraper_slug }}

{{ cookiecutter.scraper_description }}

Scaffolded from [`cookiecutter-statdesk-scraper`](https://github.com/StatDeskAU/cookiecutter-statdesk-scraper).

## Deployments

| Name | Schedule (cron) | Flow |
|---|---|---|
| `{{ cookiecutter.scraper_short_name }}-primary` | `{{ cookiecutter.primary_cron }}` (paused) | `pipeline_flow.py:{{ cookiecutter.primary_flow_name }}` |
{% if cookiecutter.has_warehouse_mirror == "y" -%}
| `{{ cookiecutter.scraper_short_name }}-warehouse-mirror` | `{{ cookiecutter.mirror_cron }}` (paused) | `pipeline_warehouse_mirror.py:mirror` |
{% endif %}

All deployments ship `paused: true`. Unpause via the Prefect UI once you've validated the first manual run.

## Local development

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev,prefect,ci]"
cp .env.example .env  # fill in PG creds for local PG, if needed

# Run preflight (the same guards CI uses)
.venv/Scripts/python.exe -m statdesk_prefect_tools.preflight.runner .

# Run tests
.venv/Scripts/python.exe -m pytest -q
```

## Deployment

Push to `{{ cookiecutter.default_branch }}` and GitHub Actions handles the rest:

1. `preflight` — runs the 10 portfolio guards
2. `tests` — `pytest -q`
3. `deploy` — `prefect deploy --all` against `prefect.statdesk.com.au`
4. `notify` — Slack message with success/failure

See [`docs/DEPLOY_AUTOMATION.md`](https://github.com/StatDeskAU/prefect-worker/blob/main/docs/DEPLOY_AUTOMATION.md) in `prefect-worker` for the full operator runbook.

## What you (the operator) need to do next

1. Replace the stub in `pipeline_flow.py:{{ cookiecutter.primary_flow_name }}` with the real scraping logic. The stub returns 0 and posts a Slack heartbeat.
{% if cookiecutter.has_warehouse_mirror == "y" -%}
2. Replace the stub in `pipeline_warehouse_mirror.py:mirror` with the real fetch + upsert. The skeleton already includes the `prepare_threshold=None` + `make_conninfo()` Supabase pattern.
{% endif %}
{% if cookiecutter.has_warehouse_mirror == "y" -%}3. {% else %}2. {% endif %}Make sure the GH repo `{{ cookiecutter.github_org }}/{{ cookiecutter.scraper_slug }}` has the four Actions configs visible to it (org-level on Team plan, repo-level on Free plan):

   - secret `PREFECT_API_AUTH_STRING`
   - secret `SLACK_WEBHOOK_URL`
   - variable `PREFECT_API_URL`
