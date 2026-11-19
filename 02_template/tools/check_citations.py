#!/usr/bin/env python3
"""
check_citations.py -- every repository path a document cites must resolve.

Asserts
    Every path cited in a Markdown document of this repository, as an inline
    code span or as a link target, names a file or directory that exists, with
    the same letter case. A citation resolves if it exists relative to the
    citing document's directory, to the top-level stream folder enclosing the
    document, or to the repository root.

Why
    A cited path that does not resolve is the same class of error as a
    fabricated citation: the reader is told there is evidence where there is
    none. Paths break silently when files are renamed, moved, or never written,
    and a project that relies on its own records needs the break reported when
    it happens, not when someone follows the link.

    Four cases are reported without failing:
    - A path declared in the exceptions file (citation_exceptions.txt beside
      this script) as deliberately external or absent. A row is consulted only
      after normal resolution fails, so it can never mask a path that resolves,
      and a row that no document uses is itself a failure, so the file cannot
      outlive the citations it was written for.
    - A path equal to or under one listed in DATA_INVENTORY.md, which
      records data kept outside git (ignored, or offloaded to lab storage)
      and where it lives. The inventory is the declaration, so a fresh clone
      without the data still verifies.
    - An absolute path outside the repository, or one under `~/`. It is
      external by form: it already says where the file lives.
    - A bare file name matching several files in the tree, printed with its
      candidates as ambiguous. A reader finds something; whether it is the
      right thing needs a person to decide.

What counts as a citation
    An inline code span holding a single token that looks like a path (it
    contains `/` or ends in a known file extension), and every link target
    that is not a URL or an in-page anchor. Fenced code blocks are skipped, as
    are spans holding glob patterns, placeholders such as <name>, {x} or $VAR,
    options, or whitespace. A trailing :LINE or #anchor is ignored. Documents
    under an archive/ directory are not checked: they record what was true
    when they were archived.

Exceptions file format
    One `path<TAB or two or more spaces>reason` per line; `#` starts a comment.
    The path may be a glob (fnmatch, `*` spans `/`). The reason names the
    system the path belongs to, or why it is deliberately absent.

Reads
    Markdown files that git tracks or does not ignore (every *.md when the
    root is not a git work tree), the file tree, the exceptions file and
    DATA_INVENTORY.md.
Writes
    Nothing. Exits 1 if a citation does not resolve or an exception row is
    unused, 2 on a usage error.

Usage
    python3 tools/check_citations.py                 # the whole repository
    python3 tools/check_citations.py DOC.md [...]    # only these documents
    python3 tools/check_citations.py --root DIR --exceptions FILE
"""

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import records  # noqa: E402

PROG = "check_citations"

EXTENSIONS = frozenset("""
    md markdown txt rst tex bib
    py ipynb sh bash zsh r rmd jl sbatch slurm pl rb js ts c h cc cpp hpp
    java go rs sql
    json jsonl yaml yml toml ini cfg conf env lock xml html htm css
    csv tsv parquet feather arrow h5 hdf5 nc zarr npy npz pkl pickle rds rdata
    mat sqlite db duckdb log out err
    pdf png jpg jpeg gif svg tif tiff eps webp docx xlsx pptx odt
    gz bz2 xz zst zip tar tgz sif def
""".split())

SKIP_DIRS = frozenset({".git", "__pycache__", "node_modules"})

FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
INLINE_LINK = re.compile(
    r"\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
REF_LINK = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
LINE_SUFFIX = re.compile(r":\d+(?:[-:]\d+)?$")
NOT_A_PATH = re.compile(r"[\s*?\[\]{}<>$|=,;()'\"\\@!:]")
PLACEHOLDER = re.compile(r"[*?\[\]{}<>$]")
GLOB = re.compile(r"[*?\[]")


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


def to_path(token, from_link):
    """The repository path a code span or link target cites, or None."""
    t = token.strip()
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1].strip()
    if not t or t.startswith("#") or t.startswith("//") or t.startswith("www."):
        return None
    t = LINE_SUFFIX.sub("", t.split("#", 1)[0])
    if SCHEME.match(t):
        return None
    if from_link:
        t = unquote(t)
        if PLACEHOLDER.search(t):
            return None
    else:
        if t.startswith("-") or NOT_A_PATH.search(t):
            return None
        ext = os.path.splitext(t.rstrip("/"))[1][1:].lower()
        if "/" not in t and ext not in EXTENSIONS:
            return None
    if not re.search(r"[A-Za-z]", t):
        return None
    return t


