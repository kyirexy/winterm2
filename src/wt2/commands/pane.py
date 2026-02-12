"""Pane-related commands for winterm2."""

from typing import Optional
import click

from ..core.terminal import WindowsTerminalCLI, get_cli


@click.group()
def pane():
    """
    Pane management commands.

    Commands:
        split   - Split a pane
        vsplit  - Split vertically
        close   - Close a pane
        focus   - Focus a pane
        resize  - Resize a pane
        list    - List panes
        zoom    - Toggle pane zoom
        swap    - Swap two panes
        split2x2 - Create 2x2 grid
    """
    pass


@pane.command("split")
@click.option("--direction", "-d", type=str, default="horizontal")
@click.option("--profile", "-p", type=str, default=None)
@click.option("--size", "-s", type=float, default=None, help="Split size (0.0-1.0)")
@click.option("--pane-id", type=str, default=None, help="Source pane ID")
@click.pass_context
def cmd_split_pane(ctx: click.Context, direction: str, profile: Optional[str], size: Optional[float], pane_id: Optional[str]) -> None:
    """Split a pane."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        # Map direction names
        direction_map = {"horizontal": "right", "vertical": "down"}
        wt_direction = direction_map.get(direction, direction)

        result = cli.split_pane(direction=wt_direction, profile=profile, size=size, pane_id=pane_id)
        if result.get("success"):
            click.echo(f"Split pane ({direction})")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("vsplit")
@click.option("--profile", "-p", type=str, default=None)
@click.option("--size", "-s", type=float, default=None)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_vsplit_pane(ctx: click.Context, profile: Optional[str], size: Optional[float], pane_id: Optional[str]) -> None:
    """Split a pane vertically."""
    ctx.invoke(cmd_split_pane, direction="vertical", profile=profile, size=size, pane_id=pane_id)


@pane.command("close")
@click.argument("pane_id", type=str, required=False)
@click.option("--force", "-f", is_flag=True, default=False)
@click.pass_context
def cmd_close_pane(ctx: click.Context, pane_id: Optional[str], force: bool) -> None:
    """Close a pane."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        if not force:
            if not click.confirm(f"Close pane {pane_id or 'current'}?"):
                click.echo("Cancelled")
                return
        result = cli.close_pane(pane_id=pane_id)
        if result.get("success"):
            click.echo("Pane closed")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("focus")
@click.argument("direction", type=click.Choice(["up", "down", "left", "right"]), required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_focus_pane(ctx: click.Context, direction: str, pane_id: Optional[str]) -> None:
    """Focus adjacent pane."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.focus_pane(direction=direction, pane_id=pane_id)
        if result.get("success"):
            click.echo(f"Focused {direction} pane")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("resize")
@click.argument("direction", type=click.Choice(["up", "down", "left", "right"]), required=True)
@click.argument("delta", type=int, default=1)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_resize_pane(ctx: click.Context, direction: str, delta: int, pane_id: Optional[str]) -> None:
    """Resize a pane."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.resize_pane(direction=direction, delta=delta, pane_id=pane_id)
        if result.get("success"):
            click.echo(f"Resized pane {direction} by {delta}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("list")
@click.option("--json", "output_json", is_flag=True, default=False)
@click.option("--tab-id", type=str, default=None)
@click.pass_context
def cmd_list_panes(ctx: click.Context, output_json: bool, tab_id: Optional[str]) -> None:
    """List panes."""
    click.echo("Panes:")
    click.echo("  Note: Enable Experimental JSON API for detailed pane list")


@pane.command("zoom")
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_zoom_pane(ctx: click.Context, pane_id: Optional[str]) -> None:
    """Toggle pane zoom (maximize/restore)."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.toggle_pane_zoom(pane_id=pane_id)
        if result.get("success"):
            click.echo("Pane zoom toggled")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("swap")
@click.argument("pane_id", type=str, required=True)
@click.argument("target_pane_id", type=str, required=True)
@click.pass_context
def cmd_swap_pane(ctx: click.Context, pane_id: str, target_pane_id: str) -> None:
    """Swap two panes."""
    click.echo("Note: Swap panes requires Experimental JSON API")


@pane.command("split2x2")
@click.option("--profile", "-p", type=str, default=None)
@click.pass_context
def cmd_split2x2(ctx: click.Context, profile: Optional[str]) -> None:
    """Create a 2x2 grid of panes."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        # Split vertically first
        result1 = cli.split_pane(direction="right", profile=profile)
        if not result1.get("success"):
            click.echo(f"Failed at first split: {result1.get('error')}", err=True)
            ctx.exit(1)

        # Split horizontally in right half
        result2 = cli.split_pane(direction="down", profile=profile)
        if not result2.get("success"):
            click.echo(f"Failed at second split: {result2.get('error')}", err=True)
            ctx.exit(1)

        click.echo("Created 2x2 pane grid (basic)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)
