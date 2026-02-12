"""
winterm2 CLI entry point.

Main Click command group and entry point for the CLI.

A native Windows CLI tool for automating Windows Terminal,
PowerShell 7+, CMD, and WSL2 shells. Designed as a full
Windows-native alternative to macOS's `it2` (iTerm2 control tool).
"""

from __future__ import annotations
import sys
import click

from .commands import window, tab, pane, session, broadcast, monitor, config
from .utils import get_shell_type


@click.group(invoke_without_command=True)
@click.version_option(
    version="0.2.0",
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
        window    - Window management (new, close, focus, list, move, resize)
        tab       - Tab management (new, close, focus, select, list, rename)
        pane      - Pane management (split, vsplit, close, focus, resize, zoom)
        session   - Session control (send, run, clear, list, restart)
        broadcast - Broadcast commands to multiple panes
        monitor   - Follow and filter pane output
        config    - Configuration management

   \b
    Examples:
        wt2 tab new --profile PowerShell
        wt2 pane split --direction vertical
        wt2 session send --command "Get-Process"
        wt2 broadcast send --all "git pull"
        wt2 window arrange save dev
        wt2 config load myprofile

    For detailed help on any command, use: wt2 <command> --help

   \b
    Shortcuts:
        wt2 send "cmd"       -> wt2 session send "cmd"
        wt2 run "cmd"        -> wt2 session run "cmd"
        wt2 split            -> wt2 pane split
        wt2 vsplit           -> wt2 pane vsplit
        wt2 clear            -> wt2 session clear
        wt2 ls               -> wt2 session list
        wt2 new              -> wt2 window new
        wt2 newtab           -> wt2 tab new
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
        click.echo(f"winterm2 v0.2.0")
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


# ============================================================================
# Shortcut Commands (aliased to full commands for convenience)
# ============================================================================

@cli.command("send")
@click.argument("text", type=str, required=True, nargs=-1)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_send_shortcut(ctx: click.Context, text: tuple, pane_id: str | None) -> None:
    """Shortcut: Send text to pane (same as 'wt2 session send')."""
    from .commands.session import cmd_send
    ctx.invoke(cmd_send, command=text, pane_id=pane_id)


@cli.command("run")
@click.argument("command", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_run_shortcut(ctx: click.Context, command: str, pane_id: str | None) -> None:
    """Shortcut: Run command in pane (same as 'wt2 session run')."""
    from .commands.session import cmd_run
    ctx.invoke(cmd_run, command=command, pane_id=pane_id)


@cli.command("split")
@click.option("--direction", "-d", type=str, default="horizontal")
@click.option("--profile", "-p", type=str, default=None)
@click.pass_context
def cmd_split_shortcut(ctx: click.Context, direction: str, profile: str | None) -> None:
    """Shortcut: Split pane (same as 'wt2 pane split')."""
    from .commands.pane import cmd_split_pane
    ctx.invoke(cmd_split_pane, direction=direction, profile=profile, size=None, pane_id=None)


@cli.command("vsplit")
@click.option("--profile", "-p", type=str, default=None)
@click.pass_context
def cmd_vsplit_shortcut(ctx: click.Context, profile: str | None) -> None:
    """Shortcut: Split pane vertically (same as 'wt2 pane vsplit')."""
    from .commands.pane import cmd_split_pane
    ctx.invoke(cmd_split_pane, direction="vertical", profile=profile, size=None, pane_id=None)


@cli.command("clear")
@click.pass_context
def cmd_clear_shortcut(ctx: click.Context) -> None:
    """Shortcut: Clear pane (same as 'wt2 session clear')."""
    from .commands.session import cmd_clear
    ctx.invoke(cmd_clear, pane_id=None)


@cli.command("ls")
@click.option("--json", "output_json", is_flag=True, default=False)
@click.pass_context
def cmd_ls_shortcut(ctx: click.Context, output_json: bool) -> None:
    """Shortcut: List sessions (same as 'wt2 session list')."""
    from .commands.session import cmd_list
    ctx.invoke(cmd_list, output_json=output_json)


@cli.command("new")
@click.option("--profile", "-p", type=str, default=None)
@click.option("--size", "-s", type=str, default=None)
@click.option("--startup-dir", "-d", type=str, default=None)
@click.pass_context
def cmd_new_shortcut(ctx: click.Context, profile: str | None, size: str | None, startup_dir: str | None) -> None:
    """Shortcut: Create new window (same as 'wt2 window new')."""
    from .commands.window import cmd_new_window
    ctx.invoke(cmd_new_window, profile=profile, size=size, startup_dir=startup_dir)


@cli.command("newtab")
@click.option("--profile", "-p", type=str, default=None)
@click.option("--title", "-t", type=str, default=None)
@click.option("--window-id", "-w", type=str, default=None)
@click.option("--command", "-c", type=str, default=None)
@click.pass_context
def cmd_newtab_shortcut(ctx: click.Context, profile: str | None, title: str | None, window_id: str | None, command: str | None) -> None:
    """Shortcut: Create new tab (same as 'wt2 tab new')."""
    from .commands.tab import cmd_new_tab
    ctx.invoke(cmd_new_tab, profile=profile, title=title, window_id=window_id, command=command)


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
