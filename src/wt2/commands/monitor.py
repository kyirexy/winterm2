"""
Monitor commands for winterm2.

Provides real-time output monitoring and filtering capabilities.
"""

from __future__ import annotations
import click
import threading
import queue
import time
from typing import Optional, Callable

from ..core.terminal import WindowsTerminalAPI, get_api


class OutputMonitor:
    """Monitor terminal output in real-time."""

    def __init__(
        self,
        pane_id: Optional[str] = None,
        keyword: Optional[str] = None,
        timeout: float = 0.0,
    ):
        """
        Initialize the output monitor.

        Args:
            pane_id: Pane ID to monitor (None for focused)
            keyword: Keyword to filter output
            timeout: Maximum monitoring time (0 = infinite)
        """
        self.pane_id = pane_id
        self.keyword = keyword.lower() if keyword else None
        self.timeout = timeout
        self._running = False
        self._output_queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._lines_matched = 0
        self._lines_total = 0

    def start(self) -> None:
        """Start monitoring."""
        self._running = True
        self._stop_event.clear()

    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
        self._stop_event.set()

    def is_running(self) -> bool:
        """Check if monitoring is active."""
        return self._running

    def process_output(self, text: str) -> bool:
        """
        Process output line.

        Args:
            text: Output text to process

        Returns:
            True if line should be displayed
        """
        self._lines_total += 1

        if self.keyword:
            if self.keyword in text.lower():
                self._lines_matched += 1
                return True
            return False

        return True


@click.group()
def monitor():
    """
    Real-time output monitoring commands.

    Commands:
        follow   - Follow pane output in real-time
        watch    - Watch for keyword matches
        tail     - Show last N lines of output
    """
    pass


@ monitor.command("follow")
@click.option(
    "--pane-id",
    type=str,
    default=None,
    help="Pane ID to monitor (defaults to focused)",
)
@click.option(
    "--timeout",
    "-t",
    type=float,
    default=0,
    help="Maximum monitoring time in seconds (0 = infinite)",
)
@click.option(
    "--lines",
    "-l",
    type=int,
    default=0,
    help="Number of recent lines to show first",
)
@click.pass_context
def follow_output(
    ctx: click.Context,
    pane_id: Optional[str],
    timeout: float,
    lines: int,
) -> None:
    """
    Follow pane output in real-time.

    Examples:
        wt2 monitor follow
        wt2 monitor follow --pane-id 1
        wt2 monitor follow --timeout 60
    """
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())

    try:
        monitor_instance = OutputMonitor(pane_id=pane_id, timeout=timeout)
        monitor_instance.start()

        click.echo(f"Following output (Ctrl+C to stop)...")

        # Start monitoring in background thread
        def _monitor_loop():
            while monitor_instance.is_running() and not monitor_instance._stop_event.is_set():
                try:
                    # Simulate output monitoring
                    # In real implementation, this would read from terminal output
                    time.sleep(0.1)
                except Exception:
                    break

        monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
        monitor_thread.start()

        # Wait for interrupt or timeout
        try:
            while monitor_instance.is_running():
                time.sleep(0.5)
                if timeout > 0:
                    if monitor_instance._lines_total > 0:
                        pass  # Would show progress
        except KeyboardInterrupt:
            monitor_instance.stop()
            click.echo("\nStopped monitoring")

    except Exception as e:
        click.echo(f"Error monitoring output: {e}", err=True)
        ctx.exit(2)


@ monitor.command("watch")
@click.argument("keyword", type=str, required=True)
@click.option(
    "--pane-id",
    type=str,
    default=None,
    help="Pane ID to monitor",
)
@click.option(
    "--timeout",
    "-t",
    type=float,
    default=0,
    help="Maximum monitoring time in seconds",
)
@click.option(
    "--count",
    "-c",
    type=int,
    default=0,
    help="Stop after N matches (0 = infinite)",
)
@click.pass_context
def watch_keyword(
    ctx: click.Context,
    keyword: str,
    pane_id: Optional[str],
    timeout: float,
    count: int,
) -> None:
    """
    Watch for keyword matches in output.

    Examples:
        wt2 monitor watch "error"
        wt2 monitor watch "Exception" --timeout 30
        wt2 monitor watch "SUCCESS" --count 5
    """
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())

    try:
        monitor_instance = OutputMonitor(pane_id=pane_id, keyword=keyword, timeout=timeout)
        monitor_instance.start()

        click.echo(f"Watching for '{keyword}' (Ctrl+C to stop)...")
        matches = 0

        # In real implementation, this would:
        # 1. Connect to terminal output stream
        # 2. Stream output line by line
        # 3. Filter and display matching lines

        def _check_for_match(text: str) -> bool:
            nonlocal matches
            if keyword.lower() in text.lower():
                matches += 1
                return True
            return False

        # Simulated monitoring loop
        start_time = time.time()
        try:
            while monitor_instance.is_running():
                time.sleep(0.5)

                # Check timeout
                if timeout > 0 and (time.time() - start_time) >= timeout:
                    break

                # Check match count
                if count > 0 and matches >= count:
                    break

        except KeyboardInterrupt:
            pass

        monitor_instance.stop()
        click.echo(f"Found {matches} match(es)")

    except Exception as e:
        click.echo(f"Error watching output: {e}", err=True)
        ctx.exit(2)


@ monitor.command("tail")
@click.argument("lines", type=int, required=False, default=20)
@click.option(
    "--pane-id",
    type=str,
    default=None,
    help="Pane ID to get output from",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    default=False,
    help="Output as JSON",
)
@click.pass_context
def tail_output(
    ctx: click.Context,
    lines: int,
    pane_id: Optional[str],
    output_json: bool,
) -> None:
    """
    Show the last N lines of pane output.

    Examples:
        wt2 monitor tail
        wt2 monitor tail 50
        wt2 monitor tail --pane-id 1 --json
    """
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())

    try:
        # Get recent output from terminal
        result = api.send_command("getOutput", paneId=pane_id, limit=lines)

        if output_json:
            import json
            click.echo(json.dumps(result, indent=2))
        else:
            output = result.get("output", "")
            output_lines = output.strip().split("\n")[-lines:]
            for line in output_lines:
                click.echo(line)

    except Exception as e:
        click.echo(f"Error getting output: {e}", err=True)
        ctx.exit(2)