def citations(text):
    """Yield (line number, cited path) for every citation outside code fences."""
    fence = None
    for n, line in enumerate(text.splitlines(), start=1):
        m = FENCE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        for span in CODE_SPAN.finditer(line):
            p = to_path(span.group(2), from_link=False)
            if p:
                yield n, p
        prose = CODE_SPAN.sub("", line)
        for rx in (INLINE_LINK, REF_LINK):
            for link in rx.finditer(prose):
                p = to_path(link.group(1), from_link=True)
                if p:
                    yield n, p


class Exceptions(object):
    """The exceptions table, with a count of the citations each row covered."""

    def __init__(self, path):
        self.path = path
        self.rows = []
        if not os.path.exists(path):
            return
        with open(path, encoding="utf-8") as fh:
            for n, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                fields = re.split(r"\t+| {2,}", line, maxsplit=1)
                if len(fields) != 2 or not fields[1].strip():
                    # A row that does not parse would cover nothing silently.
                    sys.exit("%s:%d: expected `path<TAB>reason`, got %r"
                             % (path, n, line))
                self.rows.append({"path": norm(fields[0]),
                                  "reason": fields[1].strip(),
                                  "line": n, "uses": 0})

    def cover(self, cited):
        cited = norm(cited)
        for row in self.rows:
            pat = row["path"]
            if cited == pat or (GLOB.search(pat)
                                and fnmatch.fnmatchcase(cited, pat)):
                row["uses"] += 1
                return row
        return None


def norm(p):
    p = p.strip()
    while p.startswith("./"):
        p = p[2:]
    return p.rstrip("/") or p


class Tree(object):
    """Exact-case existence tests and a lazily built index of file names."""

    def __init__(self, root):
        self.root = root
        self._listings = {}
        self._by_name = None

    def _listdir(self, d):
        if d not in self._listings:
            try:
                self._listings[d] = frozenset(os.listdir(d))
            except OSError:
                self._listings[d] = frozenset()
        return self._listings[d]

    def exists(self, path):
        # On a case-insensitive file system os.path.exists accepts a path that
        # will not resolve elsewhere, so each component inside the root is
        # matched against the directory listing.
        path = os.path.normpath(path)
        if not os.path.exists(path):
            return False
        rel = os.path.relpath(path, self.root)
        if rel == "." or rel.startswith(".." + os.sep) or rel == "..":
            return True
        d = self.root
        for part in rel.split(os.sep):
            if part not in self._listdir(d):
                return False
            d = os.path.join(d, part)
        return True

    def named(self, name):
        if self._by_name is None:
            self._by_name = {}
            for d, dirs, files in os.walk(self.root):
                dirs[:] = sorted(x for x in dirs
                                 if x not in SKIP_DIRS and not x.startswith("."))
                for f in files:
                    self._by_name.setdefault(f, []).append(
                        os.path.relpath(os.path.join(d, f), self.root))
        return self._by_name.get(name, [])


