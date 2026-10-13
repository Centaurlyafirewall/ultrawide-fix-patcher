"""`ultrawide-fix scan` — detect the engine and print a patch plan."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ultrawide_fix_patcher.core.loader.plugin_loader import PluginLoader
from ultrawide_fix_patcher.core.registry.plugin_registry import PluginRegistry
from ultrawide_fix_patcher.models.engine_profile import EngineProfile
from ultrawide_fix_patcher.services.binary_inspector import BinaryInspector
from ultrawide_fix_patcher.utils.logging_setup import get_logger

log = get_logger(__name__)
console = Console()


@click.command("scan")
@click.argument("exe", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def scan(exe: Path) -> None:
    """Fingerprint EXE, match an engine plugin, print the plan."""
    inspector = BinaryInspector(exe)
    profile: EngineProfile = inspector.detect_engine()
    console.print(f"[bold]target[/]: {exe}")
    console.print(f"[bold]engine[/]: {profile.engine_id} ({profile.confidence:.0%} confidence)")

    registry = PluginRegistry()
    PluginLoader(registry).discover()
    plugin = registry.get(profile.engine_id)
    if plugin is None:
        console.print("[yellow]no plugin registered for this engine[/]")
        return

    plan = plugin.build_plan(profile)
    table = Table(title=f"patch plan — {plugin.display_name}")
    table.add_column("#", justify="right")
    table.add_column("handler")
    table.add_column("signature")
    table.add_column("notes")
    for i, target in enumerate(plan.targets, 1):
        table.add_row(str(i), target.handler, target.signature_name, target.notes or "")
    console.print(table)