# Open items

Questions raised and not yet acted on, each with the condition that would close it.

---

## 1. The template has no working rules file

`DECISIONS.md` 4. Until it has one, a new project's citation check fails on every reference to
`CLAUDE.md`, and each user decides what their rules file says.

**Closing condition** A lab-standard `CLAUDE.md` is added to `02_template/`, or the root `README.md`
links to the one to copy.

## 2. The plugin has not been installed from a second account

The repository is private. Installation depends on each user's git credentials, which has not been
tested.

**Closing condition** One lab member installs the plugin, runs one skill, and any problem is fixed
in the root `README.md`.

## 3. The template has not started a real project

Everything here was generalized from projects that grew their conventions as they went. None has
yet been started from this template.

**Closing condition** A project started from the template reaches its third brief, and what was
missing or unnecessary is recorded here.

## 4. Part of the gate is not implemented

`01_guide/supervision.md` describes invariants beyond what `02_template/tools/verify_all.sh` checks: the
prediction block unchanged since its commit, the skip count not risen between runs, and a verifier
allowlist not grown.

**Closing condition** Each is implemented as a tool, or judged unnecessary with a reason in
`DECISIONS.md`.

## 5. The tools are untested on Linux

Tested on macOS only. Case-sensitive file systems and GNU tools may behave differently.

**Closing condition** `02_template/tools/verify_all.sh` passes on a template copy on a Linux machine.

## 6. Root detection stops at the nearest `CLAUDE.md`

A stream that has its own `CLAUDE.md` would be taken as the project root. Each tool accepts
`--root` to override this.

**Closing condition** Detection prefers `.git` when both are present, or the limitation is stated
in `02_template/tools/README.md`.
