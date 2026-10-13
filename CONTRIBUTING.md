# Contributing to ultrawide-fix-patcher

Thanks for wanting to make 21:9 and 32:9 play nice. This is a hobbyist
patcher — no telemetry, no phone-home, no bundled binaries. Everything
you ship runs on the user's machine or it doesn't ship.

## What we accept

- **Engine plugins** under `src/ultrawide_fix_patcher/plugins/`. One
  engine per module. Register via the `ultrawide_fix.plugins` entry point
  in `pyproject.toml`.
- **Signature packs** under `signatures/`. Byte patterns for hook
  targets, aspect-ratio constants, and HUD scale floats. See
  `signatures/README.md` for the schema — yes, we keep the schema
  next to the packs so nobody has to guess.
- **Handler fixes** under `src/ultrawide_fix_patcher/handlers/`. A
  handler is a small, single-purpose correction (FOV, HUD anchor,
  cinematic bars, subtitle safe-area).
- **Tests** under `tests/`. If you add a signature, add a fixture that
  proves it matches on a known binary hash.

## What we don't accept

- Pre-built DLLs, packed executables, or anything we can't read.
- Network calls from the patcher runtime. Offline only. The updater is
  a separate opt-in script and it only fetches signature packs.
- Anything that touches anti-cheat-protected processes. The patcher
  refuses to attach if a known AC driver is loaded — see
  `utils/ac_guard.py`. Don't try to work around that refusal.

## Dev setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
ruff check src tests
```

## Style

- Python 3.11+ syntax. Type hints on every public function.
- Line length 100. Ruff defaults otherwise.
- No bare `except:`. Catch the specific thing and log it.
- Logging via `utils/logging_setup.py` — never `print()` in library code.

## Signature pack versioning

Signature packs are versioned as `pack-<engine>-<YYYYMMDD>-<seq>.json`.
Bump the seq when you edit an existing pack. Old packs stay in the repo
so users on older game builds can pin.

## Commit messages

`area: short imperative summary` — e.g. `handlers: clamp FOV to engine max`,
`signatures: add UE5.4 aspect constant for Build 2026.02`.

## Reporting bugs

Open an issue with: game name, game build, GPU, resolution, the exact
symptom, and the contents of `logs/patcher_<timestamp>.log`. Redact your
Windows username if you care — the log doesn't include it anyway.