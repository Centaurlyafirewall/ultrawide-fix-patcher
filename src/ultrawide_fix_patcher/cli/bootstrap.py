"""Entry point. Parses argv, wires the host, hands off to a command."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from ultrawide_fix_patcher import __version__
from ultrawide_fix_patcher.cli.commands import apply_cmd, list_cmd, scan_cmd, verify_cmd
from ultrawide_fix_patcher.utils.logging_setup import configure_logging


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="ultrawide-fix")
@click.option(
    "--log-dir",
    type=click.Path(path_type=Path, file_okay=False),
    default=None,
    help="Directory for patcher logs. Defaults to ./logs.",
)
@click.option("-v", "--verbose", is_flag=True, help="Debug-level logging.")
def main(log_dir: Path | None, verbose: bool) -> None:
    """Widescreen / ultrawide fix patcher."""
    configure_logging(log_dir=log_dir, verbose=verbose)


main.add_command(scan_cmd.scan)
main.add_command(apply_cmd.apply)
main.add_command(list_cmd.list_plugins)
main.add_command(verify_cmd.verify)


if __name__ == "__main__":
    sys.exit(main())