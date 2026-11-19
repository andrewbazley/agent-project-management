---
name: review-stage
description: Commission an independent, adversarial review of a stage result, a draft claim or a planned cluster submission in a git-tracked research project, and record the response. Use before writing up a result, before submitting a substantial job, after a stage report lands, or when the user asks for an outside-style, scientific or engineering review.
---

# Review a stage

The reviewer must be independent of the work: a subagent or fresh session that did not do it.

1. **Choose the kind.**
   - **Stage review:** use the project's `SUPERVISION_REVIEWER.md` as the reviewer's prompt, with
     the stage named.
   - **Pre-submission review** of a cluster job or expensive run: the reviewer reads the exact
     script to be submitted, the resource figures it was sized from (measured, not estimated), the
     decision entry, and the rules for the cluster, and returns APPROVE, APPROVE WITH CHANGES or
     REJECT with blocking findings.
   - **Scientific or engineering review** of a claim or codebase: an outside reader who checks
     whether the conclusions follow, or whether the code does what its report says.
2. **Brief the reviewer with the artifacts, not the argument.** Give it file paths, the rules, and
   the claim to test. Do not give it your reasoning or the result you expect. Tell it to re-derive
   anything it checks, to trust no summary, and to look for the smallest wrong input that would
   pass. Use the highest reasoning effort available.
3. **Do not act while it runs.** For a pre-submission review, nothing is submitted until the
   verdict is in.
4. **Save the review as written** in `reviews/YYYY-MM-DD_<kind>_review.md`. Answer each point in
   `reviews/RESPONSES.md`: accepted or not, what changed, what did not and why, what stays open.
5. **Record what it changed.** A verdict that gates a run goes into `DECISIONS.md` before the run.
   Corrections it caused follow the end-session propagation step.
6. Tell the user the verdict, the blocking findings, and what you changed in response.
