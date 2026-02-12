"""
Broadcast commands for winterm2.

Provides commands for sending commands to multiple panes simultaneously.
"""

from __future__ import annotations
import click
from typing import Optional, List

from ..core.terminal import WindowsTerminalAPI, get_api


@click.group()
def broadcast():
    """
    Broadcast commands to multiple panes.

    Commands:
        on      - Enable broadcast mode
        off     - Disable broadcast mode
        send    - Send a command to broadcast targets
    """
    pass


@ broadcast.command("on")
@click.option(
    "--panes",
    "-p",
    type=str,
    default=None,
    help="Comma-separated pane IDs to broadcast to",
)
@click.option(
    "--tabs",
    "-t",
    type=str,
    default=None,
    help="Comma-separated tab IDs to broadcast to",
)
@click.option(
    "--all",
    "all_panes",
    is_flag=True,
    default=False,
    help="Broadcast to all panes",
)
@click.pass_context
def broadcast_on(
    ctx: click.Context,
    panes: Optional[str],
    tabs: Optional[str],
    all_panes: bool,
) -> None:
    """
    Enable broadcast mode for specified targets.

    Examples:
        wt2 broadcast on --all
        wt2 broadcast on --panes 1,2,3
        wt2 broadcast on --tabs 1,2
    """
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())

    try:
        target_panes: List[str] = []
        if all_panes:
            state = api.get_state()
            for tab in state.get("tabs", []):
                for pane in tab.get("panes", []):
                    target_panes.append(pane.get("id"))
        elif panes:
            target_panes = panes.split(",")
        elif tabs:
            state = api.get_state()
            for tab in state.get("tabs", []):
                if str(tab.get("id")) in tabs.split(","):
                    for pane in tab.get("panes", []):
                        target_panes.append(pane.get("id"))

        if not target_panes:
            click.echo("No broadcast targets specified", err=True)
            ctx.exit(3)
            return

        # Store broadcast state
        ctx.obj["broadcast_targets"] = target_panes
        ctx.obj["broadcast_active"] = True

        click.echo(f"Broadcast enabled for panes: {', '.join(target_panes)}")

    except Exception as e:
        click.echo(f"Error enabling broadcast: {e}", err=True)
        ctx.exit(2)


@ broadcast.command("off")
@click.pass_context
def broadcast_off(ctx: click.Context) -> None:
    """
    Disable broadcast mode.

    Examples:
        wt2 broadcast off
    """
    ctx.obj["broadcast_active"] = False
    ctx.obj["broadcast_targets"] = []
    click.echo("Broadcast disabled")


@ broadcast.command("send")
@click.argument("command", type=str, required=True, nargs=-1)
@click.option(
    "--panes",
    "-p",
    type=str,
    default=None,
    help="Comma-separated pane IDs",
)
@click.option(
    "--all",
    "all_panes",
    is_flag=True,
    default=False,
    help="Send to all panes",
)
@click.option(
    "--shell",
    "-s",
    type=str,
    default=None,
    help="Shell type for command translation",
)
@click.pass_context
def broadcast_send(
    ctx: click.Context,
    command: tuple,
    panes: Optional[str],
    all_panes: bool,
    shell: Optional[str],
) -> None:
    """
    Send a command to broadcast targets.

    Examples:
        wt2 broadcast send "git pull"
        wt2 broadcast send "npm test" --all
        wt2 broadcast send "clear" --panes 1,2,3
    """
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    cmd_str = " ".join(command)

    try:
        target_panes: List[str] = []

        if all_panes:
            state = api.get_state()
            for tab in state.get("tabs", []):
                for pane in tab.get("panes", []):
                    target_panes.append(pane.get("id"))
        elif panes:
            target_panes = panes.split(",")
        elif ctx.obj.get("broadcast_active"):
            target_panes = ctx.obj.get("broadcast_targets", [])
        else:
            click.echo("No broadcast targets. Use --all, --panes, or enable broadcast first", err=True)
            ctx.exit(3)
            return

        if not target_panes:
            click.echo("No broadcast targets found", err=True)
            ctx.exit(3)
            return

        # Translate command for shell if needed
        if shell:
            cmd_str = _translate_command(shell, cmd_str)

        # Send to each pane
        results = []
        for pane_id in target_panes:
            result = api.send_text(cmd_str, pane_id=pane_id)
            results.append({"pane": pane_id, "success": result.get("success", True)})

        sent_count = sum(1 for r in results if r["success"])
        click.echo(f"Sent to {sent_count}/{len(results)} panes")

    except Exception as e:
        click.echo(f"Error sending broadcast: {e}", err=True)
        ctx.exit(2)


def _translate_command(shell: str, command: str) -> str:
    """Translate generic commands to shell-specific equivalents."""
    translations = {
        ("cmd", "clear"): "cls",
        ("cmd", "ls"): "dir",
        ("powershell", "clear"): "Clear-Host",
        ("powershell", "ls"): "Get-ChildItem",
        ("wsl", "clear"): "clear",
    }
    return translations.get((shell, command), command)
