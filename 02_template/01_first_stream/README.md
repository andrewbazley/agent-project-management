# <Stream name>

<!-- The entry point for this stream. It says what is here, which results are current, and what
is open. It points to reports and does not repeat them. Update the status line at the end of
every session. -->

**Status, YYYY-MM-DD.** <One or two sentences: what is done, what is running, what is next. The
current brief is `PROMPT_NN_<topic>.md`.>

<!-- When the stream is closed, replace the status line with the block below, keep the rest of
this file, and mark the stream closed in FOLDER_LAYOUT.md. Sessions read this block instead of the
stream, so it has to be enough to decide whether to reopen it or reuse a part of it, and it says
what is wrong so that nobody reads the old reports to find out.

**Closed YYYY-MM-DD** by decision N. <One line: why the stream stopped.>

## Summary for a later reader

- **Asked:** <the question, and the decision that froze its rule>
- **Found:** <the results, with numbers, denominators and thresholds; which were strong and which
  tentative>
- **Reusable:** <scripts, specifications, data and outputs worth taking into other work, each with
  its path or its row in DATA_INVENTORY.md>
- **Do not reuse:** <what turned out wrong or superseded, and where that is recorded>
- **To reopen:** <what result or question would justify it, and what to restore first>
-->

## Reading order

1. <the report or summary to read first, and why>
2. <the next one>

## Map

| stage | code | verifier | outputs | report |
|---|---|---|---|---|
| <stage> | `tools/<script>.py` | `tools/verify_<stage>.py` | `results/<stage>_<YYYYMMDD>/` | `results/<stage>_<YYYYMMDD>/REPORT.md` |

Frozen specifications are indexed in `spec/INDEX.md`. Run directories follow `results/README.md`;
inputs fetched are logged in `data/DOWNLOAD_LOG.md`,
and cluster submissions in `hpc/JOBS.md`. Working output goes to the stream's work/ folder, which
git ignores.

## What is current

<!-- Which reports or figures have been corrected or superseded, with the decision that did it.
A reader who opens an old report from here should know whether its claims still stand. -->
