"""Session-related commands for winterm2."""

from typing import Optional
import click

from ..core.terminal import WindowsTerminalCLI, get_cli


@click.group()
def session():
    """
    Session control commands.

    Commands:
        send        - Send a command
        run         - Run a command
        clear       - Clear the pane
        list        - List sessions
        restart     - Restart session
        focus       - Focus a session/pane
        read        - Read screen contents
        capture     - Capture screen to file
        set-name    - Set session name
        get-var     - Get session variable
        set-var     - Set session variable
    """
    pass


@session.command("send")
@click.argument("command", type=str, required=True, nargs=-1)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_send(ctx: click.Context, command: tuple, pane_id: Optional[str]) -> None:
    """Send a command to the pane (no newline)."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        cmd_str = " ".join(command)
        result = cli.send_text(cmd_str, pane_id=pane_id)
        if result.get("success"):
            click.echo("Command sent")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("run")
@click.argument("command", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_run(ctx: click.Context, command: str, pane_id: Optional[str]) -> None:
    """Run a command in the pane (with newline)."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.send_text(command + "\r", pane_id=pane_id)
        if result.get("success"):
            click.echo("Command executed")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("clear")
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_clear(ctx: click.Context, pane_id: Optional[str]) -> None:
    """Clear the pane."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.clear_screen(pane_id=pane_id)
        if result.get("success"):
            click.echo("Cleared")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("list")
@click.option("--json", "output_json", is_flag=True, default=False)
@click.pass_context
def cmd_list(ctx: click.Context, output_json: bool) -> None:
    """List all sessions/panes."""
    click.echo("Sessions:")
    click.echo("  Note: Enable Experimental JSON API for detailed session list")


@session.command("restart")
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_restart(ctx: click.Context, pane_id: Optional[str]) -> None:
    """Restart the session."""
    click.echo("Note: Restart session requires Experimental JSON API")


@session.command("focus")
@click.argument("pane_id", type=str, required=True)
@click.pass_context
def cmd_focus(ctx: click.Context, pane_id: str) -> None:
    """Focus a specific pane."""
    click.echo("Note: Focus pane requires Experimental JSON API")


@session.command("read")
@click.option("--pane-id", type=str, default=None)
@click.option("--lines", "-n", type=int, default=None, help="Number of lines to read")
@click.pass_context
def cmd_read(ctx: click.Context, pane_id: Optional[str], lines: Optional[int]) -> None:
    """Read screen contents."""
    click.echo("Note: Read screen requires Experimental JSON API")


@session.command("capture")
@click.option("--pane-id", type=str, default=None)
@click.option("--output", "-o", type=str, required=True, help="Output file path")
@click.option("--history", is_flag=True, default=False, help="Include scrollback history")
@click.pass_context
def cmd_capture(ctx: click.Context, pane_id: Optional[str], output: str, history: bool) -> None:
    """Capture screen to file."""
    click.echo("Note: Capture screen requires Experimental JSON API")


@session.command("set-name")
@click.argument("name", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_set_name(ctx: click.Context, name: str, pane_id: Optional[str]) -> None:
    """Set session name."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.set_pane_title(name, pane_id=pane_id)
        if result.get("success"):
            click.echo(f"Session name set to: {name}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("get-var")
@click.argument("variable", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_get_var(ctx: click.Context, variable: str, pane_id: Optional[str]) -> None:
    """Get session variable value."""
    click.echo("Note: Get session variable requires Experimental JSON API")


@session.command("set-var")
@click.argument("variable", type=str, required=True)
@click.argument("value", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_set_var(ctx: click.Context, variable: str, value: str, pane_id: Optional[str]) -> None:
    """Set session variable value."""
    click.echo("Note: Set session variable requires Experimental JSON API")
