# Architecture

The patcher is a **plugin host**. A small core loads engine-specific
extension modules at startup, hands each one a `PatchContext`, and lets
the plugin decide which signatures to match, which handlers to run, and
in what order.

```
cli/                 entry point, argument parsing, subcommands
core/                host runtime: session, registry, loader, contracts
  contracts/         abstract base classes plugins must implement
  registry/          plugin registration + lookup by engine id
  loader/            discovery via entry points + local plugin dirs
  session/           per-run state, backup bookkeeping, rollback
handlers/            concrete corrections (fov, hud, bars, safe_area)
services/            cross-cutting: signature scanning, memory io,
                     config io, backup service, update service
models/              pydantic models: PatchTarget, PatchPlan, PatchResult,
                     Signature, EngineProfile, ResolutionSpec
utils/               logging, ac_guard, pe helpers, path helpers
plugins/             engine plugins (unreal, unity, source)
signatures/          JSON byte-pattern packs, one dir per engine
tests/               pytest suite + binary fixtures
```

## Lifecycle

1. `cli.bootstrap:main` parses argv and builds a `SessionConfig`.
2. `core.loader.PluginLoader` discovers entry points under the
   `ultrawide_fix.plugins` group and any local drop-ins in
   `%LOCALAPPDATA%\ultrawide-fix-patcher\plugins\`.
3. `core.registry.PluginRegistry` indexes plugins by `engine_id`.
4. `core.session.PatchSession` opens the target process, runs
   `ac_guard.assert_safe_target`, and snapshots writable regions.
5. The matched plugin returns a `PatchPlan` — an ordered list of
   `PatchTarget`s with signatures and handler bindings.
6. `services.signature_scanner` resolves each signature to an address.
7. Handlers run in order; each gets a `PatchContext` and may write memory
   or config files. Every write is journaled for rollback.
8. On exit (or Ctrl-C, or crash), `session.rollback()` restores the
   snapshot unless `--keep` was passed.

## Contracts

Plugins implement `EnginePlugin` (see `core/contracts/plugin.py`). The
host never imports a handler directly — it asks the plugin for a plan and
runs the plan. That's the whole point of the split: adding an engine
means adding one module, not editing the host.

## Resolution model

`ResolutionSpec` carries width, height, and DPI. Aspect is derived, not
stored. Handlers that need to know "is this ultrawide" ask
`spec.is_ultrawide()` — the threshold is 2.0 (i.e. wider than 2:1).