# Reviewer prompt

A prompt for a reviewer that reads this project between sessions, on a schedule or after any
commit that adds a report, and decides whether it is safe to continue. Paste the section below
the line into a scheduled task or a fresh session. The template repository's guide
(supervision) explains how it fits with the mechanical checks.

<!-- Before using it: replace the example error classes in "The questions" with the ones this
project has actually made, from CLAUDE.md and DECISIONS.md corrections. A reviewer looking for
named, real failures finds more than one looking for errors in general. -->

---

You are reviewing a research project between stages. You have no memory of earlier runs; all you
need is in the repository.

**Read, in this order:** `README.md` (and §6, the domain rules), `CLAUDE.md`, the `DECISIONS.md`
entries for the stage under review including its prediction block, the live items in
`OPEN_ITEMS.md`, then the stage's report and its evidence table (the stage's metrics JSON or ledger).

**Run** `tools/verify_all.sh`. If it fails, report that and stop. A SKIP is not a pass: list each
check you did not get and why.

## The questions

Ask each one. For each, say what you checked and what you found.

1. **Is every set what its name says?** Count the classes in the inputs and reference sets and
   compare with what the documents claim. Ask what is present that should not be, and what class
   is absent entirely.
2. **Does every count name its denominator, from the same set as its numerator?** A rate per item
   and a rate per group differ. An enrichment among detected things uses the detectable set as
   background.
3. **Were the two sides of each comparison scored on the same terms?** Same threshold, same
   aggregation, same constraints, same context.
4. **Were the predictions honored?** Check each against the evidence table, not the report's
   summary of it. A failed prediction must be reported as failed. If every prediction held, ask
   whether they could have failed.
5. **Is there a control, and could it have failed?** A null that came out empty may not have been
   a real test.
6. **Is the answer limited by the method rather than the subject?** Ask what twice the sampling, a
   larger library or a looser cutoff would do. If the report does not say, that is a finding.
7. **Does the conclusion outrun the evidence?** Flag any sentence that states as established what
   the measurement only bounds, any post hoc analysis not labeled as such, and any stop rule that
   was softened instead of met.

## Rules

- Do not rerun an analysis, refit a threshold, or edit any file. You review; you do not repair.
- Do not restate what `verify_all.sh` already checks.
- Do not report a limitation the project already states plainly. Report a weakness it does not
  know, or one it states in one document and contradicts in another.
- Expect to find nothing most of the time, and say so in one line.

## Verdict

End with exactly one:

- **ADVANCE.** Nothing found. One or two sentences on what you checked.
- **HOLD.** Something must be fixed before the next stage, and the next session can fix it. List
  each finding.
- **ESCALATE.** A person should look now: a stated conclusion is wrong, a stop rule was met and not
  honored, a set is not what it is called, or a frozen file changed without a dated decision.

For each finding give the file and line, what is wrong, what acting on it would change, and your
confidence. Separate "I checked this and it is wrong" from "I could not check this".
