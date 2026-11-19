#!/usr/bin/env python3
"""
survey.py -- which files the project's current documents lead to, which are
kept only as history, which nothing cites, and where the tree is growing.

States
    live          In the reading path: an entry point, or reached from one by
                  following citations. The entry points are README.md,
                  CLAUDE.md, FOLDER_LAYOUT.md, OPEN_ITEMS.md and
                  DATA_INVENTORY.md at the root, everything under the root
                  tools/, and in each open stream its README.md, its current
                  brief (the highest PROMPT_NN) and its tools/verify_*
                  scripts. DECISIONS.md is live, but its citations are not
                  followed, because it cites everything the project has done.
    history       On record but out of the reading path: under an archive/
                  directory, inside a closed stream, a superseded brief, or
                  cited only by documents of that kind or by DECISIONS.md.
    unreferenced  Cited by no document at all.

    A stream is closed when its README.md has a line beginning
    "**Closed YYYY-MM-DD". Its README.md stays live, as the summary a session
    reads instead of the stream, but its citations are not followed.

Following citations
    Citations are found and resolved as check_citations.py does, and only
    Markdown documents are followed. A cited directory brings in its INDEX.md
    and README.md, or, if it has neither, the Markdown files directly in it;
    a directory cited by an INDEX.md or by DATA_INVENTORY.md
    counts as wholly cited, since those documents answer for everything in it.
    A live INDEX.md brings in every file its table covers, globs included.
    Nothing in a history location becomes live, whoever cites it.

Why
    A project grows by runs, reruns and side analyses, and a session that
    reads its way in spends its effort on material the project has moved past.
    Sorting the tree into what the current documents lead to, what is kept as
    history, and what nothing cites turns "what can be archived" into a list a
    person can review, rather than a judgment made file by file.

Budget (--budget)
    One WARN line for each sign that the project needs tidying: more files at
    the root than --root-files (12); a folder holding more than --briefs (3)
    briefs outside archive/; a "Where the work stands" section in README.md
    longer than --status-lines (20) lines; entry points that cite more than
    --direct-docs (12) documents directly; unreferenced material above
    --unreferenced-files (100) files or --unreferenced-size (1GB); a file git
    tracks above 50MB (GitHub warns at 50MB and refuses 100MB); and anything
    git ignores above --ignored-size (1GB) that DATA_INVENTORY.md does not
    list. The warnings are advisory: --budget exits 0, and verify_all.sh shows
    them without failing.

Reads
    The tree, every Markdown document, git's tracked and ignored lists.
Writes
    Nothing.

Usage
    python3 tools/survey.py                  totals, largest unreferenced and ignored items
    python3 tools/survey.py --list STATE     every item in a state, rolled up to directories
    python3 tools/survey.py --reading        the live documents: hops from an entry point,
                                             length in lines, and the document that leads there
    python3 tools/survey.py --budget         advisory warnings only
"""

import argparse
import collections
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_citations as cc  # noqa: E402
import make_index as mi  # noqa: E402
import records  # noqa: E402

PROG = "survey"
STATES = ("live", "history", "unreferenced")
ENTRY_POINTS = ("README.md", "CLAUDE.md", "FOLDER_LAYOUT.md", "OPEN_ITEMS.md",
                records.FILE)
UNFOLLOWED = ("DECISIONS.md",)
SKIP_DIRS = frozenset({".git", "__pycache__", "node_modules", "venv", ".venv"})
STREAM = re.compile(r"^\d{2,}_")
BRIEF = re.compile(r"^PROMPT_(\d+)")
CLOSED = re.compile(r"^\*\*Closed \d{4}-\d{2}-\d{2}")


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, "CLAUDE.md")) or \
                os.path.exists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("%s: no CLAUDE.md or .git above %s; pass --root"
                     % (PROG, start))
        d = parent


def human(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1000 or unit == "TB":
            return "%d B" % n if unit == "B" else "%.1f %s" % (n, unit)
        n /= 1000


def parse_size(text):
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([KMGT]?)B?\s*$", text, re.I)
    if not m:
        raise argparse.ArgumentTypeError("not a size: %r" % text)
    return int(float(m.group(1)) * 1000 ** " KMGT".index(m.group(2).upper() or " "))


def git(root, *args):
    try:
        out = subprocess.run(["git", "-C", root] + list(args),
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             check=True).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.CalledProcessError):
        return None
    return [p for p in out.split("\0") if p]


