"""Click CLI for {{ cookiecutter.scraper_slug }}.

Stub. Replace `scrape` with the real entrypoint. Keep `status` and
the click.group so it stays drop-in-compatible with the portfolio
CLI shape (`<scraper> migrate`, `<scraper> run`, `<scraper> status`).
"""
from __future__ import annotations

import click


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """{{ cookiecutter.scraper_slug }} command-line interface."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
def status() -> None:
    """Print scraper status (stub)."""
    click.echo("{{ cookiecutter.scraper_slug }}: stub -- replace with real status output")


@cli.command()
def run() -> None:
    """Run the primary scrape (stub)."""
    click.echo("{{ cookiecutter.scraper_slug }}: stub -- replace with the body of pipeline_flow.{{ cookiecutter.primary_flow_name }}")


if __name__ == "__main__":
    cli()
