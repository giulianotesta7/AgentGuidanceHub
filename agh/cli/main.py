"""Typer CLI entrypoint for Agent Guidance Hub."""

from __future__ import annotations

from typing import Annotated

import typer

from agh.cli.config import (
    AghConfig,
    ConfigError,
    LoginValidationError,
    get_config_path,
    load_config,
    mask_token,
    normalize_instance_url,
    save_config,
    validate_login,
)

APP_HELP = """Agent Guidance Hub — manage and distribute agent guidance packs.

Usage:
  agh [OPTIONS] COMMAND [ARGS]...

Commands:
  login        Validate API credentials with /api/v1/me and save local config.
  config show  Show the saved instance URL, email, and masked token.

Global options:
  --help       Show this help page.

Arguments:
  Run `agh <command> --help` for command-specific options and arguments.
"""

app = typer.Typer(
    name="agh",
    help="Agent Guidance Hub — manage and distribute agent guidance packs.",
    no_args_is_help=False,
)
config_app = typer.Typer(help="Inspect local AGH CLI configuration.")
app.add_typer(config_app, name="config")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Agent Guidance Hub CLI."""
    if ctx.invoked_subcommand is None:
        typer.echo(APP_HELP)
        raise typer.Exit(0)


@app.command(help="Validate API credentials and save local AGH config.")
def login(
    url: Annotated[
        str,
        typer.Option(
            "--url",
            prompt="AGH instance URL",
            help="AGH server base URL, e.g. http://localhost:8912.",
        ),
    ],
    email: Annotated[
        str,
        typer.Option(
            "--email",
            prompt="Email",
            help="Email expected from GET /api/v1/me.",
        ),
    ],
    token: Annotated[
        str,
        typer.Option(
            "--token",
            prompt="API token",
            hide_input=True,
            help="AGH API token. The token is validated but never printed.",
        ),
    ],
) -> None:
    """Validate credentials against /api/v1/me, then write config.toml."""
    try:
        instance_url = normalize_instance_url(url)
        validate_login(instance_url=instance_url, email=email, token=token)
        save_config(AghConfig(instance_url=instance_url, email=email, token=token))
    except (ConfigError, LoginValidationError) as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=False)
        raise typer.Exit(1) from exc

    typer.echo(
        f"Logged in to {instance_url} as {email}. Config saved to {get_config_path()}."
    )


@config_app.command("show", help="Show local AGH config with the token masked.")
def config_show() -> None:
    """Show local config without revealing the plaintext token."""
    try:
        config = load_config()
    except ConfigError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=False)
        raise typer.Exit(1) from exc

    typer.echo(f"instance_url = {config.instance_url}")
    typer.echo(f"email = {config.email}")
    typer.echo(f"token = {mask_token(config.token)}")


if __name__ == "__main__":
    app()
