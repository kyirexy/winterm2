"""
Configuration management commands for winterm2.

Provides commands for loading, saving, and managing configuration files.
"""

from __future__ import annotations
import os
import click
from pathlib import Path
from typing import Optional, Dict, Any

import yaml

# Default config path
DEFAULT_CONFIG_PATH = Path(os.path.expanduser("~/.wt2rc.yaml"))


@click.group()
def config():
    """
    Configuration management commands.

    Commands:
        get     - Get a configuration value
        set     - Set a configuration value
        load    - Load a configuration file
        save    - Save the current configuration
        init    - Initialize a new config file
        edit    - Edit the config file
        path    - Show config file path
    """
    pass


@config.command("path")
@click.pass_context
def config_path(ctx: click.Context) -> None:
    """
    Show the default configuration file path.

    Examples:
        wt2 config path
    """
    click.echo(str(DEFAULT_CONFIG_PATH))


@config.command("init")
@click.argument("path", type=click.Path(), required=False)
@click.pass_context
def init_config(ctx: click.Context, path: Optional[str]) -> None:
    """
    Initialize a new configuration file.

    Examples:
        wt2 config init
        wt2 config init /path/to/config.yaml
    """
    config_file = Path(path) if path else DEFAULT_CONFIG_PATH

    # Create default configuration
    default_config = {
        "version": "1.0",
        "defaults": {
            "shell": "powershell",
            "startup_dir": str(Path.home()),
        },
        "profiles": {},
        "workflows": {},
    }

    try:
        # Create parent directories
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Write config file
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

        click.echo(f"Created configuration file: {config_file}")

    except Exception as e:
        click.echo(f"Error creating config: {e}", err=True)
        ctx.exit(1)


@config.command("load")
@click.argument("path", type=click.Path(), required=True)
@click.option(
    "--profile",
    "-p",
    type=str,
    default=None,
    help="Profile to load from the config",
)
@click.pass_context
def load_config(ctx: click.Context, path: str, profile: Optional[str]) -> None:
    """
    Load a configuration file and optionally apply a profile.

    Examples:
        wt2 config load ~/.wt2rc.yaml
        wt2 config load config.yaml --profile dev
    """
    config_path = Path(path)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            click.echo("Invalid configuration file", err=True)
            ctx.exit(4)
            return

        # Store config in context
        ctx.obj["config"] = config
        ctx.obj["config_path"] = str(config_path)

        click.echo(f"Loaded configuration from: {config_path}")

        if profile:
            if profile in config.get("profiles", {}):
                ctx.obj["profile"] = config["profiles"][profile]
                click.echo(f"Applied profile: {profile}")
            else:
                click.echo(f"Profile '{profile}' not found", err=True)
                ctx.exit(3)

    except FileNotFoundError:
        click.echo(f"Config file not found: {path}", err=True)
        ctx.exit(2)
    except yaml.YAMLError as e:
        click.echo(f"Invalid YAML: {e}", err=True)
        ctx.exit(4)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        ctx.exit(1)


@config.command("get")
@click.argument("key", type=str, required=True)
@click.pass_context
def get_config(ctx: click.Context, key: str) -> None:
    """
    Get a configuration value.

    Examples:
        wt2 config get defaults.shell
        wt2 config get profiles.dev.window.size
    """
    config = ctx.obj.get("config", {})

    try:
        # Navigate nested keys
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break

        if value is not None:
            import json
            click.echo(json.dumps(value, indent=2))
        else:
            click.echo(f"Key not found: {key}", err=True)
            ctx.exit(3)

    except Exception as e:
        click.echo(f"Error getting config: {e}", err=True)
        ctx.exit(1)


@config.command("set")
@click.argument("key", type=str, required=True)
@click.argument("value", type=str, required=True)
@click.pass_context
def set_config(ctx: click.Context, key: str, value: str) -> None:
    """
    Set a configuration value.

    Examples:
        wt2 config set defaults.shell PowerShell
    """
    config = ctx.obj.get("config", {})

    try:
        # Parse value as YAML
        parsed_value = yaml.safe_load(value)

        # Navigate and set nested key
        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = parsed_value
        ctx.obj["config"] = config

        click.echo(f"Set {key} = {value}")

    except Exception as e:
        click.echo(f"Error setting config: {e}", err=True)
        ctx.exit(1)


@config.command("save")
@click.argument("path", type=click.Path(), required=False)
@click.pass_context
def save_config(ctx: click.Context, path: Optional[str]) -> None:
    """
    Save the current configuration to a file.

    Examples:
        wt2 config save
        wt2 config save /path/to/backup.yaml
    """
    config = ctx.obj.get("config", {})
    config_path = Path(path) if path else ctx.obj.get("config_path", str(DEFAULT_CONFIG_PATH))

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        click.echo(f"Saved configuration to: {config_path}")

    except Exception as e:
        click.echo(f"Error saving config: {e}", err=True)
        ctx.exit(1)


