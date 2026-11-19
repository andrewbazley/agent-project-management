# results/

One directory per run, named `<stage>_<YYYYMMDD>/`. A run never writes into a directory that a
document or verifier already reads; it makes a new one. Copy the two templates below into each new
directory.

## INDEX.md

Derive the "made by" column by searching the scripts for their own output paths
(`tools/make_index.py --draft <dir>`), not from memory.

```markdown
# <stage>, YYYY-MM-DD

<One line: what this run did, under which decision, and the command that reproduces it.>

| file | made by | what it is |
|---|---|---|
| `metrics.json` | `tools/<script>.py` | **the evidence table.** Every number the report asserts |
| `REPORT.md` | `tools/<script>.py` | **deliverable.** Generated from `metrics.json`; computes nothing |
| `manifest.json` | `tools/check_frozen.py` | SHA-256 digests of the frozen files below |

**Frozen.** <files a document or verifier reads; do not overwrite>
**Replaceable.** <what regenerates, from what, and how long it takes>
**Only copy.** <anything that cannot be regenerated in reasonable time, or "nothing">
```

## REPORT.md

```markdown
# <stage> report, YYYY-MM-DD

**Current reading.** <Added when anything below is corrected: which claims stand, which changed,
and the decision that changed them.>

## Question
<What this stage asks, and the decision entry that froze its rule.>

## Predictions
| # | prediction | outcome | held? |
|---|---|---|---|

## Result
<Each number with its denominator, threshold and the set it is over. Controls beside results.>

## Limits
<Where the method stops working, what was skipped and why, what is post hoc.>

## What this licenses
<The next stage this result permits, or the stop rule it meets.>
```
