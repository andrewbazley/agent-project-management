# Working instructions for this project

These rules govern how work is done here, not what the project is about. Each one came out of a
mistake made in an earlier project and names the failure it exists to prevent, so that a later
session can tell a rule with a reason from a rule kept by habit. The rules specific to this project
are in `README.md` §6. A conflict between the two is settled by a dated entry in `DECISIONS.md`.

The project runs as a chain of sessions. Each one inherits the last one's written state, does a
piece of work, and writes the brief for the next. No session is expected to remember anything, so
anything a later session needs has to be on disk and committed.

---

## 1. Before claiming anything is new

**Search for prior work before building, not after.** An earlier project reconstructed a published
result in the same system as the original paper and did not find out until an unrelated prior-art
search turned the paper up. Everything built in between was still correct, but it was a
replication described as a discovery, and the paper that got there first went uncited.

1. For any result that would be a contribution, search for it before the work starts and again
   before it is written up. Search the method and the system separately, and search for the
   method applied to a different system, since that is the form a prior claim usually takes.
2. Record each search: what was searched, where, with which terms, and what came back. A search
   that found nothing is a result and belongs in the record, because the next session will
   otherwise repeat it.
3. When a prior paper covers the result, say so in the document that makes the claim, in the same
   paragraph. Reframing a finding as a replication costs little when done early and costs the
   whole claim when done late.
4. Never cite a paper, accession, identifier or coordinate that has not been checked against the
   source. Anything unverifiable goes in the open-items file marked unverified.

## 2. Before trusting a measurement

**Check more than one source, and prefer sources that could disagree.** A reference set used in an
earlier project for months turned out to be missing an entire class of competitor, which nothing
in the pipeline could have revealed. The error surfaced through a single retraction and only then did a systematic
scan find the other thirteen cases.

1. Ask what the reference set or input does not contain. Count its classes and compare the counts
   with the source it was built from. An absent class is invisible to every downstream check.
2. Confirm an important result against a second, independently constructed source, chosen so that
   disagreement is possible. Two sources that agree are worth far more when one is several times
   larger than the other and built differently. If they disagree, the disagreement is the finding.
3. Validate the arithmetic of a method against the tool that implements it, rather than assuming
   a shared convention. Recomputing a derived quantity for tens of thousands of records and
   comparing it against the tool's own value takes minutes and either confirms the convention or
   finds an offset.
4. Treat coordinate, offset, frame and alignment handling as a likely source of silent error. One
   statistic was computed on projected, gap-filtered columns, which changed what it measured
   without changing what it was called. Recompute any such statistic in the native coordinate
   system of the data and compare.
5. State the range over which a method works. The same statistic degrades with input length until
   it fails completely, so every figure drawn from it describes short inputs because of the
   method rather than because of the subject. A method's failure mode belongs beside its result.
6. Treat an exact tie as undecided. Which of two equally scoring candidates a tool reports is
   arbitrary, so give ties their own category and count them rather than letting the tool's
   arbitrary choice become a result.
7. Where two inputs cannot be distinguished by the instrument or method in principle, give that
   ambiguity its own category too, instead of resolving it silently in favor of the preferred
   answer.
8. **Nothing may donate to itself.** A reference distribution, library, threshold or null panel
   is never built from the items it will be tested against. Record in the decision what was held
   out from what.
9. **Name the context a number was computed in.** A score is not a claim until it says what was
   present when it was measured: which inputs, which components, which state, which version of
   the reference. One project reached a confident wrong answer twice, in opposite directions,
   because a score silently included a component nobody had asked about.

## 3. Numbers discipline

Most of the errors in earlier projects were arithmetic or bookkeeping rather than conceptual.

1. **Freeze the rule before taking the count.** Write down what will be counted, what the classes
   are, what the control is and what threshold applies, then count. A count whose rule was chosen
   after seeing the data is not evidence. An analysis chosen after the data were seen may still
   be reported, labeled post hoc wherever it appears.
