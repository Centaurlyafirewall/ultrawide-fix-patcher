"""BaseHandler contract shared by every correction handler."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ultrawide_fix_patcher.models.patch_result import PatchResult
from ultrawide_fix_patcher.models.patch_target import PatchTarget
from ultrawide_fix_patcher.models.resolution_spec import ResolutionSpec
from ultrawide_fix_patcher.services.memory_io import MemoryIO


@dataclass(slots=True)
class HandlerContext:
    mem: MemoryIO
    spec: ResolutionSpec
    target: PatchTarget
    dry_run: bool
    resolved_address: int | None = None


class BaseHandler(ABC):
    """Resolve → write → verify. Handlers never touch the process directly."""

    name: str = "base"

    def prepare(
        self,
        *,
        mem: MemoryIO,
        spec: ResolutionSpec,
        target: PatchTarget,
        dry_run: bool,
    ) -> HandlerContext:
        return HandlerContext(mem=mem, spec=spec, target=target, dry_run=dry_run)

    @abstractmethod
    def apply(self, ctx: HandlerContext) -> PatchResult: ...