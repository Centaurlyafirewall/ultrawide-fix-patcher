"""PatchSession — owns the target process, snapshot, and rollback journal."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType

from ultrawide_fix_patcher.models.patch_plan import PatchPlan
from ultrawide_fix_patcher.models.patch_result import PatchResult
from ultrawide_fix_patcher.models.resolution_spec import ResolutionSpec
from ultrawide_fix_patcher.services.memory_io import MemoryIO
from ultrawide_fix_patcher.services.snapshot_service import SnapshotService
from ultrawide_fix_patcher.utils.ac_guard import assert_safe_target
from ultrawide_fix_patcher.utils.logging_setup import get_logger

log = get_logger(__name__)


class PatchSession:
    """Context manager. Snapshot on enter, rollback on exit unless keep=True."""

    def __init__(
        self,
        *,
        exe: Path,
        spec: ResolutionSpec,
        keep: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.exe = exe
        self.spec = spec
        self.keep = keep
        self.dry_run = dry_run
        self._mem: MemoryIO | None = None
        self._snap: SnapshotService | None = None

    def __enter__(self) -> "PatchSession":
        assert_safe_target(self.exe)
        self._mem = MemoryIO.attach(self.exe)
        self._snap = SnapshotService(self._mem)
        log.info("session open exe=%s spec=%sx%s@%sdpi", self.exe.name, self.spec.width, self.spec.height, self.spec.dpi)
        return self

    def run(self, plan: PatchPlan) -> list[PatchResult]:
        if self._mem is None:
            raise RuntimeError("session not entered")
        results: list[PatchResult] = []
        for target in plan.targets:
            handler_cls = _import_handler(target.handler)
            handler = handler_cls()
            ctx = handler.prepare(mem=self._mem, spec=self.spec, target=target, dry_run=self.dry_run)
            try:
                results.append(handler.apply(ctx))
            except Exception as exc:  # noqa: BLE001 — a broken handler must not orphan the session
                log.exception("handler %s failed", target.handler)
                results.append(PatchResult(handler=target.handler, status="error", detail=str(exc)))
        return results

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._snap is not None and not self.keep:
            self._snap.rollback()
        if self._mem is not None:
            self._mem.detach()
        log.info("session closed keep=%s", self.keep)


def _import_handler(dotted: str):
    import importlib

    mod_name, _, cls_name = dotted.rpartition(".")
    mod = importlib.import_module(mod_name)
    return getattr(mod, cls_name)