2. **One threshold per comparison.** One enrichment figure compared a count taken at one
   cutoff with a count taken at another. Both counts were correct and the comparison was not.
   State the cutoff beside every count.
3. **Never report an unfiltered count as a result.** Two unfiltered totals were published as a
   ratio; at a stated cutoff the same comparison came out three times larger.
4. **Name the denominator and check it belongs to the same set as the numerator.** Several errors
   were a count from a looser set carried into a document about a stricter one, including a
   figure that differed by a third once recomputed on the right set.
5. **For any enrichment among detected things, the background is the set that could have been
   detected**, not everything that exists. The same wrong-background error happened three times
   before it became a rule.
6. **Report error rates by class against a matched control, never globally.** A global rate hides
   exactly the class a project cares about.
7. **Zero is not absence.** A zero count carries wide uncertainty, so state the interval. One
   claim of "none of N" was false once recounted, and the arms that found no control hits
   were consistent with having missed about three.
8. **Two numbers that are equal are not the same number.** Two different quantities were printed
   as the same value twenty-four lines apart, both individually correct, and no audit would have
   caught it. When a value recurs, say what set it is over.
9. **Measure a resource cost, do not predict it.** A memory estimate derived from the wrong
   proportionality authorized a run that paged for an hour and produced nothing. Measure the
   driving quantity on a small case, then size the job. When an estimate is falsified, record that
   it was falsified and do not replace it with a second estimate; record the quantity as unmeasured.
10. **Never report a check that was not performed.** One column read as agreement on every row
    because the comparison it summarized had never run. A field for a skipped check is blank, and
    the verification script asserts that it is blank.
11. **Count every attempt in the denominator.** Timeouts, crashes and inputs that failed to build
    are attempts. A pass rate over only the attempts that finished is inflated.

## 4. Verification

1. Every number asserted in a document is re-derived from the primary data by a script, not from
   another document. One evidence table is the single source, and documents read from it.
2. Each piece of work gets a verification script that re-derives its numbers and checks its
   internal invariants. Write the falsifier before the result is seen: state what outcome would
   mean the work is untrustworthy, and have the script test for it.
3. All verification scripts run from one command, and that command runs before and after any
   change to a document or a table. Report the count of checks, failures and skips.
4. Where a prediction can be made before a run, write it down first and have the verifier compare
   the prediction against the outcome. One prediction was wrong by five, and that was
   more informative than a correct one would have been, because it exposed a set-mixing error in
   the reasoning.
5. Invariants are better checks than expected values. A sum that must equal a known total, a set
   equality, or a precedence rule that must hold on every row will catch errors that an expected
   number will not.
6. **A missing input is never a passed check.** Where a verifier cannot perform a check, it says
   so by name, with the reason, and does not count it as a pass. One verifier reported a clean
   pass on a loop that had iterated zero times.
7. **Calibrate a check before trusting it.** Break the thing it guards, on a copy, and confirm
   that it fails.

## 5. Keeping a decision record

Decisions are written when they are made and read only when needed. The record exists so that a
future session can tell what was decided deliberately from what happened by accident.

1. One file holds the decisions, numbered in sequence, each with a date, the question, the
   decision, the reason, and the falsifier if one applies.
2. Write the entry **before** the work it governs. An entry written after the result is a
   rationalization of it. Commit the entry before the run, so the commit order shows which came
   first.
3. A sub-entry of an existing decision takes a letter suffix and one more heading level. A new
   top-level decision takes the next number at the top level. Keep the heading levels consistent,
   because the file is read by grep more often than by eye.
4. A decision that turns out to be wrong gets a correction as a new dated sub-entry. The original
   entry stays exactly as written. Two corrections in an earlier project were more useful than the
   decisions they corrected, because they record a reasoning error and not only a wrong number.
5. Record failures with the same prominence as successes, including what was attempted, what the
   evidence of failure was, what it costs, and what it does not cost. A failure that is written
   up properly stops the next session from repeating it.
