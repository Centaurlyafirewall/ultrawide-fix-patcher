"""Cinematic bar removal — stretches letterbox to true aspect."""

from __future__ import annotations

import struct

from ultrawide_fix_patcher.handlers.base_handler import BaseHandler, HandlerContext
from ultrawide_fix_patcher.models.patch_result import PatchResult


class CinematicBarsHandler(BaseHandler):
    name = "cinematic_bars"

    def apply(self, ctx: HandlerContext) -> PatchResult:
        if ctx.resolved_address is None:
            return PatchResult(handler=self.name, status="skipped", detail="no resolved address")

        # Stored as a single float32 "bar fraction" of viewport height.
        # On ultrawide the game still letterboxes to 16:9 — we zero it out.
        if ctx.spec.is_ultrawide():
            raw = struct.pack("<f", 0.0)
            detail = "bars zeroed"
        else:
            raw = struct.pack("<f", 0.125)
            detail = "bars restored to 12.5%"

        if ctx.dry_run:
            return PatchResult(handler=self.name, status="dry-run", detail=f"would {detail}")