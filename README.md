# cookiecutter-statdesk-scraper

Cookiecutter template that scaffolds a new StatDeskAU scraper repo
configured for the portfolio's automated Prefect deployment pipeline.

## Usage

```bash
pip install cookiecutter        # one-time
cookiecutter gh:StatDeskAU/cookiecutter-statdesk-scraper
```

Cookiecutter will prompt for the variables in [`cookiecutter.json`](cookiecutter.json):

| Variable | Default | Notes |
|---|---|---|
| `scraper_number` | `0099` | 4-digit portfolio number |
| `scraper_short_name` | `template-smoke` | Used in deployment names, Slack messages |
| `scraper_slug` | `{short_name}-scraper` | GH repo name + package import alias |
| `package_name` | derived from slug | Python package name (snake_case) |
| `github_org` | `StatDeskAU` | GH org owning the new repo |
| `default_branch` | `main` | Auto-deploy is triggered on push to this branch |
| `has_warehouse_mirror` | `y` | Set to `n` to scaffold without the Supabase mirror |
| `pg_database` | derived from package | Scraper-portfolio-pg database name |
| `primary_cron` | `0 19 * * *` | Cron for the primary deployment (UTC) |
| `mirror_cron` | `30 20 * * *` | Cron for the warehouse-mirror deployment (UTC) |
| `statdesk_prefect_tools_sha` | pinned SHA | Immutable commit SHA of statdesk-prefect-tools |

After scaffolding, push the generated repo to GitHub and the [auto-deploy
workflow](https://github.com/StatDeskAU/prefect-worker/blob/main/docs/DEPLOY_AUTOMATION.md)
takes over.

## What it scaffolds

A ready-to-deploy scraper with:

- `prefect.yaml` with 1-2 paused deployments on the shared `default` work pool
- `pipeline_flow.py` stub @flow with the portfolio 5-wiring-points notify pattern
- `pipeline_warehouse_mirror.py` (optional) with `prepare_threshold=None` + `make_conninfo()` pre-baked
- `notify.py` for Slack messaging
- `config.py` (Pydantic v2 AppConfig + DatabaseConfig + SupabaseConfig)
- `pyproject.toml` with the `[ci]` extra (SHA-pinned `statdesk-prefect-tools`) + hatchling opt-in
- `.github/workflows/deploy.yml` (preflight + tests + deploy + notify jobs)
- `tests/test_prefect_yaml.py` validating against the portfolio schema
- `tests/test_warehouse_mirror.py` AST-asserting the two Supabase-pooler gotchas
- `CLAUDE.md` + `README.md` + `.env.example` + `.gitignore`

The post-generation hook initialises a git repo and lands an initial commit.

## Adding a new scraper

1. Generate locally:
   ```bash
   cookiecutter gh:StatDeskAU/cookiecutter-statdesk-scraper
   ```
2. Create the empty GH repo (`gh repo create StatDeskAU/<scraper-slug> --private --confirm`).
3. `cd <scraper-slug>` and `git remote add origin git@github.com:StatDeskAU/<scraper-slug>.git`.
4. `git push -u origin main`. CI runs preflight + tests + deploy automatically.

Operator runbook (one-time secrets setup, troubleshooting, rotation) lives at
[`prefect-worker/docs/DEPLOY_AUTOMATION.md`](https://github.com/StatDeskAU/prefect-worker/blob/main/docs/DEPLOY_AUTOMATION.md).