def documents(root):
    """Markdown files git tracks or does not ignore, else every *.md."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files", "-z", "--cached", "--others",
             "--exclude-standard", "--", "*.md"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True
        ).stdout.decode("utf-8", "replace")
        docs = [os.path.join(root, p) for p in out.split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        docs = []
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs
                       if x not in SKIP_DIRS and not x.startswith(".")]
            docs += [os.path.join(d, f) for f in files if f.endswith(".md")]
    return sorted(p for p in set(docs)
                  if "archive" not in os.path.relpath(p, root).split(os.sep)
                  and os.path.isfile(p))


def bases_for(doc, root):
    """
    Where a citation in this document may resolve from: its own directory,
    the top-level stream folder enclosing it, and the root. Returns the bases
    and the stream folder, which is None for a document at the root.
    """
    here = os.path.dirname(os.path.abspath(doc))
    rel = os.path.relpath(here, root)
    stream = None
    if rel != "." and not rel.startswith(".."):
        stream = os.path.join(root, rel.split(os.sep)[0])
    bases = []
    for b in (here, stream, root):
        if b and b not in bases:
            bases.append(b)
    return bases, stream


def check(root, docs, exceptions):
    tree = Tree(root)
    counts = {"cited": 0, "resolved": 0, "external": 0, "excepted": 0,
              "inventoried": 0, "ambiguous": 0, "unresolved": 0}
    listed = [p for p, _ in records.inventoried(root)]
    report = []

    for doc in docs:
        with open(doc, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        rel_doc = os.path.relpath(doc, root)
        bases, stream = bases_for(doc, root)

        for n, cited in citations(text):
            counts["cited"] += 1
            where = "%s:%d" % (rel_doc, n)
            expanded = os.path.expanduser(cited)

            if cited.startswith("~") or (
                    os.path.isabs(cited)
                    and not (expanded + os.sep).startswith(root + os.sep)):
                counts["external"] += 1
                continue
            if os.path.isabs(cited):
                if tree.exists(cited):
                    counts["resolved"] += 1
                    continue
            elif any(tree.exists(os.path.join(b, cited)) for b in bases):
                counts["resolved"] += 1
                continue

            matches = [] if "/" in cited else tree.named(cited)
            if len(matches) > 1 and stream:
                # A document inside a stream means the copy beside it.
                local = [m for m in matches if os.path.join(root, m)
                         .startswith(stream + os.sep)]
                if len(local) == 1:
                    matches = local
            if len(matches) == 1:
                counts["resolved"] += 1
                continue

            if not os.path.isabs(cited) and any(
                    records.covering(os.path.relpath(
                        os.path.normpath(os.path.join(b, cited)), root), listed)
                    for b in bases):
                counts["inventoried"] += 1
                continue

            if exceptions.cover(cited):
                counts["excepted"] += 1
                continue

            if len(matches) > 1:
                counts["ambiguous"] += 1
                report.append(("AMBIGUOUS", where, cited,
                               "matches " + ", ".join(sorted(matches))))
                continue

            counts["unresolved"] += 1
            if os.path.isabs(cited):
                why = "absolute path inside the repository does not exist"
            else:
                why = "not found from " + ", ".join(
                    os.path.relpath(b, root) for b in bases)
                if "/" not in cited:
                    why += ", nor anywhere in the tree"
            report.append(("FAIL", where, cited, why))
    return counts, report


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docs", nargs="*", help="documents to check (default: all)")
    ap.add_argument("--root", help="repository root (default: found by walking "
                    "up from this script to CLAUDE.md or .git)")
    ap.add_argument("--exceptions", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "citation_exceptions.txt"))
    args = ap.parse_args(argv)

    root = os.path.realpath(args.root) if args.root else \
        os.path.realpath(find_root(os.path.dirname(os.path.abspath(__file__))))
    exceptions = Exceptions(args.exceptions)
    if args.docs:
        missing = [d for d in args.docs if not os.path.isfile(d)]
        if missing:
            sys.exit("%s: no such document: %s" % (PROG, ", ".join(missing)))
        docs = [os.path.realpath(d) for d in args.docs]
    else:
        docs = documents(root)

    counts, report = check(root, docs, exceptions)

    # Whether a row is unused can only be known when every document was read.
    unused = [] if args.docs else [r for r in exceptions.rows if r["uses"] == 0]
    exc_name = os.path.relpath(exceptions.path, root) \
        if exceptions.path.startswith(root + os.sep) else exceptions.path
    for r in unused:
        report.append(("FAIL", "%s:%d" % (exc_name, r["line"]), r["path"],
                       "exception used by no document (the citation is gone, "
                       "or the path now resolves)"))

    for status, where, cited, why in report:
        print("%-9s %s  `%s`  %s" % (status, where, cited, why))
    print("%s: %d citations in %d documents: %d resolve, %d external by form, "
          "%d in the data inventory, %d excepted, %d ambiguous, %d do not "
          "resolve; %d unused exceptions"
          % (PROG, counts["cited"], len(docs), counts["resolved"],
             counts["external"], counts["inventoried"], counts["excepted"],
             counts["ambiguous"],
             counts["unresolved"], len(unused)))
    return 1 if counts["unresolved"] or unused else 0


if __name__ == "__main__":
    sys.exit(main())