6. Three failed attempts at the same thing is the limit. Record the attempts in the open-items
   file with a closing condition and move on.

## 6. Editing documents

1. **Corrections go in place, dated, with the original text left standing.** Never quietly
   revise. A reader needs to see what was claimed and what it became, and the project's own
   history of corrections is part of what makes the current numbers believable.
2. **Never use a global find-and-replace on prose.** Renumbering a list in one file once changed
   a percentage in an unrelated paragraph and broke a second list, because the pattern matched
   text that had nothing to do with the edit. Replace against unique anchors, assert that each
   anchor occurs exactly once, and check the file afterwards for collateral changes.
3. **When a finding withdraws or changes the content of another document, update that document in
   the same session.** Two documents once continued to present a withdrawn item as their
   best-supported result, with no reference to the work that withdrew it, because the work was
   written up somewhere else. A finding is not propagated until every document that depends on it
   says so.
4. **Delete a stale warning rather than leaving it.** One index carried a do-not-circulate
   warning about an error that had been fixed, which would have told a reader the document still
   contained it. Correct the warning with a dated replacement.
5. **Never quote a result the project has itself retracted.** One retracted internal value was
   carried forward into a later document. When something is retracted, search for every place it
   appears.
6. Rebuild derived outputs, such as rendered documents, in the same session as the source edit,
   and check that the new text is present in the rebuilt file. A correction that exists only in
   the source is not in the thing people read.
7. **Keep a current reading on top.** Corrections left in place make a long document hard to read.
   A report or index that has been corrected carries, near its top, a short dated note saying
   which of its claims still stand, which changed, and where the change is recorded.

## 7. Files, labeling and archiving

1. **Every output directory has an index** that says what each file is and which script made it.
   One directory accumulated thirty-seven files with no index. When writing one, derive the
   script-to-output mapping by searching the scripts for their own output paths rather than from
   memory.
2. **Every script carries a docstring** saying what it computes, which rule or decision governs
   it, what it reads and what it writes.
3. **Every table carries its provenance**: a header comment naming the script, the date, and the
   rule it implements, or that information in the directory index.
4. **Outputs that a document or a verifier reads are frozen.** Never overwrite them. New work
   writes new files in a new dated directory, and the verifier asserts that the frozen
   directories have not been modified.
5. **Mark anything irreplaceable as such, in the inventory, next to the thing that would delete
   it.** One inventory suggested a delete pattern that would have removed output no longer
   reproducible in reasonable time and would have broken two verification scripts. Say which
   outputs are the only copy and what re-creating them would cost.
6. **Log any large download before starting it**, with the source and the size, and stop before
   writing more than the agreed limit.
   This applies to a machine with finite disk. The rule exists so that a runaway fetch cannot
   fill the volume holding the only copy of something irreplaceable. Where storage is effectively
   unbounded and separate from that copy, such as a lab allocation on a cluster, a size ceiling
   buys nothing; state instead *where* the data will live, respect whatever quota is actually
   enforced, and never write in other users' directories. The project's `README.md` §6 names the
   paths and quotas.
7. **Archive rather than delete.** Superseded briefs, prior builds and resolved registers go to a
   dated archive directory. When an archived file is still referenced by documents, leave a stub
   in its place naming the new location, so the citations keep resolving.
8. **Keep working files out of the project.** Intermediate results and scratch scripts go in a
   scratch directory. Anything that belongs to the record goes in the project with a name that
   says what it is and a date where the date matters.
9. **Check that every path cited in a document exists** before the session ends. A cited path
   that does not resolve is the same class of error as a fabricated citation.

## 8. Writing the next session's prompt

Every session ends by writing the brief for the next one. The brief is how the project keeps
direction across sessions, so write it as an instruction to someone who knows nothing rather than
as a summary of what happened.

The brief contains, in this order:

