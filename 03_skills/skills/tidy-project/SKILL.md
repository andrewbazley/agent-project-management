---
name: tidy-project
description: Tidy a git-tracked research project after it has grown. Surveys which files the current documents still lead to, proposes what to archive, close, offload to lab storage or remove, and carries out only what the person approves, leaving a summary and a recorded location for everything moved. Also closes or reopens a stream. Use at a milestone, when verify_all.sh shows budget warnings, when the user asks to clean up, archive, shrink or reorganize a project, or to close, shelve, revive or reopen a line of work.
---

# Tidy a project

The rules are `CLAUDE.md` §13. Two of them shape every step here. Anything moved stays reachable
through a summary, a recorded location and a way back. Nothing is moved or removed until the person
approves it.

## 1. Survey (read-only)

1. `git status` must be clean; commit or set aside other work first. Run `tools/verify_all.sh` and
   note its failures; a tidy does not hide them.
2. `python3 tools/survey.py` for the totals, the reading path, the largest unreferenced items and
   what git ignores; `--list unreferenced` and `--list history` for the full lists; `--reading` for
   each live document's distance from an entry point and what leads there; `--budget` for the
   warnings. A project that does not have the template's tools can be surveyed with them from
   elsewhere: `python3 <template>/tools/survey.py --root <project>`.
   If the project predates the template (no numbered streams, briefs not named `PROMPT_NN`), say
   which documents are the current brief and entry points, since the survey infers them from
   names, and propose adopting it (`adopt-project`) as a separate step rather than inside the tidy.
3. Read only what classifying needs: the root and stream READMEs, `FOLDER_LAYOUT.md`,
   `DATA_INVENTORY.md`, the `DECISIONS.md` index, the current briefs and the `INDEX.md` of each
   candidate. Do not read archived or closed material to judge it; its summary or index is enough,
   and where there is none, that is a finding.
4. For each candidate, find what it would cost to make again: the producing script in its index,
   the download log entry, the job record's elapsed time. If you cannot tell, write "unknown" and
   ask. Do not guess that something is cheap.

## 2. Propose

Write the proposal to `archive/TIDY_<YYYY-MM-DD>.md` (it becomes the tidy's record) and show it to
the person as a table, largest first:

| item | size | state | proposed action | why | cost to regenerate |
|---|---|---|---|---|---|

The actions, from least to most consequential:

- **keep**: still in the reading path, or the person's call.
- **archive**: move to the folder's `archive/` with `git mv`, leaving a stub at any path a live
  document cites. For superseded briefs, old builds, resolved registers and one-off notes.
- **summarize**: the item stays where it is, but the document that leads to it gains a dated line
  saying it is outdated or wrong and what replaced it (`CLAUDE.md` 13.3). For material whose only
  problem is that sessions keep reading it.
- **shorten an entry point**: when an entry point cites many documents directly (the survey's
  fan-out warning), rewrite it to cite the few that are current, with one line pointing to an
  index for the rest. Everything else leaves the reading path without a file moving or a citation
  breaking. In a project whose README links every report, this does more than any move.
- **close stream**: see section 4.
- **offload**: copy to the lab storage named in `README.md` §6 with `tools/offload.py`, then
  remove the local copy (section 3). For anything that took hours to make or download.
- **remove**: only for output that regenerates within about an hour from committed code and
  available inputs, that nothing live cites, and that is not an only copy. Its `INDEX.md` stays.
- **ask**: anything you could not classify.

Never propose removing an only copy, anything listed under "Only copies" in `DATA_INVENTORY.md`, or
anything whose cost is unknown. Say what the tidy would not touch and why. Then stop and wait for
approval, row by row if the person prefers; an approval covers the rows it names.

## 3. Act on the approved rows

1. **Tag the starting point:** `git tag tidy-<YYYY-MM-DD>-before`.
2. **Offload** each approved set, one at a time:
   `python3 tools/offload.py copy <path> --to <base from README §6> --cost "<hours, with the scripts>"`
   then `python3 tools/offload.py prune <path>` to list what would go, and
   `python3 tools/offload.py prune <path> --yes`. Prune re-verifies the stored copy and removes only
   files that match it, keeping documents, indexes and small tables. If the storage is not mounted
   here, stop and tell the person; never offload to this machine's own disk. Data on a cluster is
   offloaded from the cluster, under its rules for data transfer. Offloading runs where the data
   is: a clone from GitHub can be surveyed and its documents tidied, but it does not hold what git
   ignores.
3. **Archive** with `git mv`, so history follows each file. Where a document outside `archive/`
   still cites the old path, leave a stub there: for a Markdown file, a one-line file at the old
   path naming the new location and the date; for any other file, a row in
   `tools/citation_exceptions.txt` giving the old path and "moved to <new path> on <date>". Never
   edit the citing document's claims to make the citation go away.
4. **Remove** approved regenerable output with `git rm` (or `rm` if git ignores it), and add a
   dated line to its `INDEX.md` or to `DATA_INVENTORY.md` saying how to regenerate it.
5. **Record:** add a dated note to `FOLDER_LAYOUT.md` for each directory moved or stream closed;
   update `README.md` "Where the work stands" if the current work changed; complete
   `archive/TIDY_<YYYY-MM-DD>.md` with what was done, what was declined, the before-and-after totals
   from `survey.py`, and the tag.
6. **Verify:** `tools/verify_all.sh` must pass with no new failures. Then commit once: "Tidy:
   archive N files, offload M sets (X GB) to lab storage, close stream NN".

## 4. Closing and reopening a stream

A stream is closed when it stopped producing work that the project's current question needs: it
answered its question, it was superseded, or it failed. Closing keeps it as a summary a session can
read in a minute.

**Close.** With the person's approval:

1. Write a decision closing it (`record-decision`), and mark the decisions it governed "closed with
   stream NN" in the `DECISIONS.md` index.
2. Replace the status line of the stream's `README.md` with the closing block from the template's
   stream README, filled in from the stream's reports and briefs: what it asked; what it found, with
   numbers; what is reusable, with paths or inventory rows; what must not be reused and where that
   is recorded; and what would justify reopening it. This block is what later sessions read, so it
   has to stand on its own.
3. Mark it closed in the `FOLDER_LAYOUT.md` stream table, with its one-line summary.
4. Offload or remove its bulky outputs by sections 2 and 3. Leave its documents, indexes, scripts
   and specifications in place, so citations into it still resolve.

**Reopen.** Write a decision saying why, citing the result or question that justifies it. Restore
any data it needs (`python3 tools/offload.py restore <path> --yes`). Replace the closing line with a
dated status line and keep the summary beneath it. Mark the stream open in `FOLDER_LAYOUT.md` and
write its next brief.

## 5. Report

Tell the person what moved and where, the before-and-after totals, anything declined or left for
them, and any offloaded set whose storage could not be checked from here.