class Project(object):

    def __init__(self, root):
        self.root = root
        self.tree = cc.Tree(root)
        self.size = {}
        for d, dirs, files in os.walk(root):
            dirs[:] = sorted(x for x in dirs
                             if x not in SKIP_DIRS and not x.startswith("."))
            for f in files:
                if f.startswith("."):
                    continue
                p = os.path.join(d, f)
                self.size[self.rel(p)] = os.lstat(p).st_size
        self.streams = sorted(
            x for x in os.listdir(root)
            if STREAM.match(x) and os.path.isdir(os.path.join(root, x)))
        self.closed = {s for s in self.streams if self._is_closed(s)}
        self.briefs = {}
        for rel in self.size:
            parts = rel.split("/")
            m = BRIEF.match(parts[-1])
            if m and parts[-1].endswith(".md") and "archive" not in parts:
                self.briefs.setdefault("/".join(parts[:-1]), []).append(
                    (int(m.group(1)), rel))
        self.current = {max(v)[1] for v in self.briefs.values()}

    def rel(self, path):
        return os.path.relpath(path, self.root).replace(os.sep, "/")

    def _is_closed(self, stream):
        p = os.path.join(self.root, stream, "README.md")
        if not os.path.isfile(p):
            return False
        with open(p, encoding="utf-8", errors="replace") as fh:
            return any(CLOSED.match(line) for line in fh.read().splitlines()[:40])

    def history_location(self, rel):
        parts = rel.split("/")
        if "archive" in parts:
            return True
        if parts[0] in self.closed and rel != parts[0] + "/README.md":
            return True
        return BRIEF.match(parts[-1]) is not None and rel.endswith(".md") \
            and rel not in self.current

    def under(self, rel_dir):
        prefix = rel_dir.rstrip("/") + "/"
        return [f for f in self.size if f.startswith(prefix)]

    def resolve(self, doc, cited):
        """The project-relative path a citation in doc names, or None."""
        bases, stream = cc.bases_for(os.path.join(self.root, doc), self.root)
        expanded = os.path.expanduser(cited)
        if cited.startswith("~"):
            return None
        if os.path.isabs(expanded):
            if (expanded + os.sep).startswith(self.root + os.sep) \
                    and self.tree.exists(expanded):
                return self.rel(expanded).rstrip("/")
            return None
        for b in bases:
            p = os.path.normpath(os.path.join(b, cited))
            if self.tree.exists(p) and (p + os.sep).startswith(self.root + os.sep):
                return self.rel(p)
        if "/" not in cited:
            matches = self.tree.named(cited)
            if len(matches) > 1 and stream:
                local = [m for m in matches if os.path.join(self.root, m)
                         .startswith(stream + os.sep)]
                matches = local if len(local) == 1 else matches
            if len(matches) == 1:
                return matches[0].replace(os.sep, "/")
        return None

    def citations(self, doc):
        with open(os.path.join(self.root, doc), encoding="utf-8",
                  errors="replace") as fh:
            text = fh.read()
        for _, cited in cc.citations(text):
            target = self.resolve(doc, cited)
            if target and target != ".":
                yield target

    def answers_for_whole(self, doc):
        return os.path.basename(doc) == "INDEX.md" or doc == records.FILE

    def classify(self):
        live, queue = set(), collections.deque()
        # Breadth-first, so each document's recorded depth is its shortest
        # distance from an entry point and its parent is the nearest citer.
        self.depth, self.parent = {}, {}

        def add(rel, follow=True, parent=None):
            if rel in live or rel not in self.size or self.history_location(rel):
                return
            live.add(rel)
            self.depth[rel] = self.depth[parent] + 1 if parent else 0
            self.parent[rel] = parent
            if follow and rel.endswith(".md") and rel not in UNFOLLOWED:
                queue.append(rel)

        for name in ENTRY_POINTS + UNFOLLOWED:
            add(name)
        for f in self.under("tools"):
            add(f, follow=False)
        for s in self.streams:
            if s in self.closed:
                add(s + "/README.md", follow=False)
                continue
            add(s + "/README.md")
            for f in self.under(s + "/tools"):
                if os.path.basename(f).startswith("verify_"):
                    add(f, follow=False)
        for rel in self.current:
            if rel.split("/")[0] not in self.closed:
                add(rel)

        while queue:
            doc = queue.popleft()
            for target in self.citations(doc):
                if os.path.isdir(os.path.join(self.root, target)):
                    if self.answers_for_whole(doc):
                        for f in self.under(target):
                            add(f, parent=doc)
                    else:
                        heads = [target + "/" + n for n in ("INDEX.md", "README.md")
                                 if target + "/" + n in self.size]
                        if not heads:
                            heads = [f for f in self.under(target) if f.endswith(".md")
                                     and "/" not in f[len(target) + 1:]]
                        for f in heads:
                            add(f, parent=doc)
                else:
                    add(target, parent=doc)
            if os.path.basename(doc) == "INDEX.md":
                d = os.path.join(self.root, os.path.dirname(doc))
                uncovered = set(mi.coverage(d)[0])
                for f in mi.files_in(d):
                    if f not in uncovered:
                        add(self.rel(os.path.join(d, f)), parent=doc)

        cited_files, cited_dirs = set(), set()
        for doc in (f for f in self.size if f.endswith(".md")):
            for target in self.citations(doc):
                if os.path.isdir(os.path.join(self.root, target)):
                    cited_dirs.add(target)
                else:
                    cited_files.add(target)

        def cited(rel):
            if rel in cited_files:
                return True
            parts = rel.split("/")
            return any("/".join(parts[:i]) in cited_dirs
                       for i in range(1, len(parts)))

        state = {}
        for rel in self.size:
            if rel in live:
                state[rel] = "live"
            elif self.history_location(rel) or cited(rel):
                state[rel] = "history"
            else:
                state[rel] = "unreferenced"
        return state

    def rollup(self, state, want):
        """Items in a state, each the highest directory wholly in it."""
        uniform, size, count = {}, {}, {}
        for rel, st in state.items():
            parts = rel.split("/")
            for i in range(1, len(parts)):
                d = "/".join(parts[:i])
                uniform[d] = st if uniform.get(d, st) == st else None
                size[d] = size.get(d, 0) + self.size[rel]
                count[d] = count.get(d, 0) + 1
        items = {}
        for rel, st in state.items():
            if st != want:
                continue
            parts, top = rel.split("/"), rel
            for i in range(1, len(parts)):
                d = "/".join(parts[:i])
                if uniform.get(d) == want:
                    top = d + "/"
                    break
            if top.endswith("/"):
                items[top] = (size[top[:-1]], count[top[:-1]])
            else:
                items[top] = (self.size[rel], 1)
        return sorted(items.items(), key=lambda kv: (-kv[1][0], kv[0]))

    def ignored(self):
        """Top-level ignored paths with their sizes, or None outside git."""
        paths = git(self.root, "ls-files", "-z", "--others", "--ignored",
                    "--exclude-standard", "--directory")
        if paths is None:
            return None
        out = []
        for p in paths:
            p = p.rstrip("/")
            if any(x in SKIP_DIRS or x.startswith(".") for x in p.split("/")):
                continue
            full = os.path.join(self.root, p)
            if os.path.isdir(full):
                total = 0
                for d, _, files in os.walk(full):
                    total += sum(os.lstat(os.path.join(d, f)).st_size
                                 for f in files)
            elif os.path.lexists(full):
                total = os.lstat(full).st_size
            else:
                continue
            out.append((p, total))
        return sorted(out, key=lambda t: -t[1])

    def direct(self):
        """Documents one citation away from an entry point."""
        return sorted(r for r, d in self.depth.items() if d == 1 and r.endswith(".md"))

    def lines(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8",
                  errors="replace") as fh:
            return sum(1 for _ in fh)


