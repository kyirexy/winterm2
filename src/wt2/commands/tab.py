"""Tab-related commands."""

from typing import Optional, List
import click

from ..core.terminal import WindowsTerminalAPI, get_api


@click.group()
def tab():
    """
    Tab management commands.

    Commands:
        new     - Create a new tab
        close   - Close a tab
        focus   - Focus a tab
        list    - List all tabs
        next    - Switch to next tab
        prev    - Switch to previous tab
    """
    pass


@tab.command("new")
@click.option("--profile", "-p", type=str, default=None)
@click.option("--title", "-t", type=str, default=None)
@click.option("--window-id", "-w", type=str, default=None)
@click.pass_context
def cmd_new_tab(
    ctx: click.Context,
    profile: Optional[str],
    title: Optional[str],
    window_id: Optional[str],
) -> None:
    """Create a new tab."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        params = {"profile": profile or ctx.obj.get("profile")}
        if title:
            params["title"] = title
        if window_id:
            params["windowId"] = window_id
        result = api.new_tab(**params)
        if result.get("success"):
            click.echo(f"Created new tab")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("close")
@click.argument("tab_id", type=str, required=False)
@click.pass_context
def cmd_close_tab(ctx: click.Context, tab_id: Optional[str]) -> None:
    """Close a tab."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        if tab_id:
            result = api.close_tab(tab_id=int(tab_id))
        else:
            state = api.get_state()
            tabs = state.get("tabs", [])
            if tabs:
                for t in tabs:
                    if t.get("isFocused", False):
                        result = api.close_tab(tab_id=t.get("id"))
                        break
            else:
                click.echo("No tab specified", err=True)
                ctx.exit(3)
                return
        if result.get("success"):
            click.echo(f"Closed tab")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("list")
@click.pass_context
def cmd_list_tabs(ctx: click.Context) -> None:
    """List all tabs."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        tabs = state.get("tabs", [])
        for t in tabs:
            t_id = t.get("id", "unknown")
            title = t.get("title", "Untitled")
            marker = " *" if t.get("isFocused", False) else ""
            click.echo(f"[{t_id}] {title}{marker}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


def new_tab(
    window_id: Optional[int] = None,
    profile: Optional[str] = None,
    title: Optional[str] = None,
    command: Optional[str] = None,
) -> dict:
    """Create a new tab in Windows Terminal.

    Args:
        window_id: The ID of the window to create the tab in.
        profile: The profile to use for the new tab.
        title: The title of the new tab.
        command: Initial command to run in the tab.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        action = {
            "action": "newTab",
        }

        if window_id:
            action["windowId"] = window_id
        if profile:
            action["profile"] = profile
        if title:
            action["title"] = title
        if command:
            action["command"] = command

        result = conn.send_message(action)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def close_tab(tab_id: int) -> dict:
    """Close a tab.

    Args:
        tab_id: The ID of the tab to close.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "closeTab",
            "tabId": tab_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def focus_tab(tab_id: int) -> dict:
    """Focus a tab.

    Args:
        tab_id: The ID of the tab to focus.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "focusTab",
            "tabId": tab_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def rename_tab(tab_id: int, title: str) -> dict:
    """Rename a tab.

    Args:
        tab_id: The ID of the tab to rename.
        title: The new title for the tab.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "renameTab",
            "tabId": tab_id,
            "title": title,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_tabs(window_id: int) -> dict:
    """Get list of tabs in a window.

    Args:
        window_id: The ID of the window.

    Returns:
        dict: List of tabs.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "getTabs",
            "windowId": window_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
