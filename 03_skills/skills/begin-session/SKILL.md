---
name: begin-session
description: Start a working session on a project kept as a git-tracked record, by reading the current brief and its named entries, checking the tree verifies, and confirming scope before any work. Use at the start of any session that continues such a project, or when the user says to pick up, resume or continue it.
---

# Begin a session

1. **Find the current brief:** the highest-numbered `PROMPT_NN_*.md` in the active stream named in
   `README.md` "Where the work stands". If a later block quote headed "Amended" exists, it overrides
   the sections below it.
2. **Read in the brief's order.** `CLAUDE.md` in full, `README.md` §6, then only the `DECISIONS.md`
   entries and `OPEN_ITEMS.md` items the brief names. Do not read whole long record files.
3. **Check the state.** `git status` and `git log --oneline -15` (uncommitted changes or a commit
   newer than the brief mean someone worked since it was written). Run `tools/verify_all.sh` and
   note failures and skips before changing anything; they are not this session's to hide.
4. **Check anything still running** that the brief lists (cluster jobs, background runs) and record
   its state.
5. **State the plan back to the user in a few lines:** the work the brief names, what is out of
   scope, the decision entries to write before running anything, and anything in step 3 or 4 that
   changes the plan. Ask before proceeding if the brief and the tree disagree.
6. Questions that come up during the work go to `OPEN_ITEMS.md` or the next brief, not into this
   session's work.
