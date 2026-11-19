---
name: adopt-project
description: Bring an existing research folder under the git-tracked record system without losing or rewriting its history. Use when the user has a project that began without DECISIONS.md, briefs, indexes or version control, or whose root has accumulated loose reports and results folders.
---

# Adopt an existing project

Change nothing until step 2 is committed. Do not delete anything at any step.

1. **Survey, read-only.** List the tree with sizes and dates. Identify documents, scripts, inputs,
   outputs, briefs and anything that looks like a decision or a result. Note files over 50 MB.
2. **Commit the starting state.** `git init` if needed, with a `.gitignore` that leaves out large
   regenerable data (each rule with its reason), and commit everything else as found: "Record the
   project as found, before reorganization".
3. **Inventory the data** in `DATA_INVENTORY.md`: what must never be deleted (the only copies,
   irreplaceable inputs), what can be rebuilt and at what cost, and what can go. Ask the user about
   anything you cannot classify.
4. **Add the record files** from the template (`DECISIONS.md`, `OPEN_ITEMS.md`, `FOLDER_LAYOUT.md`,
   `README.md`, `tools/`). `DECISIONS.md` opens at decision 1 with a preamble saying the record
   starts now and where earlier decisions live. Do not back-date reconstructed decisions. Any
   reconstructed document says so at its top.
5. **Propose the reorganization** to the user before moving anything: which files become which
   streams, what goes to `archive/`, and which old paths need a stub because a document cites them.
   Use `git mv` so history follows each file.
6. **Index the outputs** that documents rely on (`tools/make_index.py --draft`), and freeze those a
   document or verifier reads.
7. **Run `tools/verify_all.sh`.** Expect citation failures at first. Fix them by moving, stubbing or
   declaring exceptions, never by editing a document's claims.
8. **Write the first brief** from what is actually on disk, with the strong and tentative lists, and
   commit.