1. **What to read first**, in order, and the standing rules.
2. **Where the work stands**, in a few sentences.
3. **Which results are strong and which are tentative**, as two explicit lists. A result is
   strong when it rests on a measurement with a matched control and a falsifier that was written
   down first. Everything else is tentative, and say why for each: under-powered, confounded,
   resting on a design that cannot settle it, or not yet replicated. This list is the most useful
   part of the brief, because a later session will otherwise treat every sentence in a document as
   equally load-bearing.
4. **Open questions and inconsistencies**, including numbers that are unmeasured rather than
   measured, estimates known to be wrong, stale cross-references, and any place where two parts of
   the record disagree.
5. **What is cheap and overdue.** Items that take minutes and have been deferred repeatedly
   should be named and marked as not requiring the session's main effort.
6. **What matters less.** Say explicitly what not to spend the session on, and why. A brief that
   lists only priorities gets read as a list of everything.
7. **What could be augmented**: the parts of the work where more data, more power or a better
   control would change the answer, each phrased as a question that a specific result would settle.
8. **What success looks like** for the session.

Keep the previous brief if it still holds content the next session needs, and annotate it with a
dated note rather than deleting it. One brief was superseded as a work order while its list
of untested ideas remained the best such list in the project, and two figures in that list had
since been corrected elsewhere, which the annotation records.

## 9. Scope: finish the stream you were given

**Do not add a new analysis stream.** A session works on the lines of investigation its brief
names, and nothing else. This is the rule most often tempting to break, because a session that is
going well generates good questions, and acting on one of them immediately feels like progress.
It is not progress. It converts a finishable piece of work into two unfinished ones, and the
second one is the one that gets written up badly.

1. A question raised mid-session goes to the open-items file with a closing condition, or to the
   next session's brief. It does not go into this session's work.
2. A new stream is opened deliberately, by the brief, with its own rule frozen in advance and its
   own falsifier. It is never opened as a detour.
3. Finishing means the work is verified, its numbers are re-derived by a script, its outputs are
   indexed, and the documents that depend on it say so. A stream left at "the analysis ran" is not
   finished and will cost more to pick up than it saved.
4. Work that is genuinely separate gets its own self-contained study with its own deliverable,
   planned as such, rather than being folded into whatever is in flight.
5. When a brief and a good idea conflict, the brief wins for this session and the idea gets
   written down. The record of untested ideas is more valuable than any one of them acted on out
   of turn, because it is what lets a later session choose between them.

## 10. When to stop and ask

Ask rather than guess when the answer changes what gets built: an ambiguous scope, a choice
between designs with different costs, or anything that would consume a shared resource. Ask for
facts about an environment rather than inventing them, including machine limits, available
software and whether a resource can be reached.

Do not change a position under pressure alone. Change it on a new measurement or a corrected
calculation, and equally, do not defend a position once the calculation says otherwise.

## 11. Subagents and independent review

1. **One writer.** The orchestrating session owns the decision record, the open-items file, the
   README, every index, report and brief. No subagent writes them.
2. **Separate outputs.** Each subagent writes only into its own new dated directory and hands back
   numbers and paths. A subagent that needs a decision asks for it.
3. **Brief with the goal, the files and what done looks like, never with the hypothesis.** A
   subagent given a hypothesis tends to return it confirmed.
4. **Review anything consequential independently** before it is acted on: a result about to be
   written up, a cluster submission, a change of architecture. Give the reviewer the artifacts and
   the claim, not the reasoning, and tell it to re-derive what it checks. One adversarial reviewer
   at high effort has found more than several parallel helpers. Answer each review point by point,
   and record a verdict that gates a run in the decision record before the run.

## 12. Proportion

The full apparatus (rule frozen in advance, predictions, falsifier, independent review, frozen
manifest) is for decisions that change a claim, an architecture or a large compute allocation. A
rename, a bookkeeping fix or a syntax check needs a commit message and nothing more. Measure
progress by the decisions results changed and the failure classes found, not by the number of
commits, checks or documents.