@config.command("edit")
@click.pass_context
def edit_config(ctx: click.Context) -> None:
    """
    Edit the configuration file in the default editor.

    Examples:
        wt2 config edit
    """
    config_path = ctx.obj.get("config_path", str(DEFAULT_CONFIG_PATH))

    try:
        # Get editor
        editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "notepad"))

        import subprocess
        result = subprocess.run([editor, config_path], check=False)

        if result.returncode == 0:
            # Reload config if edited successfully
            ctx.invoke(load_config, path=config_path)

    except Exception as e:
        click.echo(f"Error editing config: {e}", err=True)
        ctx.exit(1)


@config.command("list")
@click.pass_context
def list_config(ctx: click.Context) -> None:
    """
    List all configuration sections.

    Examples:
        wt2 config list
    """
    config = ctx.obj.get("config", {})

    click.echo("Configuration:")
    click.echo("-" * 40)

    for key, value in config.items():
        if isinstance(value, dict):
            click.echo(f"  {key}:")
            for sub_key in list(value.keys())[:5]:  # Show first 5
                click.echo(f"    - {sub_key}")
            if len(value) > 5:
                click.echo(f"    ... ({len(value)} total items)")
        else:
            click.echo(f"  {key}: {value}")


@config.command("reload")
@click.pass_context
def reload_config(ctx: click.Context) -> None:
    """
    Reload configuration from file.

    Examples:
        wt2 config reload
    """
    config_path = ctx.obj.get("config_path", str(DEFAULT_CONFIG_PATH))
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        ctx.obj["config"] = config
        click.echo("Configuration reloaded")

        # Show summary
        profiles = config.get("profiles", {})
        workflows = config.get("workflows", {})
        if profiles:
            click.echo(f"Profiles: {', '.join(profiles.keys())}")
        if workflows:
            click.echo(f"Workflows: {', '.join(workflows.keys())}")
    except FileNotFoundError:
        click.echo(f"Config file not found: {config_path}", err=True)
        ctx.exit(2)
    except Exception as e:
        click.echo(f"Error reloading config: {e}", err=True)
        ctx.exit(1)


@config.command("alias")
@click.argument("alias_name", type=str, required=False)
@click.pass_context
def cmd_alias(ctx: click.Context, alias_name: str | None) -> None:
    """
    Execute or list aliases from config.

    Examples:
        wt2 config alias deploy
        wt2 config alias
    """
    config = ctx.obj.get("config", {})
    aliases = config.get("aliases", {})

    if not aliases:
        click.echo("No aliases defined in config")
        ctx.exit(3)
        return

    if alias_name:
        alias_cmd = aliases.get(alias_name)
        if not alias_cmd:
            click.echo(f"Alias '{alias_name}' not found", err=True)
            ctx.exit(3)
            return

        click.echo(f"Running alias '{alias_name}': {alias_cmd}")

        # Parse and execute the alias command
        import shlex
        try:
            args = shlex.split(alias_cmd)
            # Remove 'wt2' prefix if present
            if args and args[0] == "wt2":
                args = args[1:]

            # Create a new argument list for Click
            original_argv = __import__("sys").argv
            __import__("sys").argv = ["wt2"] + args

            from ..cli import cli
            cli(standalone_mode=False)

            __import__("sys").argv = original_argv
        except Exception as e:
            click.echo(f"Failed to execute alias: {e}", err=True)
            ctx.exit(4)
    else:
        click.echo("Available aliases:")
        for name, cmd in aliases.items():
            click.echo(f"  {name}: {cmd}")


@config.group()
def profile():
    """Profile management commands."""
    pass


@profile.command("list")
@click.pass_context
def profile_list(ctx: click.Context) -> None:
    """List all profiles in config."""
    config = ctx.obj.get("config", {})
    profiles = config.get("profiles", {})

    if not profiles:
        click.echo("No profiles defined in config")
        return

    click.echo("Profiles:")
    for name in profiles:
        click.echo(f"  - {name}")


@profile.command("show")
@click.argument("name", type=str, required=True)
@click.pass_context
def profile_show(ctx: click.Context, name: str) -> None:
    """Show profile details."""
    config = ctx.obj.get("config", {})
    profiles = config.get("profiles", {})

    if name not in profiles:
        click.echo(f"Profile '{name}' not found", err=True)
        ctx.exit(3)
        return

    import json
    profile_data = profiles[name]
    click.echo(json.dumps(profile_data, indent=2))


@profile.command("apply")
@click.argument("name", type=str, required=True)
@click.pass_context
def profile_apply(ctx: click.Context, name: str) -> None:
    """Apply a profile from config."""
    config = ctx.obj.get("config", {})
    profiles = config.get("profiles", {})

    if name not in profiles:
        click.echo(f"Profile '{name}' not found", err=True)
        ctx.exit(3)
        return

    profile_data = profiles[name]
    ctx.obj["profile"] = profile_data
    click.echo(f"Applied profile: {name}")

    # Execute profile steps
    from ..core.terminal import get_api
    api = get_api()

    for step in profile_data.get("steps", []):
        if "command" in step:
            api.send_text(step["command"] + "\r")
            click.echo(f"  Running: {step['command']}")
        elif "split" in step:
            split_type = step["split"]
            direction = "vertical" if split_type == "vertical" else "horizontal"
            api.new_pane(direction=direction)
            click.echo(f"  Split: {split_type}")
