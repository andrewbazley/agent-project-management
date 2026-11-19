# <Project title>

<!-- One paragraph: what the project makes or measures, which streams exist and which one is
current. Point to FOLDER_LAYOUT.md for what is where. Say whether any of it is wet-lab work or all
of it is computational. -->

**The claim, and the nearest prior work, in the same paragraph.**
<!-- State the contribution as narrowly as the evidence allows, then the closest published work
and how this differs from it. Link the search record (what was searched, where, with which
terms, including searches that found nothing). Amend this paragraph in place, dated, whenever a
search narrows the claim. -->

## Where the work stands

<!-- A few sentences, dated, rewritten by the session that ends. Which stream is active, the last
verified result, the current brief (PROMPT_NN), and the verify_all.sh summary line. Anything
longer belongs in the brief. -->

## Running it

<!-- The environment (exact versions, where it lives, how to build it), how to regenerate any
input that is not in the repository, and the one command that verifies everything:
`tools/verify_all.sh`. A fresh clone without large inputs must still verify, with the checks that
need those inputs reported as SKIP. -->

## 1. What this project is for

<!-- The question and the deliverable. Amend in place when the goal changes, citing the decision. -->

## 2. What can and cannot be established here

<!-- What the methods can measure, and what they cannot. This defines what counts as success, and
it stops a later session from reporting a proxy as the thing itself. -->

## 3. How a session works

The project runs as a chain of sessions. Each inherits the last one's written state from the
current brief, does the work that brief names, and writes the next brief. `CLAUDE.md` holds the
working rules and overrides habit.

## 4. Records

| file | holds |
|---|---|
| `CLAUDE.md` | the general working rules; binding on every session |
| `DECISIONS.md` | numbered decisions and predictions, each written before the work it governs |
| `OPEN_ITEMS.md` | questions raised and deliberately not acted on, each with a closing condition |
| `FOLDER_LAYOUT.md` | what is where, and why streams are kept apart |
| `<stream>/PROMPT_NN_*.md` | the brief each session works from; the highest number is current |
| `<stream>/results/<dated>/INDEX.md` | every file in an output directory and the script that made it |
| `reviews/` | independent reviews and the project's responses to them |

## 5. Verification

`tools/verify_all.sh` runs every stream verifier and the whole-tree checks in one command and
exits non-zero if any fails or reports a check it could not perform as passed. `tools/README.md`
lists what each check asserts. Run it before and after any change to a document or a table.

## 6. Domain-specific rules

<!-- Rules that apply to this project only, in addition to CLAUDE.md. A conflict between the two
is settled by a dated entry in DECISIONS.md, not by whichever was read last. Number them; other documents cite them as "README §6.N".
Typical entries: which specification and thresholds are frozen and how a new version is made;
which stage licenses which; what is held out from what; where large data and cluster outputs
live; which machine-specific limits apply. Give each rule its reason. -->

1. <rule>. <reason>.
