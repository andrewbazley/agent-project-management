---
name: end-session
description: Close a working session on a git-tracked research project. Verifies, indexes and freezes outputs, propagates findings to every dependent document, checks cited paths, follows up on jobs, writes the next brief and commits. Use when the user says to wrap up, close out, hand off or write the next prompt, or before a session ends after substantive work.
---

# End a session

Do these in order. A stream left at "the analysis ran" is not finished.

1. **Verify.** Run `tools/verify_all.sh`. Fix failures or record them; never report a skip as a pass.
2. **Promote, index and freeze.** Outputs a document now cites move from `work/` into a dated
   results directory. Every new output directory has an `INDEX.md` (`tools/make_index.py
   --draft`), and outputs a document or verifier reads have a manifest
   (`tools/check_frozen.py --write`). Large or costly outputs left in `work/` get a row in
   `DATA_INVENTORY.md` saying what they are and what regenerating them would cost.
3. **Propagate.** For each finding, correction or retraction this session made, search the
   repository for every document that states the old value or depends on it, and update each with
   a dated amendment. Add a "current reading" note to any report whose claims changed. Rebuild any
   rendered output and confirm the new text is in it.
4. **Record.** Decisions and corrections are in `DECISIONS.md`. Deferred questions are in
   `OPEN_ITEMS.md` with closing conditions. Failures are recorded as prominently as successes.
5. **Jobs.** Check every job this session submitted. Cancel any that are stuck or no longer needed.
   List any still running in `hpc/JOBS.md` and in the brief, with id, purpose, expected end and
   output path.
6. **Write the next brief**, `PROMPT_<NN+1>_<topic>.md`, from the template sections, for a reader
   who knows nothing. The strong and tentative lists matter most. Annotate the previous brief with
   a dated note saying it is superseded and what it still holds, or move it to `archive/`. If
   anything the session found makes an earlier document outdated or wrong, say so where it will
   be read (`CLAUDE.md` 13.3).
7. **Update** the status lines in `README.md` and the stream `README.md`.
8. **Run `tools/verify_all.sh` again**, then commit with a message that states what is now true.
   Push if the project has a remote.
9. **Report to the user:** what was established, what was not, the verify summary line, any running
   jobs, and the name of the next brief.
