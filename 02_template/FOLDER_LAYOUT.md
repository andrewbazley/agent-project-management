# Folder layout

<!-- Say what is where and why. Update this file in the same session that adds a stream or moves a
directory, with a dated note rather than a silent rewrite. -->

## At the root

The record files (`CLAUDE.md`, `README.md`, `DECISIONS.md`, `OPEN_ITEMS.md`, this file), the
whole-tree checks in `tools/`, independent reviews in `reviews/`, and `SUPERVISION_REVIEWER.md`,
the prompt for a reviewer that reads the project between sessions.

## Streams

Each line of work is a numbered folder, `NN_<name>/`. Streams are kept apart when they rest on
different assumptions and should not be read together. A new stream is opened by a decision, never
as a detour, and an old one is left in place when work moves on.

| path | holds |
|---|---|
| `NN_<name>/README.md` | the stream's entry point: status, reading order, which results are current |
| `NN_<name>/PROMPT_NN_<topic>.md` | session briefs, numbered; the highest number is the current one |
| `NN_<name>/tools/` | the stream's scripts, each with a docstring, and its `verify_<stage>.py` |
| `NN_<name>/spec/` | frozen specifications and thresholds, versioned (`_v1`, `_v2`), with an `INDEX.md` |
| `NN_<name>/results/<stage>_<YYYYMMDD>/` | one dated directory per run, each with an `INDEX.md`; frozen once a document or verifier reads it |
| `NN_<name>/data/` | small inputs, identifier lists, and `DOWNLOAD_LOG.md` for anything fetched |
| `NN_<name>/hpc/` | cluster job scripts and the record of each submission |
| `NN_<name>/archive/` | superseded briefs, builds and logs, kept rather than deleted |

## Not in the repository

<!-- Large inputs, regenerable outputs and scratch. Each is named in .gitignore with the reason
and the way to get it back. If the omitted material is large or scattered, keep an
ARCHIVE_MANIFEST.md listing what was left out, where it lives and how to regenerate it, and
mark anything that is the only copy. -->
