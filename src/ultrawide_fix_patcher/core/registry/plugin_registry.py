"""In-memory index of engine plugins, keyed by engine_id."""

from __future__ import annotations

from dataclasses import dataclass

from ultrawide_fix_patcher.core.contracts.plugin import EnginePlugin
from ultrawide_fix_patcher.utils.logging_setup import get_logger

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    engine_id: str
    display_name: str
    version: str
    source: str
    plugin: EnginePlugin


class PluginRegistry:
    """Last registration wins on engine_id collision, but we log it."""

    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}

    def register(self, plugin: EnginePlugin, *, source: str) -> None:
        if not getattr(plugin, "engine_id", None):
            raise ValueError("plugin missing engine_id")
        if plugin.engine_id in self._entries:
            prior = self._entries[plugin.engine_id].source
            log.warning("engine_id %r re-registered (was %s)", plugin.engine_id, prior)
        self._entries[plugin.engine_id] = RegistryEntry(
            engine_id=plugin.engine_id,
            display_name=plugin.display_name,
            version=plugin.version,
            source=source,
            plugin=plugin,
        )

    def get(self, engine_id: str) -> EnginePlugin | None:
        entry = self._entries.get(engine_id)
        return entry.plugin if entry else None

    def all(self) -> list[RegistryEntry]:
        return sorted(self._entries.values(), key=lambda e: e.engine_id)