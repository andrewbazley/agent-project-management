# Agent project management
by Andrew Bazley

This repository contains documents and an example file system for running long research projects with AI agents, 
in a chain of sessions that build on each other's work, with the project's memory kept as a git-tracked record 
instead of in any one conversation. This avoids losing work to memory compression or archiving, while keeping 
files and discovery organized, documented, and auditable.
I based this repository on how I run my own research projects. While I tried making this as general as possible, 
not all of these workflows may suit every project. Because these documents contain direct agent instructions, 
including CLAUDE.md files, it's important to review the instructions before and during your project, so progress isn't 
inhibited by unhelpful or irrelevant rules.

The overview, is that each session reads the current brief, does the work that brief names, records what it decided and
measured, verifies it, and writes the brief for the next session. Git provides the history and the
proof of order: a decision committed before its result is a prediction, and one committed after is
not. This enables simultaneous benchmarking and learning for coding and development projects.

## What is here

| path | what it is |
|---|---|
| `01_guide/conventions.md` | the record files, naming, version control, adopting an existing project, and when to use less of all this |
| `01_guide/supervision.md` | mechanical checks, independent reviewers, unattended runs, and several agents sharing one record |
| `01_guide/shared_compute.md` | rules for an agent using a shared cluster on your account, with a block for `~/.claude/CLAUDE.md` |
| `01_guide/writing_style.md` | how documents, briefs and commit messages are written |
| `02_template/` | the folder you copy to start a project: the working rules (`CLAUDE.md`), record files, a first stream, review templates and the check tools |
| `03_skills/` | Claude Code skills that carry out the routines: start, adopt, begin a session, end a session, record a decision, review |
| `DECISIONS.md`, `OPEN_ITEMS.md` | this repository's own record |

## Start a project

With the skills installed (below), ask Claude Code to start a project, or run
`/research-record:start-project`. By hand:

```bash
git clone --depth 1 https://github.com/andrewbazley/agent-project-management /tmp/apm
cp -R /tmp/apm/02_template/. my-project/
```

Then rename `01_first_stream/`, fill in
`README.md`, write decision 1 and the first brief, `git init`, and run `tools/verify_all.sh`.

For a project that already exists, use `/research-record:adopt-project`, or follow "Adopting an
existing project" in `01_guide/conventions.md`.

## The working rules (`CLAUDE.md`)

`02_template/CLAUDE.md` holds the general working rules, each with the failure behind it. Claude
Code reads it at the start of every session. Leave it general: rules for one project go in that
project's `README.md` §6, and rules for one person's accounts and machines (such as a cluster) go
in their `~/.claude/CLAUDE.md`. Add a rule only when a real failure is behind it, at the end of its
section, so that existing cross-references such as "`CLAUDE.md` 7.4" keep pointing at the same
rule.

## Install the skills

The skills are a Claude Code plugin. You need git access to this repository on your machine
(`gh auth login` then `gh auth setup-git`, or an SSH key that loads without a prompt). In a Claude
Code session:

```
/plugin marketplace add andrewbazley/agent-project-management
/plugin install research-record@agent-project-management
```

If you have no GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` first. Updates arrive with
`/plugin marketplace update agent-project-management`. To install by hand instead, copy each folder
in `03_skills/skills/` to `~/.claude/skills/`; the skills are then invoked without the
`research-record:` prefix.

| skill | use it to |
|---|---|
| `start-project` | create a new project from the template |
| `adopt-project` | bring an existing folder under this system without losing its history |
| `begin-session` | read the current brief and named entries, check the tree verifies, confirm scope |
| `end-session` | verify, index, propagate, follow up on jobs, write the next brief, commit |
| `record-decision` | write a decision, prediction block or correction before the work it governs |
| `review-stage` | commission an independent review and record the response |

## Changing this repository

Changes follow the same conventions: a reason for each, recorded in `DECISIONS.md` when it changes
how projects are run. Keep it short; every page here is read by people starting a project, and an
idea stated twice will eventually be stated two ways. Nothing from a real project's data, and no
personal paths or account details, belongs here.