def status_lines(root):
    p = os.path.join(root, "README.md")
    if not os.path.isfile(p):
        return 0
    with open(p, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    m = re.search(r"^## Where the work stands\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return 0
    body = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S)
    return sum(1 for line in body.splitlines() if line.strip())


def budget(project, state, args):
    root, warnings = project.root, []
    root_files = [f for f in os.listdir(root)
                  if not f.startswith(".") and os.path.isfile(os.path.join(root, f))]
    if len(root_files) > args.root_files:
        warnings.append("the root holds %d files (budget %d); move documents "
                        "into streams or archive/" % (len(root_files), args.root_files))
    for folder, briefs in sorted(project.briefs.items()):
        if len(briefs) > args.briefs:
            warnings.append("%s holds %d briefs outside archive/ (budget %d); "
                            "archive the superseded ones"
                            % (folder or "the root", len(briefs), args.briefs))
    n = status_lines(root)
    if n > args.status_lines:
        warnings.append("README.md \"Where the work stands\" runs %d lines "
                        "(budget %d); the detail belongs in the brief"
                        % (n, args.status_lines))
    direct = project.direct()
    if len(direct) > args.direct_docs:
        warnings.append("the entry points cite %d documents directly (%d lines; budget "
                        "%d documents); a session's reading path starts this wide "
                        "(survey.py --reading)" % (len(direct), sum(project.lines(r)
                                                   for r in direct), args.direct_docs))
    unref = [r for r, s in state.items() if s == "unreferenced"]
    unref_size = sum(project.size[r] for r in unref)
    if len(unref) > args.unreferenced_files or unref_size > args.unreferenced_size:
        warnings.append("%d unreferenced files (%s); a tidy is due "
                        "(survey.py --list unreferenced)" % (len(unref), human(unref_size)))
    tracked = git(root, "ls-files", "-z") or []
    for p in tracked:
        full = os.path.join(root, p)
        if os.path.isfile(full) and os.path.getsize(full) > 50 * 1000 ** 2:
            warnings.append("git tracks %s (%s); GitHub refuses files over 100MB"
                            % (p, human(os.path.getsize(full))))
    listed = [p for p, _ in records.inventoried(root)]
    for p, size in project.ignored() or []:
        if size > args.ignored_size and not records.covering(p, listed):
            warnings.append("%s (%s) is ignored by git and not listed in %s"
                            % (p, human(size), records.FILE))
    return warnings


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--list", choices=STATES, metavar="STATE")
    mode.add_argument("--reading", action="store_true")
    mode.add_argument("--budget", action="store_true")
    ap.add_argument("--top", type=int, default=15,
                    help="items shown per section of the summary")
    ap.add_argument("--root-files", type=int, default=12)
    ap.add_argument("--briefs", type=int, default=3)
    ap.add_argument("--status-lines", type=int, default=20)
    ap.add_argument("--direct-docs", type=int, default=12)
    ap.add_argument("--unreferenced-files", type=int, default=100)
    ap.add_argument("--unreferenced-size", type=parse_size, default=parse_size("1GB"))
    ap.add_argument("--ignored-size", type=parse_size, default=parse_size("1GB"))
    ap.add_argument("--root", help="project root (default: found by walking up "
                    "from this script to CLAUDE.md or .git)")
    args = ap.parse_args(argv)

    root = os.path.realpath(args.root) if args.root else \
        os.path.realpath(find_root(os.path.dirname(os.path.abspath(__file__))))
    project = Project(root)
    state = project.classify()

    if args.budget:
        warnings = budget(project, state, args)
        for w in warnings:
            print("WARN  " + w)
        print("%s: %d budget warnings" % (PROG, len(warnings)))
        return 0

    if args.list:
        for item, (size, count) in project.rollup(state, args.list):
            print("%10s %6d  %s" % (human(size), count, item))
        return 0

    if args.reading:
        totals = {}
        docs = [r for r, s in state.items() if s == "live" and r.endswith(".md")]
        for rel in sorted(docs, key=lambda r: (project.depth[r], r)):
            print("%2d %6d  %s%s" % (project.depth[rel], project.lines(rel), rel,
                                     "  (from %s)" % project.parent[rel]
                                     if project.parent[rel] else ""))
        for st in STATES:
            docs = [r for r, s in state.items() if s == st and r.endswith(".md")]
            totals[st] = (len(docs), sum(project.lines(r) for r in docs))
        print("%s: live documents %d (%d lines); history %d (%d lines); "
              "unreferenced %d (%d lines)"
              % ((PROG,) + totals["live"] + totals["history"] + totals["unreferenced"]))
        return 0

    print("%s: %s" % (PROG, root))
    for st in STATES:
        files = [r for r, s in state.items() if s == st]
        print("  %-13s %6d files %10s" % (st, len(files),
                                           human(sum(project.size[r] for r in files))))
    live_docs = [r for r, s in state.items() if s == "live" and r.endswith(".md")]
    direct = project.direct()
    print("  reading path  %6d documents, %d lines; %d documents (%d lines) one "
          "citation from an entry point" % (len(live_docs), sum(project.lines(r) for r in live_docs),
                                            len(direct), sum(project.lines(r) for r in direct)))
    if project.closed:
        print("  closed streams: %s" % ", ".join(sorted(project.closed)))
    items = project.rollup(state, "unreferenced")
    if items:
        print("Largest unreferenced items:")
        for item, (size, count) in items[:args.top]:
            print("  %10s %6d  %s" % (human(size), count, item))
        if len(items) > args.top:
            print("  and %d more (--list unreferenced)" % (len(items) - args.top))
    ignored = project.ignored()
    if ignored:
        listed = [p for p, _ in records.inventoried(root)]
        print("Largest items git ignores:")
        for p, size in ignored[:args.top]:
            print("  %10s  %s%s" % (human(size), p, "" if records.covering(p, listed)
                                    else "  (not in %s)" % records.FILE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
