# Security Policy

## Scope

`ultrawide-fix-patcher` reads game executables, writes patched bytes to
in-memory copies, and optionally persists corrected config files. It
does **not**:

- open network sockets at runtime
- install kernel drivers
- touch processes protected by EasyAntiCheat, BattlEye, or Vanguard
- modify files outside the game's own install directory and our
  `backups/` folder

If you find behavior that contradicts that list, that's a security bug.

## Reporting a vulnerability

Email `security@ultrawide-fix-patcher.invalid` with:

- affected version (from `ultrawide-fix --version`)
- a minimal reproduction
- the patcher log (`logs/patcher_<timestamp>.log`)

PGP key fingerprint is listed in `docs/SIGNING.md`. Expect an ack within
72 hours. We don't run a bug bounty; we do credit reporters in
`docs/CREDITS.md` if they want.

## Anti-cheat interaction

The patcher's `utils/ac_guard.py` refuses to attach to any process with a
loaded AC driver from the blocklist. Bypassing that guard is out of scope
for this project and pull requests that weaken it will be closed without
discussion. We patch offline / single-player games and offline modes of
multiplayer games. That's the line.

## Supported versions

Only the latest minor release receives fixes. Signature pack updates
ship independently of code releases.

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | no        |
| < 0.5   | no        |