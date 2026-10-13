"""`ultrawide-fix apply` — run a patch plan against a live process."""

from __future__ import annotations

from pathlib import Path

import click

from ultrawide_fix_patcher.core.loader.plugin_loader import PluginLoader
from ultrawide_fix_patcher.core.registry.plugin_registry import PluginRegistry
from ultrawide_fix_patcher.core.session.patch_session import PatchSession
from ultrawide_fix_patcher.models.resolution_spec import ResolutionSpec
from ultrawide_fix_patcher.services.binary_inspector import BinaryInspector
from ultrawide_fix_patcher.utils.logging_setup import get_logger

log = get_logger(__name__)


@click.command("apply")
@click.argument("exe", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--width", type=int, required=True, help="Target render width, e.g. 3440.")
@click.option("--height", type=int, required=True, help="Target render height, e.g. 1440.")
@click.option("--dpi", type=int, default=96, show_default=True)
@click.option("--keep", is_flag=True, help="Do not roll back on exit (persist patches).")
@click.option("--dry-run", is_flag=True, help="Resolve signatures but write nothing.")
def apply(exe: Path, width: int, height: int, dpi: int, keep: bool, dry_run: bool) -> None:
    """Attach, resolve signatures, run handlers in plan order."""
    spec = ResolutionSpec(width=width, height=height, dpi=dpi)
    profile = BinaryInspector(exe).detect_engine()

    registry = PluginRegistry()
    PluginLoader(registry).discover()
    plugin = registry.get(profile.engine_id)
    if plugin is None:
        raise click.ClickException(f"no plugin for engine '{profile.engine_id}'")

    plan = plugin.build_plan(profile)
    with PatchSession(exe=exe, spec=spec, keep=keep, dry_run=dry_run) as session:
        results = session.run(plan)
        for r in results:
            log.info("handler=%s status=%s detail=%s", r.handler, r.status, r.detail)