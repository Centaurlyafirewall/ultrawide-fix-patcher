"""EnginePlugin contract — the single surface between host and extensions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ultrawide_fix_patcher.models.engine_profile import EngineProfile
from ultrawide_fix_patcher.models.patch_plan import PatchPlan


class EnginePlugin(ABC):
    """An engine-specific extension.

    Host guarantees:
      * ``build_plan`` is called exactly once per session, before any
        handler runs.
      * The returned ``PatchPlan`` is treated as immutable by the host.
      * Handlers referenced by the plan are imported lazily by the host
        and instantiated with no arguments.

    Plugin must guarantee:
      * ``engine_id`` is a stable, lowercase, dot-free token that also
        appears in ``signatures/<engine_id>/``.
      * ``build_plan`` does not touch the target process — it is pure
        data assembly.
    """

    engine_id: str
    display_name: str
    version: str

    @abstractmethod
    def matches(self, profile: EngineProfile) -> bool:
        """Return True if this plugin can patch the detected build."""

    @abstractmethod
    def build_plan(self, profile: EngineProfile) -> PatchPlan:
        """Assemble the ordered list of patch targets for this build."""