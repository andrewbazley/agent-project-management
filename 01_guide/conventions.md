# Conventions

How a project is organized, named and kept under version control. The working rules themselves
are in the project's `CLAUDE.md`, and the file formats are in `02_template/`; this page explains
the parts that neither states.

## The idea

A long project is run as a chain of sessions, and no session remembers the last one. Everything a
later session needs is on disk and committed: what was decided and why, what was measured, what is
open, and what to do next. Git supplies the ordering. A decision committed before the result it
governs is a prediction, and git can prove it was written first. A decision committed after is a
rationalization, whatever its text says.

## The record files

| file | written when | read when |
|---|---|---|
| `README.md` | at the start; status line rewritten every session | first, by everyone |
| `CLAUDE.md` | rarely; a new rule needs a real failure behind it | every session, in full |
| `DECISIONS.md` | before the work each entry governs | the entries a brief names |
| `OPEN_ITEMS.md` | whenever a question is deferred | the items a brief names |
| `FOLDER_LAYOUT.md` | when a stream is opened or closed, or a directory moved | when looking for something |
| `DATA_INVENTORY.md` | when data leaves git or is offloaded | before moving or removing any data |
| `NN_<stream>/PROMPT_NN_*.md` | at the end of every session | at the start of the next |
| `NN_<stream>/README.md` | when a stage finishes or a result is corrected | on entering the stream |
| `results/<run>/INDEX.md` | when the run's outputs are written | before trusting any file in it |

Each idea has one home. A number lives in an evidence table and documents cite it; a rule lives in
`CLAUDE.md` or `README.md` §6 and briefs cite it; a question lives in `OPEN_ITEMS.md` and briefs
list its number. Restating instead of citing is how two copies come to disagree.

## Naming

- Streams: `NN_<short_name>/`, numbered in the order they were opened.
- Briefs: `PROMPT_NN_<topic>.md`, numbered within the stream. The highest number is current.
- Run outputs: `results/<stage>_<YYYYMMDD>/`. A second run on the same day takes a suffix.
- Versioned specifications: `<name>_v1.json`, `<name>_v2.json`. Never edited in place.
- Dated one-off documents: `<TOPIC>_YYYY-MM-DD.md`, for example a review or a search record.
- Root-level documents are few and in capitals. Avoid `REPORT2.md`, `REPORT3.md` and
  `results7/` at the root: an earlier project reached fourteen numbered reports and nine numbered
  results directories at its root, and nobody could tell which ones were current.

## Version control

**What to commit.** Every document, script, specification, index and evidence table. Small
outputs that a document reads. Cluster job scripts and their logs.

**What to leave out.** Large inputs that can be fetched again, outputs that regenerate from
committed code, environments, and scratch. Each `.gitignore` rule carries a comment saying why and
how to get the file back, and `DATA_INVENTORY.md` lists the data that matters, where each copy
lives and which are only copies. GitHub rejects files over 100 MB and warns above 50 MB.

**When to commit.** At each verified step: after a decision is written and before the run it
governs, after a run is indexed and verified, after a correction is propagated. One logical change
per commit.

**Commit messages** state what is now true, in one sentence a reader can understand without the
diff:

- "Stage 1 counted 34 qualifying positions; prediction P4 failed by five"
- "Correct stage 1's elapsed time: 00:46:12, not the 00:42 read off a running job"
- "Log the reference download before fetching it, with sizes measured"

Avoid "update files", "fixes", "WIP" and messages that describe the activity instead of the
result. Never rewrite pushed history; a correction is a new commit.

**Branches.** A single writer can work on `main`. Parallel sessions that write code each get their
own branch or worktree and merge back through the orchestrating session.

**Public and private.** If the project produces something public (a package, a website), keep the
research record in a separate private repository, or enforce the split with a check that fails
when a private path (briefs, `DECISIONS.md`, notes, test data) is staged in the public one.
`.gitignore` alone does not stop a forced add.

## Adopting an existing project

Most projects start before the record does. To bring one under this system:

1. Put it under git as it is, so the starting state is recoverable.
2. Write `DECISIONS.md` opening at decision 1, with a preamble saying the record starts now and
   where earlier decisions live. Do not reconstruct old decisions as if they had been written at
   the time.
3. Inventory the data: what must never be deleted, what is reconstructible and at what cost, and
   what can go. Mark the only copies.
4. Move loose root files into streams and `archive/`, leaving a stub at any old path a document
   still cites, and close finished lines of work with a summary (`tidy-project`).
5. Write `README.md`, `FOLDER_LAYOUT.md` and the first brief from what is actually on disk. Where a
   document has to be reconstructed, say so at its top.

The `adopt-project` skill walks through this.

## Keeping a project small

The rules are `CLAUDE.md` §13 and the procedure is the `tidy-project` skill. What neither states is
how the parts fit.

A file is in one of three states, which `tools/survey.py` works out from the citations. It is
**live** if a current document leads to it: the root records, an open stream's README and current
brief, and whatever those cite, transitively. It is **history** if it is archived, inside a closed
stream, a superseded brief, or cited only by documents of that kind or by `DECISIONS.md`. It is
**unreferenced** if nothing cites it. Live material is what sessions read. History is kept and
reachable, but a session reads its summary instead. Unreferenced material is where a tidy starts,
since nobody is relying on it, though some of it is only uncited because nobody wrote the index.

Three places hold what a session needs instead of the thing itself: a closed stream's README
summary, the `INDEX.md` left in an offloaded run directory, and `DATA_INVENTORY.md`. Each is short
enough to scan, and each says where the full material is and how to get it back.

Git's history is a good archive for small files, which is why archiving is a `git mv` and a removed
file can always be recovered from an earlier commit. It is a poor archive for large data, which
should never have entered it, so large outputs start in an ignored `work/` and, when they are
costly to make again, are copied to backed-up lab storage. The copy is verified file by file against
a manifest kept with it, and the manifest's own digest is committed in `DATA_INVENTORY.md`, so the
record in git can detect a stored copy that was later changed, replaced or lost.

`tools/verify_all.sh` shows the budget warnings from `survey.py --budget` but never fails on them.
They mark when a tidy is due, and the person decides when to run it.

## Proportion

The full apparatus (pre-registered predictions, an independent review, a frozen manifest) is for
decisions that change a claim, an architecture or a large compute allocation. A file rename, a
bookkeeping fix or a syntax check needs a commit message and nothing more. An audit of one earlier
project found that much of its effort went to records that could not distinguish between
hypotheses, while the checks that did change conclusions were a few specific ones: isolating a
component, rebuilding a model explicitly, checking an identity mapping.

Measure a project's progress by the decisions its results changed and the failure classes it found,
not by the number of commits, checks or documents.
