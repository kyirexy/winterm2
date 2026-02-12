"""Pane-related commands."""

from typing import Optional, Literal
import click

from ..core.terminal import WindowsTerminalAPI, get_api


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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.new_pane(profile=profile, direction=direction, size=size, paneId=pane_id)
        if result.get("success"):
            click.echo(f"Split pane ({direction})")
        else:
            click.echo(f"Failed", err=True)
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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        if not force:
            if not click.confirm(f"Close pane {pane_id}?"):
                click.echo("Cancelled")
                return
        result = api.send_command("closePane", paneId=pane_id)
        if result.get("success"):
            click.echo(f"Closed pane {pane_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("focus")
@click.argument("direction", type=click.Choice(["up", "down", "left", "right"]), required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_focus_pane(ctx: click.Context, direction: str, pane_id: Optional[str]) -> None:
    """Focus adjacent pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("moveFocus", direction=direction, paneId=pane_id)
        if result.get("success"):
            click.echo(f"Focused {direction} pane")
        else:
            click.echo("Failed", err=True)
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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.resize_pane(pane_id=pane_id, direction=direction, delta=delta)
        if result.get("success"):
            click.echo(f"Resized pane {direction} by {delta}")
        else:
            click.echo("Failed", err=True)
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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        panes = state.get("panes", [])

        if tab_id:
            panes = [p for p in panes if str(p.get("tabId")) == tab_id]

        if output_json:
            import json
            click.echo(json.dumps({"panes": panes}, indent=2))
        else:
            click.echo("Panes:")
            click.echo("-" * 60)
            for p in panes:
                p_id = p.get("id", "unknown")
                shell = p.get("shellType", "unknown")
                marker = " *" if p.get("isFocused", False) else ""
                click.echo(f"[{p_id}] {shell}{marker}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("zoom")
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_zoom_pane(ctx: click.Context, pane_id: Optional[str]) -> None:
    """Toggle pane zoom (maximize/restore)."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("togglePaneZoom", paneId=pane_id)
        if result.get("success"):
            is_zoomed = result.get("isZoomed", False)
            click.echo(f"Pane {'zoomed' if is_zoomed else 'restored'}")
        else:
            click.echo("Failed", err=True)
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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("swapPane", paneId=pane_id, targetPaneId=target_pane_id)
        if result.get("success"):
            click.echo(f"Swapped panes {pane_id} and {target_pane_id}")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("split2x2")
@click.option("--profile", "-p", type=str, default=None)
@click.pass_context
def cmd_split2x2(ctx: click.Context, profile: Optional[str]) -> None:
    """Create a 2x2 grid of panes."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        # Split vertically first
        result1 = api.new_pane(profile=profile, direction="vertical")
        if not result1.get("success"):
            click.echo("Failed at first split", err=True)
            ctx.exit(1)

        # Split horizontally in each half
        result2 = api.new_pane(profile=profile, direction="horizontal")
        if not result2.get("success"):
            click.echo("Failed at second split", err=True)
            ctx.exit(1)

        # Focus back to first pane and split horizontally
        api.send_command("focusPane", paneId=result1.get("paneId"))
        result3 = api.new_pane(profile=profile, direction="horizontal")
        if not result3.get("success"):
            click.echo("Failed at third split", err=True)
            ctx.exit(1)

        click.echo("Created 2x2 pane grid")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


def split_pane(
    tab_id: Optional[int] = None,
    direction: Literal["horizontal", "vertical", "left", "right", "up", "down"] = "vertical",
    profile: Optional[str] = None,
    size: Optional[float] = None,
) -> dict:
    """Split a pane in Windows Terminal.

    Args:
        tab_id: The ID of the tab to split.
        direction: The direction to split.
        profile: The profile to use for the new pane.
        size: The size of the split (0.0 to 1.0).

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        action = {
            "action": "splitPane",
            "direction": direction,
        }

        if tab_id:
            action["tabId"] = tab_id
        if profile:
            action["profile"] = profile
        if size is not None:
            action["size"] = size

        result = conn.send_message(action)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def close_pane(pane_id: int) -> dict:
    """Close a pane.

    Args:
        pane_id: The ID of the pane to close.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "closePane",
            "paneId": pane_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def focus_pane(pane_id: int) -> dict:
    """Focus a pane.

    Args:
        pane_id: The ID of the pane to focus.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "focusPane",
            "paneId": pane_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def swap_pane(pane_id: int, target_pane_id: int) -> dict:
    """Swap two panes.

    Args:
        pane_id: The ID of the first pane.
        target_pane_id: The ID of the second pane.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "swapPane",
            "paneId": pane_id,
            "targetPaneId": target_pane_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def resize_pane(pane_id: int, deltaX: int, deltaY: int) -> dict:
    """Resize a pane.

    Args:
        pane_id: The ID of the pane to resize.
        deltaX: Horizontal resize amount.
        deltaY: Vertical resize amount.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "resizePane",
            "paneId": pane_id,
            "deltaX": deltaX,
            "deltaY": deltaY,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_panes(tab_id: int) -> dict:
    """Get list of panes in a tab.

    Args:
        tab_id: The ID of the tab.

    Returns:
        dict: List of panes.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "getPanes",
            "tabId": tab_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
