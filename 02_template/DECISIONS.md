# Decision record

One file, numbered in sequence. Each entry carries a date, the question, the decision, the reason,
and the falsifier where one applies. Entries are written and committed **before** the work they
govern. A wrong entry gets a dated sub-entry and the original text stays as written.

Headings are fixed so the file can be read by grep: `## N. Title` for a decision, `### Na. Title`
for a sub-entry, correction or prediction block. Sessions read the entries their brief names, not
the whole file.

<!-- If the project existed before this file, say so here: when the record opens, and where the
earlier decisions live (script docstrings, old notes), and add the gap to OPEN_ITEMS.md. -->

---

## 1. <What the first session is licensed to do>

**Date** YYYY-MM-DD
**Question** <the question this decision settles>

**Decision** <what will be done, and what is out of scope>

**Reason** <why; cite the brief, the plan or an earlier decision>

**Falsifier** <the observation that would show this decision was wrong>

---

<!-- Formats for the other kinds of entry. Delete this comment block once the first of each exists.

### 1a. Predictions for <stage>, written before it was run

| # | prediction | falsified if |
|---|---|---|
| P1 | <expected outcome, with number and tolerance> | <outcome that would falsify it> |

The verifier for this stage reads this table and reports each prediction as held or falsified.

### 1b. Correction, YYYY-MM-DD: <what was wrong, in one line>

<What the entry above got wrong, the reasoning error behind it, what changes, and which documents
were updated in the same session. The entry above stays as written.>

-->
