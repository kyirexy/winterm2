"""Tab-related commands for winterm2."""

from typing import Optional
import click

from ..core.terminal import WindowsTerminalCLI, get_cli


@click.group()
def tab():
    """
    Tab management commands.

    Commands:
        new     - Create a new tab
        close   - Close a tab
        focus   - Focus a tab
        select  - Select tab by ID or index
        list    - List all tabs
        next    - Switch to next tab
        prev    - Switch to previous tab
        goto    - Go to tab by index
        rename  - Rename a tab
        move    - Move tab to new window
    """
    pass


@tab.command("new")
@click.option("--profile", "-p", type=str, default=None, help="Profile to use")
@click.option("--title", "-t", type=str, default=None, help="Tab title")
@click.option("--window-id", "-w", type=str, default=None, help="Window ID")
@click.option("--command", "-c", type=str, default=None, help="Command to run in new tab")
@click.pass_context
def cmd_new_tab(
    ctx: click.Context,
    profile: Optional[str],
    title: Optional[str],
    window_id: Optional[str],
    command: Optional[str],
) -> None:
    """Create a new tab."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.new_tab(profile=profile, command=command, cwd=None, window_id=window_id, title=title)
        if result.get("success"):
            click.echo("New tab created")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("close")
@click.argument("tab_id", type=str, required=False)
@click.option("--force", "-f", is_flag=True, default=False)
@click.pass_context
def cmd_close_tab(ctx: click.Context, tab_id: Optional[str], force: bool) -> None:
    """Close a tab."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        if not force:
            if not click.confirm(f"Close tab {tab_id or 'current'}?"):
                click.echo("Cancelled")
                return
        result = cli.close_tab(tab_id=tab_id)
        if result.get("success"):
            click.echo("Tab closed")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("focus")
@click.argument("tab_id", type=str, required=True)
@click.pass_context
def cmd_focus_tab(ctx: click.Context, tab_id: str) -> None:
    """Focus a tab by ID."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.focus_tab(tab_id)
        if result.get("success"):
            click.echo(f"Focused tab: {tab_id}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("select")
@click.argument("tab_id_or_index", type=str, required=True)
@click.option("--window-id", "-w", type=str, default=None)
@click.pass_context
def cmd_select_tab(ctx: click.Context, tab_id_or_index: str, window_id: Optional[str]) -> None:
    """Select tab by ID or index."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        # Try to parse as index
        try:
            index = int(tab_id_or_index)
            click.echo(f"Switching to tab at index {index} (not fully implemented)")
        except ValueError:
            # ID-based selection
            result = cli.focus_tab(tab_id_or_index)
            if result.get("success"):
                click.echo(f"Selected tab: {tab_id_or_index}")
            else:
                click.echo(f"Failed: {result.get('error')}", err=True)
                ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("list")
@click.option("--json", "output_json", is_flag=True, default=False)
@click.option("--window-id", "-w", type=str, default=None)
@click.pass_context
def cmd_list_tabs(ctx: click.Context, output_json: bool, window_id: Optional[str]) -> None:
    """List all tabs."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.list_tabs()
        if result.get("success"):
            click.echo("Tabs:")
            click.echo("  Note: Enable Experimental JSON API for detailed tab list")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("next")
@click.pass_context
def cmd_next_tab(ctx: click.Context) -> None:
    """Switch to next tab."""
    click.echo("Note: Next/Prev tab switching requires Experimental JSON API")


@tab.command("prev")
@click.pass_context
def cmd_prev_tab(ctx: click.Context) -> None:
    """Switch to previous tab."""
    click.echo("Note: Next/Prev tab switching requires Experimental JSON API")


@tab.command("goto")
@click.argument("index", type=int, required=True)
@click.option("--window-id", "-w", type=str, default=None)
@click.pass_context
def cmd_goto_tab(ctx: click.Context, index: int, window_id: Optional[str]) -> None:
    """Go to tab by index (0-based)."""
    click.echo(f"Note: Goto tab by index requires Experimental JSON API")


@tab.command("rename")
@click.argument("tab_id", type=str, required=False)
@click.argument("title", type=str, required=True)
@click.pass_context
def cmd_rename_tab(ctx: click.Context, tab_id: Optional[str], title: str) -> None:
    """Rename a tab."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.rename_tab(tab_id=tab_id, title=title)
        if result.get("success"):
            click.echo(f"Renamed tab to: {title}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("move")
@click.argument("tab_id", type=str, required=False)
@click.pass_context
def cmd_move_tab(ctx: click.Context, tab_id: Optional[str]) -> None:
    """Move tab to its own new window."""
    click.echo("Note: Move tab to new window requires Experimental JSON API")
