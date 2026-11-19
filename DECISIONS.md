# Decision record

Decisions about how projects are run, in the format the template uses. Numbered in sequence, each
written before the change it governs; a wrong entry gets a dated sub-entry and stays as written.

## Index

| # | decision | status |
|---|---|---|
| 1 | what this repository holds | in force |
| 2 | three parts, one home for each idea | in force |
| 3 | which patterns from the earlier projects were kept | in force |
| 4 | the template does not include `CLAUDE.md` | amended by 4a |
| 5 | skills ship as a plugin | in force |
| 6 | the check tools use only the standard library | in force |
| 7 | projects are kept small by survey, summary and offload | in force |

---

## 1. What this repository holds

**Date** 2026-11-19
**Question** What goes into a model that other people copy to run their own projects?

**Decision** Conventions, templates, tools and skills drawn from four earlier projects, generalized
so that none of them depends on a scientific domain. No data, results, figures or file names from
those projects, and no personal paths, account names or cluster identifiers.

**Reason** The repository is shared with lab members as a model for their own projects. Anything
specific to one project would be copied into another where it does not apply.

---

## 2. Three parts, and one home for each idea

**Date** 2026-11-19
**Question** How is the material divided, and how is repetition avoided?

**Decision** `01_guide/` explains conventions that neither the rules nor the templates state.
`02_template/` holds every file format, as the files themselves. `03_skills/` holds procedures and
points to the template for formats. Each idea is written in one place and cited from the others.

**Reason** The earlier projects stated the same rule in several documents, and the copies
drifted. A model that repeats itself teaches repetition.

---

## 3. Which patterns from the earlier projects were kept

**Date** 2026-11-19
**Question** The conventions changed over the four projects. Which version is the model?

**Decision** The most recent. Kept: numbered stream folders; dated, indexed and frozen run
directories; numbered briefs with strong and tentative lists; the decision record with prediction
blocks; the open-items file with closing conditions; one command that verifies everything; the
gate, reviewer and escalation split; one writer for the record when several agents work at once;
a stream entry point that says which results are current; reviews answered point by point.

Dropped or merged: numbered reports and results directories at the root (they made it impossible
to tell what was current); separate handoff, needs and summary files (their content belongs in the
brief and the open-items file); machine-specific schedulers and collectors (described in general
terms in `01_guide/supervision.md`); cluster rules inside project files (moved to the user-level
file, `01_guide/shared_compute.md`).

Added from an audit of the most recent project: a "current reading" note on corrected documents,
because append-only corrections made long documents hard to read, and a section on proportion,
because much of the record-keeping effort could not distinguish between hypotheses.

---

## 4. The template does not include `CLAUDE.md`

**Date** 2026-11-19
**Question** Should the template carry the working rules file?

**Decision** No, for now. Users copy the lab's current rules file. The template's `README.md` keeps
the domain rules at §6, because the existing rules files point there. `README.md` at the root lists
what the rules file should cover.

**Reason** Drafting a generalized rules file in the session that built this repository was blocked
by an automated check, and the existing files are already nearly project-independent. `OPEN_ITEMS.md`
item 1 tracks the gap.

### 4a. Amended 2026-11-19: the template now includes `CLAUDE.md`

The rules file from the earlier projects was edited by hand and added as `02_template/CLAUDE.md`.
The edits: the stories behind each rule refer to "an earlier project" instead of "this project";
the storage amendment in 7.6 no longer names a cluster path or quota; new rules were appended at the
end of their sections (2.8, 2.9, 3.11, 4.6, 4.7, 6.7) so existing numbers still point to the same
rules; 3.1, 4.3 and 5.2 were extended; and two sections were added, 11 on subagents and independent
review and 12 on proportion. A conflict between it and a project's `README.md` §6 is settled by a
decision entry. `OPEN_ITEMS.md` item 1 is closed.

---

## 5. Skills ship as a Claude Code plugin in `03_skills/`

**Date** 2026-11-19
**Question** How do lab members get the skills?

**Decision** `03_skills/` is a plugin (`research-record`) listed by a marketplace file at the
repository root, so one command installs all six and an update reaches everyone. Copying the folders
into `~/.claude/skills/` remains possible.

**Reason** Copied skills drift between people. The plugin layout was checked against the Claude Code
documentation on 2026-11-19 but has not been installed from a second account (`OPEN_ITEMS.md` item 2).

---

## 6. The check tools use only the standard library

**Date** 2026-11-19
**Question** What may the check tools depend on?

**Decision** Python standard library and bash 3.2, tested on Python 3.7, 3.8 and 3.9 on macOS. Each
finds the project root by walking up to `CLAUDE.md` or `.git`.

**Reason** The checks must run on a fresh clone, on a laptop and on a cluster login node, before any
project environment exists.

---

## 7. Projects are kept small by survey, summary and offload

**Date** 2026-11-19
**Question** How does a project shed material it has moved past without losing it, and without
sessions spending their reading on it?

**Decision** Archived, closed and offloaded material leaves the reading path but stays reachable
through a summary, a recorded location and a way back (`02_template/CLAUDE.md` §13). Added to the
template: `DATA_INVENTORY.md`, which replaces the earlier projects' archive manifests and data
inventories; a closing summary in the stream README; an index at the top of `DECISIONS.md`; an
ignored `work/` in each stream; and three tools, `survey.py` (live, history and unreferenced files,
and budget warnings that never fail), `offload.py` (verified copies to lab storage, recorded in the
inventory, with prune and restore) and `records.py` (the inventory reader the checks share). The
procedure is a seventh skill, `tidy-project`. Nothing costly to regenerate is deleted, and nothing
moves without the person's approval.

**Reason** The earlier projects grew by reruns and side analyses until their roots held dozens of
reports and results folders, and their large data outgrew both git and the laptops it sat on. One
moved its cluster tree into the repository and needed a separate manifest to say what was left
behind. Sessions spent reading on documents a person then had to call outdated.

**Falsifier** A project tidied this way loses something a later session needs, or its sessions
still open archived or closed material to find out whether it is current.

