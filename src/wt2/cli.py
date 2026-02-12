"""
winterm2 CLI entry point.

Main Click command group and entry point for the CLI.
"""

from __future__ import annotations
import sys
import click

from .commands import window, tab, pane, session, broadcast, monitor, config
from .utils import get_shell_type


@click.group(invoke_without_command=True)
@click.version_option(
    version="0.1.0",
    prog_name="winterm2",
    message="winterm2 version %(version)s",
)
@click.option(
    "--shell",
    type=click.Choice(["powershell", "pwsh", "cmd", "wsl", "auto"]),
    default="auto",
    help="Shell type to use (default: auto-detect)",
)
@click.option(
    "--profile",
    type=str,
    default=None,
    help="Terminal profile to use",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def cli(
    ctx: click.Context,
    shell: str,
    profile: str | None,
    verbose: bool,
) -> None:
    """
    winterm2 - Windows Terminal CLI tool (it2 for Windows).

    A native Windows CLI tool for automating Windows Terminal,
    PowerShell 7+, CMD, and WSL2 shells.

   \b
    Core Commands:
        window    - Window management (new, close, focus, list)
        tab       - Tab management (new, close, focus, list)
        pane      - Pane management (split, resize, focus, list)
        session   - Session control (send, run, clear, list)
        broadcast - Broadcast commands to multiple panes
        monitor   - Follow and filter pane output
        config    - Configuration management

    \b
    Examples:
        wt2 tab new --profile PowerShell
        wt2 pane split --direction vertical
        wt2 session send --command "Get-Process"
        wt2 broadcast --panes 1,2,3 --command "git pull"

    For detailed help on any command, use: wt2 <command> --help
    """
    # Store context for subcommands
    ctx.ensure_object(dict)

    # Auto-detect shell if needed
    if shell == "auto":
        detected = get_shell_type()
        shell = detected if detected else "powershell"

    ctx.obj["shell"] = shell
    ctx.obj["profile"] = profile
    ctx.obj["verbose"] = verbose

    # Print banner in verbose mode
    if verbose:
        click.echo(f"winterm2 v0.1.0")
        click.echo(f"Shell: {shell}")
        click.echo(f"Profile: {profile or 'default'}")
        click.echo()

    # If no command is given, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register subcommand groups
cli.add_command(window, "window")
cli.add_command(tab, "tab")
cli.add_command(pane, "pane")
cli.add_command(session, "session")
cli.add_command(broadcast, "broadcast")
cli.add_command(monitor, "monitor")
cli.add_command(config, "config")


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code.
    """
    try:
        cli()
        return 0
    except click.ClickException as e:
        e.show()
        return 1
    except Exception as e:
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            traceback.print_exc()
        else:
            click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
