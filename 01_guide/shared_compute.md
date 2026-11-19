# Shared compute

Rules for an agent using a shared cluster on your account. They belong in your user-level
`~/.claude/CLAUDE.md`, because they apply to every project and to nobody else's account. Copy the
block at the end, fill in the bracketed facts, and delete anything that does not apply.

Survey the cluster before writing them: partitions and their nodes, memory and time limits, what
the default partition and memory are, storage paths and quotas, and what the login node tolerates.
Record what was measured, with the date, in one file the agent reads before anything non-trivial.
Institutional wikis go out of date; a measured fact does not.

## Why each rule exists

- **Ask before non-trivial jobs.** A shared cluster is not a default. Pre-approve a scope for a
  named project when asking every time would stall the work.
- **Login node for metadata only.** Administrators kill compute on login nodes, and repeated kills
  draw attention to the account.
- **Measure, then size.** A small test job and `seff` cost minutes. A memory figure guessed from the
  wrong proportionality once paged for an hour and produced nothing.
- **State partition, time and memory on every job.** Defaults can be a partition with no nodes,
  no time limit, or unlimited memory.
- **Follow up every job in the session that submitted it.** A job left running that does nothing
  useful holds resources others are waiting for.
- **Work like a careful person on your account.** Short descriptive job names, no tool or session
  identifiers, no agent signatures in scripts or comments, one reused SSH connection, no tight
  polling loops, job arrays instead of hundreds of submissions.
- **Never contact the administrators** without your approval of the exact message.
- **Say when the rules hold the work back.** Cautious rules are only worth keeping if someone
  learns where they cost too much.

## Block for `~/.claude/CLAUDE.md`

```markdown
## Shared cluster ([name], [host], user [username]) — rules of conduct

0. The cluster is a shared resource, not a default. Run work locally unless it needs the
   cluster's memory, cores, wall-clock or data, and say why when proposing a cluster job. Ask me
   before submitting any non-trivial job, except read-only metadata queries and jobs within a
   scope I have pre-approved for a named project. Non-trivial means more than a few minutes on a
   few cores, writing outside [my allocation path], downloading large data, or building a
   container or environment.
1. Login node: metadata only (sinfo, squeue, sacct, seff, scontrol, module avail, ls, df, small
   file reads and edits, sbatch/srun/scancel). Everything else, including package solves,
   container builds and any real compute, runs inside a job ([short interactive partition] for
   short interactive work). Data transfer may run from [login or transfer node].
2. Never contact the cluster's administrators without my approval of the exact message.
3. Request only what the job needs. Measure first with a small job and `seff <id>` /
   `sacct -j <id> -o JobID,ReqMem,MaxRSS,Elapsed,State`, then size the real job. Use the smallest
   node class and shortest partition that fit. Do not hold idle GPUs. Delete intermediates.
4. Every job states `-p`, `-t` and `--mem`. [Note any default that would hang or overrun.]
5. Storage: write only under [allocation path]. Never write in other people's directories. Keep
   `$HOME` ([quota]) free of environments, caches and outputs.
6. Software: install it ourselves, in this order: a container image, a conda env with an explicit
   prefix under [allocation path], an existing module. Never ask the administrators to install
   anything.
7. Job scripts begin with `source [env setup script]` (caches and temp dirs out of $HOME).
8. Everything sent to the cluster reads as if I sent it: short descriptive job names, no session
   or tool identifiers, no agent signatures, scratch files kept in a project folder. Reuse one
   SSH connection, do not poll the scheduler more than every few minutes, prefer job arrays.
9. Follow up every job in the session that submitted it. Cancel anything stuck, misplaced, failing
   or no longer needed. Report any job that outlives the session with its id, purpose, expected
   end and output path.
10. Tell me when these rules hold the work back: what you would do instead, why, what it would
    cost the shared resource, and which rule stops you. Then follow the rule unless I change it.
11. Before anything non-trivial, read [path to the measured cluster survey].
```
