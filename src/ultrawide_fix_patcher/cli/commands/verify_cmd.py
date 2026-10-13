"""`ultrawide-fix verify` — check signature packs against known hashes."""

from __future__ import annotations

from pathlib import Path

import click

from ultrawide_fix_patcher.services.signature_loader import SignatureLoader
from ultrawide_fix_patcher.utils.logging_setup import get_logger

log = get_logger(__name__)


@click.command("verify")
@click.argument("pack_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def verify(pack_dir: Path) -> None:
    """Load every pack in PACK_DIR and report parse errors."""
    loader = SignatureLoader(pack_dir)
    packs = loader.load_all()
    bad = [p for p in packs if not p.is_valid()]
    log.info("loaded=%d invalid=%d", len(packs), len(bad))
    for p in bad:
        log.warning("invalid pack: %s — %s", p.path, p.error)
    if bad:
        raise click.ClickException(f"{len(bad)} invalid signature pack(s)")