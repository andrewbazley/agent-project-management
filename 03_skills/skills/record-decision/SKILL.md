---
name: record-decision
description: Write a decision, a prediction block or a correction into a project's DECISIONS.md in the standard numbered format, and commit it before the work it governs. Use before running any analysis whose rule, threshold, control or expected outcome should be fixed in advance, and whenever an earlier decision turns out to be wrong.
---

# Record a decision

1. **Find the next number.** `grep -n '^## [0-9]' DECISIONS.md | tail -1` for a new decision;
   `grep -n '^### <N>[a-z]' DECISIONS.md` for the next letter of a sub-entry. Keep heading levels
   exactly as the file's preamble states.
2. **Choose the kind:**
   - **Decision** (`## N. Title`): date, question, decision, reason, falsifier. For a count or
     comparison, freeze the rule first: what is counted, the classes, the control, the threshold,
     the denominator, and what is held out from what.
   - **Prediction block** (`### Na. Predictions for <stage>, written before it was run`): a
     numbered table of each expected outcome with its tolerance and the outcome that would falsify
     it. Make them demanding enough that some could fail.
   - **Correction** (`### Nb. Correction, YYYY-MM-DD: <what was wrong>`): what the original got
     wrong, the reasoning error behind it, what changes, and which documents were updated. The
     original entry is not edited.
3. **Match the weight to the stakes.** Full rule, falsifier and predictions for anything that
   changes a claim, an architecture or a large compute allocation. One short entry for a routine
   choice. Bookkeeping needs a commit message, not an entry.
4. **Update the index** at the top of `DECISIONS.md`: a row for a new decision, and a new status
   for any decision this entry amends, corrects or supersedes.
5. **Commit the entry by itself, before the run**, so the commit order shows it came first:
   "Decision N: <one-line summary>, written before <stage> runs".
6. Cite the entry by number in the script docstring, the output `INDEX.md` and the report.
