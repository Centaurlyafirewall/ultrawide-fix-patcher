"""Discover engine plugins via entry points and a local drop-in dir."""

from __future__ import annotations

import importlib.metadata as md
import os
from pathlib import Path

from ultrawide_fix_patcher.core.registry.plugin_registry import PluginRegistry
from ultrawide_fix_patcher.utils.logging_setup import get_logger

log = get_logger(__name__)

_ENTRY_GROUP = "ultrawide_fix.plugins"
_LOCAL_DIR_ENV = "ULTRAWIDE_FIX_PLUGIN_DIR"


class PluginLoader:
    """Populates a registry from installed entry points + local drop-ins."""

    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    def discover(self) -> PluginRegistry:
        self._load_entry_points()
        self._load_local_dir()
        return self._registry

    def _load_entry_points(self) -> None:
        for ep in md.entry_points(group=_ENTRY_GROUP):
            try:
                cls = ep.load()
                self._registry.register(cls(), source=f"entrypoint:{ep.name}")
            except Exception as exc:  # noqa: BLE001 — one bad plugin must not kill discovery
                log.warning("failed to load entry point %s: %s", ep.name, exc)

    def _load_local_dir(self) -> None:
        raw = os.environ.get(_LOCAL_DIR_ENV)
        if not raw:
            return
        local = Path(raw).expanduser()
        if not local.is_dir():
            log.debug("local plugin dir missing: %s", local)
            return
        for py in sorted(local.glob("*.py")):
            self._load_file(py)

    def _load_file(self, path: Path) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(f"uwfix_local_{path.stem}", path)
        if spec is None or spec.loader is None:
            log.warning("unloadable plugin file: %s", path)
            return
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001
            log.warning("plugin %s raised on import: %s", path.name, exc)
            return
        for attr in vars(mod).values():
            if isinstance(attr, type) and getattr(attr, "engine_id", None) and attr.__module__ == mod.__name__:
                try:
                    self._registry.register(attr(), source=f"local:{path.name}")
                except TypeError:
                    pass  # not a zero-arg plugin class