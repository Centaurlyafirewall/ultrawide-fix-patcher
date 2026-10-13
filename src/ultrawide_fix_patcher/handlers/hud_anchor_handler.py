"""HUD anchor correction — widens the safe-area so HUD doesn't squish."""

from __future__ import annotations

import struct

from ultrawide_fix_patcher.handlers.base_handler import BaseHandler, HandlerContext
from ultrawide_fix_patcher.models.patch_result import PatchResult


class HudAnchorHandler(BaseHandler):
    name = "hud_anchor"

    def apply(self, ctx: HandlerContext) -> PatchResult:
        if ctx.resolved_address is None:
            return PatchResult(handler=self.name, status="skipped", detail="no resolved address")

        # HUD safe-area is stored as two float32s: left, right, in normalized units.
        # We push both outward proportionally to the extra horizontal space.
        extra = (ctx.spec.aspect() - (16.0 / 9.0)) / (16.0 / 9.0)
        left = max(0.0, 0.5 - (0.5 * (1.0 + extra)))
        right = min(1.0, 0.5 + (0.5 * (1.0 + extra)))
        raw = struct.pack("<ff", left, right)

        if ctx.dry_run:
            return PatchResult(handler=self.name, status="dry-run", detail=f"would write safe_area=({left:.3f},{right:.3f})")

        ctx.mem.write(ctx.resolved_address, raw)
        return PatchResult(handler=self.name, status="ok", detail=f"safe_area=({left:.3f},{right:.3f})")