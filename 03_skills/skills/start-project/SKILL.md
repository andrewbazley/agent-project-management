---
name: start-project
description: Start a new research project as a git-tracked record (README, DECISIONS, OPEN_ITEMS, numbered streams, verification tools) from the agent-project-management template. Use when the user wants to begin a new long-running or multi-session research project.
---

# Start a project

1. **Ask for what you cannot infer:** the project folder, a one-paragraph goal, the first stream's
   name, and whether a private GitHub remote should be created. Do not invent the goal.
2. **Copy the template.** Clone the template repository shallowly into a scratch directory and copy
   `02_template/` into the new folder, including dotfiles:
   `git clone --depth 1 https://github.com/andrewbazley/agent-project-management <tmp>` then
   `cp -R <tmp>/02_template/. <project>/`. Rename `01_first_stream/` to `01_<stream_name>/`.
3. **Add the working rules.** The template has no `CLAUDE.md`. Ask the user which one to copy (their
   lab's standard file or a recent project's), copy it to the root, and remove anything specific to
   another project. Check that its cross-references (for example "`README.md` §6") match the
   template.
4. **Fill in, from the user's answers only:** the title and goal in `README.md`, §1 and §2, the
   stream row in `FOLDER_LAYOUT.md`, and the stream `README.md`. Leave the HTML comments that guide
   later sessions until the section is filled.
5. **Write decision 1** in `DECISIONS.md`: what the first session is licensed to do and what it is
   not. Write the first brief, `PROMPT_01_<topic>.md`, from the template's sections.
6. **Record the prior-art search** the goal needs before any work starts, or add it to
   `OPEN_ITEMS.md` as the first item if it cannot be run now.
7. **Initialize git**, run `tools/verify_all.sh`, and commit with a message such as "Open the
   project record: goal, first stream, decision 1 and brief 01". Create the remote only if the user
   asked for one, and make it private.
8. Tell the user what was created, what is still a placeholder, and which brief the next session
   should start from.
