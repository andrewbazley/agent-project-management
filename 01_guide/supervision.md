# Supervision, review and subagents

How a project checks itself, how independent reviewers are used, and how several agents work on
one record without corrupting it.

## Gate, reviewer, escalation

Once sessions run unattended, reviewing each run by hand becomes the slowest part of the chain. The
answer is three layers with a clear boundary between them.

**The gate** is mechanical. It runs `tools/verify_all.sh` and the invariants a verifier cannot
check about itself: frozen files unchanged, the prediction block unchanged since it was committed,
the number of skipped checks not risen, every output directory indexed, every cited path resolving.
It is fast and exact, and it catches nothing it was not told to look for.

**The reviewer** is a fresh session with no memory of the work, running
`SUPERVISION_REVIEWER.md`. It does not recompute. It looks for the error classes no check can be
written for in advance, because they live in the reasoning: a set that is not what it is called, a
denominator that is not what the sentence implies, an answer that is an artifact of the method's
capacity, a replication described as a discovery. It ends with ADVANCE, HOLD or ESCALATE.

**The escalation policy** is written before the run and decides what reaches a person. A failed
prediction always escalates, because it is usually the most informative thing a run produces.

The supervisor may advance or stop. It never edits documents, reruns a stage for a different
answer, widens a threshold, or opens a stream.

Two traps:

- **Saturation.** A check that is already failing cannot announce a new failure by turning red.
  Clear standing failures before relying on the gate.
- **Allowlist growth.** A verifier that compares report numbers against a list of permitted values
  can be made to pass by adding to the list. Count the entries and fail if the count grows.

Calibrate before trusting the gate: inject each error the project has actually made into a copy,
and record which ones the gate catches.

## Independent reviews

Use a reviewer that did not do the work for anything consequential: a result about to be written
up, a cluster submission, a change of architecture. In earlier projects a single adversarial
reviewer at high effort found more than several parallel helpers. It caught a missing log
directory that would have killed a job silently, a gate that would have fired on a healthy run, and
a claim that inverted once re-derived.

- Give the reviewer the artifact itself (files, coordinates, scripts, the job script as it will be
  submitted), the rules, and the claim. Do not give it your reasoning or your hypothesis.
- Tell it not to take any summary on trust and to re-derive what it checks.
- Ask for the smallest wrong input that would pass.
- Save the review as written in `reviews/`, answer it point by point in `reviews/RESPONSES.md`, and
  record any verdict that gates a run in `DECISIONS.md` before the run starts.

## Several agents on one record

- **One writer.** The orchestrating session owns every record file: `DECISIONS.md`,
  `OPEN_ITEMS.md`, `README.md`, every `INDEX.md`, every report and brief. No subagent writes them.
- **Separate outputs.** Each subagent writes only into its own new dated directory and hands back
  numbers and paths. The orchestrator writes them into the record.
- **Read anything, decide nothing.** Subagents may read the whole repository. A subagent that needs
  a decision asks for it.
- **Brief with the goal, the files and what done looks like.** A subagent given a hypothesis tends
  to return it confirmed.
- **Independent parts start together.** Dependent ones start as soon as their input exists, not
  when every parallel arm finishes.
- **Say which outputs are frozen** at the top of the brief, so no subagent overwrites one.

## Unattended runs

A scheduled task starts a fresh session each time it fires. It can reach a laptop only if the task
requires the local machine and the machine is awake, and a background job on a laptop may need
explicit file-system permission to read a project folder. Work that must survive the laptop
sleeping has to be reachable elsewhere, which usually means a repository and a cloud session that
clones it. A collector that fetches finished cluster jobs should commit only after the pipeline
verifies, and should do nothing when nothing has finished, so that the history does not fill with
empty commits.
