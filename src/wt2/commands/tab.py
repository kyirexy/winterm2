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
@click.option("--profile", "-p", type=str, default=None)
@click.option("--title", "-t", type=str, default=None)
@click.option("--window-id", "-w", type=str, default=None)
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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        params = {"profile": profile or ctx.obj.get("profile")}
        if title:
            params["title"] = title
        if window_id:
            params["windowId"] = window_id
        if command:
            params["command"] = command
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
@click.option("--force", "-f", is_flag=True, default=False)
@click.pass_context
def cmd_close_tab(ctx: click.Context, tab_id: Optional[str], force: bool) -> None:
    """Close a tab."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        if not tab_id:
            state = api.get_state()
            tabs = state.get("tabs", [])
            if tabs:
                for t in tabs:
                    if t.get("isFocused", False):
                        tab_id = str(t.get("id"))
                        break
        if not tab_id:
            click.echo("No tab specified", err=True)
            ctx.exit(3)
            return
        if not force:
            if not click.confirm(f"Close tab {tab_id}?"):
                click.echo("Cancelled")
                return
        result = api.close_tab(tab_id=int(tab_id))
        if result.get("success"):
            click.echo(f"Closed tab {tab_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("focus")
@click.argument("tab_id", type=str, required=True)
@click.pass_context
def cmd_focus_tab(ctx: click.Context, tab_id: str) -> None:
    """Focus a tab by ID."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("focusTab", tabId=tab_id)
        if result.get("success"):
            click.echo(f"Focused tab {tab_id}")
        else:
            click.echo(f"Failed", err=True)
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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        # Try to parse as index
        try:
            index = int(tab_id_or_index)
            result = api.send_command("selectTabByIndex", index=index, windowId=window_id)
            if result.get("success"):
                click.echo(f"Selected tab at index {index}")
            else:
                click.echo(f"Failed", err=True)
                ctx.exit(1)
        except ValueError:
            # ID-based selection
            result = api.send_command("focusTab", tabId=tab_id_or_index)
            if result.get("success"):
                click.echo(f"Selected tab {tab_id_or_index}")
            else:
                click.echo(f"Failed", err=True)
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
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        tabs = state.get("tabs", [])

        if output_json:
            import json
            click.echo(json.dumps({"tabs": tabs}, indent=2))
        else:
            click.echo("Tabs:")
            click.echo("-" * 60)
            for idx, t in enumerate(tabs):
                t_id = t.get("id", "unknown")
                title = t.get("title", "Untitled")
                marker = " *" if t.get("isFocused", False) else ""
                click.echo(f"[{t_id}] {title}{marker}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("next")
@click.pass_context
def cmd_next_tab(ctx: click.Context) -> None:
    """Switch to next tab."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("nextTab")
        if result.get("success"):
            click.echo("Switched to next tab")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("prev")
@click.pass_context
def cmd_prev_tab(ctx: click.Context) -> None:
    """Switch to previous tab."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("prevTab")
        if result.get("success"):
            click.echo("Switched to previous tab")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("goto")
@click.argument("index", type=int, required=True)
@click.option("--window-id", "-w", type=str, default=None)
@click.pass_context
def cmd_goto_tab(ctx: click.Context, index: int, window_id: Optional[str]) -> None:
    """Go to tab by index (0-based)."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("selectTabByIndex", index=index, windowId=window_id)
        if result.get("success"):
            click.echo(f"Switched to tab {index}")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("rename")
@click.argument("tab_id", type=str, required=False)
@click.argument("title", type=str, required=True)
@click.pass_context
def cmd_rename_tab(ctx: click.Context, tab_id: Optional[str], title: str) -> None:
    """Rename a tab."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        if not tab_id:
            state = api.get_state()
            tabs = state.get("tabs", [])
            for t in tabs:
                if t.get("isFocused", False):
                    tab_id = str(t.get("id"))
                    break
        result = api.send_command("renameTab", tabId=tab_id, title=title)
        if result.get("success"):
            click.echo(f"Renamed tab to: {title}")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@tab.command("move")
@click.argument("tab_id", type=str, required=False)
@click.pass_context
def cmd_move_tab(ctx: click.Context, tab_id: Optional[str]) -> None:
    """Move tab to its own new window."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        if not tab_id:
            state = api.get_state()
            tabs = state.get("tabs", [])
            for t in tabs:
                if t.get("isFocused", False):
                    tab_id = str(t.get("id"))
                    break
        result = api.send_command("moveTabToNewWindow", tabId=tab_id)
        if result.get("success"):
            click.echo("Moved tab to new window")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
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
