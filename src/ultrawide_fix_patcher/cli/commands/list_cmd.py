"""`ultrawide-fix list` — show discovered plugins."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from ultrawide_fix_patcher.core.loader.plugin_loader import PluginLoader
from ultrawide_fix_patcher.core.registry.plugin_registry import PluginRegistry


@click.command("list")
def list_plugins() -> None:
    """List engine plugins visible to the host."""
    registry = PluginRegistry()
    loader = PluginLoader(registry)
    loader.discover()

    table = Table(title="engine plugins")
    table.add_column("engine_id")
    table.add_column("display name")
    table.add_column("source")
    table.add_column("version")
    for entry in registry.all():
        table.add_row(entry.engine_id, entry.display_name, entry.source, entry.version)
    Console().print(table)