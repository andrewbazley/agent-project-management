# Open items

Questions raised and not yet acted on, each with the condition that would close it.

---

## 1. The template has no working rules file

`DECISIONS.md` 4. Until it has one, a new project's citation check fails on every reference to
`CLAUDE.md`, and each user decides what their rules file says.

**Closing condition** A lab-standard `CLAUDE.md` is added to `02_template/`, or the root `README.md`
links to the one to copy.

**Closed 2026-11-19.** `02_template/CLAUDE.md` added; `DECISIONS.md` 4a.

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

## 7. Offloading is untested against real lab storage

`02_template/tools/offload.py` was tested on one volume with `--same-volume`, including a changed
stored file, a replaced manifest, storage that is not mounted, prune and restore. It has not copied
to a network share or a cluster file system, where timestamps, permissions and interrupted copies
behave differently, and its SKIP-or-FAIL rule for a missing location relies on the share being a
separate volume.

`copy` also needs the storage mounted on the machine that holds the data. A cluster file system
reached only over SSH is not supported; that would need a copy over SSH and a hash check run on
the cluster, inside a job where the cluster's rules require one.

**Closing condition** One real set is offloaded to lab storage, pruned, checked with `--full` and
restored, and any problem is fixed or stated in the tool's docstring.

## 8. The survey's states and budgets are untested on a real project

`02_template/tools/survey.py` was checked on template copies only. The budget thresholds (12 root
files, 3 briefs, 20 status lines, 100 unreferenced files or 1 GB) are judgments, and projects that
cite through generated reports may show live material as unreferenced.

**Closing condition** The survey is run on a project of several streams, its unreferenced list is
reviewed by hand, and the rules or thresholds are adjusted in a decision.

**2026-11-19.** Run on a clone of a project that predates the template (4,041 files). It took under
3 seconds and read that project's own data inventory, but found almost nothing unreferenced,
because the project's README cites 39 documents directly and the reading path reaches 104
documents (42,533 lines). The fan-out from the entry points was the useful measure, so the survey
now reports it and warns above 12 documents, and the skill gained "shorten an entry point". Not
yet run on a project built from the template.

