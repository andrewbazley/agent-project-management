# Folder layout

<!-- Say what is where and why. Update this file in the same session that adds, closes or reopens
a stream or moves a directory, with a dated note rather than a silent rewrite. -->

## At the root

The record files (`CLAUDE.md`, `README.md`, `DECISIONS.md`, `OPEN_ITEMS.md`, `DATA_INVENTORY.md`,
this file), the whole-tree checks in `tools/`, independent reviews in `reviews/`, and
`SUPERVISION_REVIEWER.md`, the prompt for a reviewer that reads the project between sessions.

## Streams

Each line of work is a numbered folder, `NN_<name>/`. Streams are kept apart when they rest on
different assumptions and should not be read together. A new stream is opened by a decision, never
as a detour. A stream that stops is closed by a decision and stays in place under its number, with
a summary at the top of its README that sessions read instead of the stream.

| stream | status | what it is about, in one line |
|---|---|---|
| `01_<name>/` | open | <one line> |

## Inside a stream

| path | holds |
|---|---|
| `NN_<name>/README.md` | the stream's entry point: status, reading order, which results are current; the summary, once closed |
| `NN_<name>/PROMPT_NN_<topic>.md` | session briefs, numbered; the highest number is the current one |
| `NN_<name>/tools/` | the stream's scripts, each with a docstring, and its `verify_<stage>.py` |
| `NN_<name>/spec/` | frozen specifications and thresholds, versioned (`_v1`, `_v2`), with an `INDEX.md` |
| `NN_<name>/results/<stage>_<YYYYMMDD>/` | one dated directory per run that a document cites, each with an `INDEX.md`; frozen once a document or verifier reads it |
| `NN_<name>/work/` | where runs, subagents and cluster jobs write; ignored by git until a file is promoted to a results directory |
| `NN_<name>/data/` | small inputs, identifier lists, and `DOWNLOAD_LOG.md` for anything fetched |
| `NN_<name>/hpc/` | cluster job scripts and the record of each submission |
| `NN_<name>/archive/` | superseded briefs, builds and logs, kept rather than deleted |

## Not in the repository

Everything git ignores is named in `.gitignore` with the reason. Data that matters beyond the
session that made it (large inputs, costly outputs, only copies) is listed in `DATA_INVENTORY.md`
with where each copy lives and what regenerating it would cost. Lab storage for offloaded data:
<path, named in `README.md` §6>.
