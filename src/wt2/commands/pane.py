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
    """
    pass


@pane.command("split")
@click.option("--direction", "-d", type=str, default="horizontal")
@click.option("--profile", "-p", type=str, default=None)
@click.pass_context
def cmd_split_pane(ctx: click.Context, direction: str, profile: Optional[str]) -> None:
    """Split a pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.new_pane(profile=profile, direction=direction)
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
@click.pass_context
def cmd_vsplit_pane(ctx: click.Context, profile: Optional[str]) -> None:
    """Split a pane vertically."""
    ctx.invoke(cmd_split_pane, direction="vertical", profile=profile)


@pane.command("close")
@click.argument("pane_id", type=str, required=False)
@click.pass_context
def cmd_close_pane(ctx: click.Context, pane_id: Optional[str]) -> None:
    """Close a pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("closePane", paneId=pane_id)
        if result.get("success"):
            click.echo(f"Closed pane")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@pane.command("list")
@click.pass_context
def cmd_list_panes(ctx: click.Context) -> None:
    """List panes."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        panes = state.get("panes", [])
        for p in panes:
            p_id = p.get("id", "unknown")
            shell = p.get("shellType", "unknown")
            marker = " *" if p.get("isFocused", False) else ""
            click.echo(f"[{p_id}] {shell}{marker}")
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
