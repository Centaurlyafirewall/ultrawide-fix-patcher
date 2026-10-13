"""FOV correction — rewrites the horizontal FOV constant for ultrawide."""

from __future__ import annotations

import struct

from ultrawide_fix_patcher.handlers.base_handler import BaseHandler, HandlerContext
from ultrawide_fix_patcher.models.patch_result import PatchResult
from ultrawide_fix_patcher.utils.logging_setup import get_logger

log = get_logger(__name__)

# Most engines store horizontal FOV as a float32 in degrees. Vert- scaling
# means a 21:9 panel shows less vertical FOV than a 16:9 panel at the same
# horizontal value, so we widen horizontal to compensate.
_HFOV_16_9 = 90.0


class FovHandler(BaseHandler):
    name = "fov"

    def apply(self, ctx: HandlerContext) -> PatchResult:
        if ctx.resolved_address is None:
            return PatchResult(handler=self.name, status="skipped", detail="no resolved address")

        target_hfov = self._compute_target_hfov(ctx)
        raw = struct.pack("<f", target_hfov)

        if ctx.dry_run:
            return PatchResult(handler=self.name, status="dry-run", detail=f"would write hfov={target_hfov:.2f}")

        before = ctx.mem.read(ctx.resolved_address, len(raw))
        ctx.mem.write(ctx.resolved_address, raw)
        after = ctx.mem.read(ctx.resolved_address, len(raw))
        if after != raw:
            return PatchResult(handler=self.name, status="error", detail="write verify mismatch")
        log.info("fov patched %.2f -> %.2f at 0x%x", struct.unpack("<f", before)[0], target_hfov, ctx.resolved_address)
        return PatchResult(handler=self.name, status="ok", detail=f"hfov={target_hfov:.2f}")

    def _compute_target_hfov(self, ctx: HandlerContext) -> float:
        # Preserve vertical FOV: hfov_new = 2*atan(tan(hfov_old/2) * aspect_new / aspect_old)
        import math

        aspect_old = 16.0 / 9.0
        aspect_new = ctx.spec.aspect()
        vfov_half = math.atan(math.tan(math.radians(_HFOV_16_9) / 2.0) / aspect_old)
        return math.degrees(2.0 * math.atan(math.tan(vfov_half) * aspect_new))