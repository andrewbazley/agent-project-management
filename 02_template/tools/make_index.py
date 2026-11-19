#!/usr/bin/env python3
"""
make_index.py -- an output directory's INDEX.md must name exactly what is in it.

Asserts
    For each directory given, INDEX.md exists, and the backticked names in the
    first column of its table rows cover every file in the directory and name
    nothing that is absent. A name is relative to the directory and may be a
    file (`summary.csv`), a subdirectory covering everything under it
    (`logs/`), or a glob covering a family of files (`fold_*.json`). Files
    under a subdirectory with its own INDEX.md belong to that index. Hidden
    files are ignored, and so is the OFFLOADED.md that offload.py leaves. An
    entry naming a file that is absent because the directory was offloaded (a
    row in DATA_INVENTORY.md "Offloaded") is not stale.

Why
    An output nobody indexed is an output nobody can attribute: later there is
    no record of which script made it, from what, or whether it is current. An
    entry naming a file that is gone is worse, a record claiming evidence that
    is not there. Both creep in silently as scripts are rerun and renamed.

Drafting entries
    --draft prints table rows for the files the index does not name. The
    "made by" column is derived by searching the project's scripts (*.py, *.sh,
    *.R, *.r, *.jl, *.sbatch) in three tiers, stopping at the first that finds
    anything: the exact file name; the name with each run of digits treated as
    interpolated (fold_007.json found as "fold_{i:03d}.json"); and the longest
    stem followed by an interpolation on a line that also names the extension
    ("scores_" + label + ".csv"). A file no tier finds is marked unattributed,
    never guessed. The draft goes to stdout, the evidence for each attribution
    to stderr; descriptions are left for a person to write.

Reads
    Each directory and its INDEX.md; for --draft, the scripts under the root.
Writes
    Nothing. --check exits 1 if any directory fails; --draft exits 0.

Usage
    python3 tools/make_index.py --check DIR [DIR ...]
    python3 tools/make_index.py --draft DIR
"""

import argparse
import fnmatch
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import records  # noqa: E402

PROG = "make_index"
INDEX = "INDEX.md"
SCRIPT_EXTENSIONS = (".py", ".sh", ".R", ".r", ".jl", ".sbatch")
SKIP_DIRS = frozenset({".git", "__pycache__", "node_modules"})
OWN_TOOLS = ("check_citations.py", "check_frozen.py", "make_index.py",
             "verify_all.sh")

TICKED = re.compile(r"`([^`]+)`")
GLOB = re.compile(r"[*?\[]")
DIGITS = re.compile(r"\d+(?:[-_.:T]\d+)*")
VARIABLE = r"[^\s\"'`]{1,40}?"
INTERPOLATION = r"[_.-]?(?:\{|\$|%|[\"']\s*[+,.)])"


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


def read_index(path):
    """Names in the first column of every table row, and the widest header."""
    names, width = [], 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = line.strip("|").split("|")
            names += [n.strip() for n in TICKED.findall(cells[0])]
            width = max(width, len(cells))
    return names, width


def files_in(directory):
    """Relative paths of every file a directory's index answers for."""
    out = []
    for d, dirs, files in os.walk(directory):
        dirs[:] = sorted(
            x for x in dirs if not x.startswith(".")
            and not os.path.exists(os.path.join(d, x, INDEX)))
        for f in sorted(files):
            if f.startswith(".") or (d == directory and f == INDEX) \
                    or f.endswith("OFFLOADED.md"):
                continue
            out.append(os.path.relpath(os.path.join(d, f), directory)
                       .replace(os.sep, "/"))
    return out


def offloaded_here(directory):
    """Whether files under this directory may be absent because offloaded."""
    root = find_root(directory)
    rel = os.path.relpath(os.path.abspath(directory), root)
    return records.covering(rel, [r["local path"]
                                  for r in records.offloaded(root)]) is not None


def coverage(directory):
    """(files no entry covers, entries that match nothing)."""
    entries, _ = read_index(os.path.join(directory, INDEX))
    elsewhere = offloaded_here(directory)
    files = files_in(directory)
    covered, stale = set(), []
    for raw in entries:
        e = raw[2:] if raw.startswith("./") else raw
        if GLOB.search(e):
            hit = {f for f in files if fnmatch.fnmatchcase(f, e)}
        elif os.path.isdir(os.path.join(directory, e)):
            prefix = e.rstrip("/") + "/"
            hit = {f for f in files if f.startswith(prefix)}
            if not hit:
                hit = {None}  # an indexed directory that is empty still exists
        else:
            hit = {e} if os.path.isfile(os.path.join(directory, e)) else set()
        if not hit and not elsewhere:
            stale.append(raw)
        covered |= hit
    return [f for f in files if f not in covered], stale


def display(path, root):
    rel = os.path.relpath(path, root)
    return path if rel.startswith("..") else rel


def check(dirs, root):
    failed = 0
    for d in dirs:
        name = display(os.path.abspath(d), root)
        if not os.path.isfile(os.path.join(d, INDEX)):
            print("FAIL      %s: no %s" % (name, INDEX))
            failed += 1
            continue
        missing, stale = coverage(d)
        if not missing and not stale:
            print("OK        %s (%d files)" % (name, len(files_in(d))))
            continue
        failed += 1
        print("FAIL      %s" % name)
        for f in missing:
            print("  not in %s: %s" % (INDEX, f))
        for e in stale:
            print("  in %s but matches nothing: %s" % (INDEX, e))
    print("%s: %d directories checked, %d failing" % (PROG, len(dirs), failed))
    return 1 if failed else 0


def scripts(root):
    own = {os.path.realpath(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), t)) for t in OWN_TOOLS}
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs
                         if x not in SKIP_DIRS and not x.startswith("."))
        for f in sorted(files):
            p = os.path.join(d, f)
            if f.endswith(SCRIPT_EXTENSIONS) and os.path.realpath(p) not in own:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    out.append((p, fh.read()))
    return out


def tiers(name):
    """(label, compiled pattern, extension a matching line must carry)."""
    base, ext = os.path.splitext(name)
    yield ("name", re.compile(r"(?<![\w.-])" + re.escape(name) + r"(?![\w-]|\.\w)"),
           None)

    parts = DIGITS.split(name)
    if len(parts) > 1 and len(re.sub(r"[^A-Za-z]", "", "".join(parts))) >= 4:
        body = VARIABLE.join(re.escape(p) for p in parts)
        lead = r"(?<![\w.-])" if parts[0] else ""
        yield ("digits as variables", re.compile(lead + body + r"(?![\w-])"), None)

    cuts = [m.start() for m in re.finditer(r"[_.-]", base)]
    for cut in sorted(cuts, reverse=True):
        stem = base[:cut]
        if len(stem) >= 4 and re.search(r"[A-Za-z]", stem):
            yield ("stem %r" % stem,
                   re.compile(r"(?<![\w.-])" + re.escape(stem) + INTERPOLATION),
                   ext or None)


def attribute(name, corpus):
    for label, rx, ext in tiers(name):
        hits = []
        for path, text in corpus:
            for line in text.splitlines():
                if rx.search(line) and (ext is None or ext in line):
                    hits.append(path)
                    break
        if hits:
            return hits, label
    return [], None


def cite(script, directory, root):
    """A script path as the index should cite it: stream-relative if local."""
    rel = os.path.relpath(script, root)
    dir_rel = os.path.relpath(os.path.abspath(directory), root)
    stream = dir_rel.split(os.sep)[0]
    if not dir_rel.startswith("..") and rel.split(os.sep)[0] == stream \
            and stream != ".":
        rel = os.path.relpath(script, os.path.join(root, stream))
    return "`%s`" % rel.replace(os.sep, "/")


def draft(directory, root):
    index = os.path.join(directory, INDEX)
    width = 0
    if os.path.isfile(index):
        missing, stale = coverage(directory)
        width = read_index(index)[1]
    else:
        missing, stale = files_in(directory), []
    if width < 2:
        width = 3
        print("| file | made by | what it is |")
        print("|---|---|---|")
    corpus = scripts(root)
    for f in missing:
        hits, how = attribute(os.path.basename(f), corpus)
        made_by = ", ".join(cite(h, directory, root) for h in hits) \
            if hits else "**unattributed**"
        print("| `%s` | %s |%s" % (f, made_by, " |" * (width - 2)))
        if hits:
            print("%s: by %s in %s" % (f, how, ", ".join(
                os.path.relpath(h, root) for h in hits)), file=sys.stderr)
        else:
            print("%s: no script names it; fill in by hand" % f, file=sys.stderr)
    for e in stale:
        print("%s names %s, which matches nothing; remove or fix the row"
              % (INDEX, e), file=sys.stderr)
    if not missing:
        print("%s: %s names every file" % (PROG, display(index, root)),
              file=sys.stderr)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", nargs="+", metavar="DIR")
    mode.add_argument("--draft", metavar="DIR")
    ap.add_argument("--root", help="repository root (default: found by walking "
                    "up from this script to CLAUDE.md or .git)")
    args = ap.parse_args(argv)

    root = os.path.realpath(args.root) if args.root else \
        os.path.realpath(find_root(os.path.dirname(os.path.abspath(__file__))))
    for d in args.check or [args.draft]:
        if not os.path.isdir(d):
            sys.exit("%s: not a directory: %s" % (PROG, d))
    if args.draft:
        return draft(os.path.realpath(args.draft), root)
    return check([os.path.realpath(d) for d in args.check], root)


if __name__ == "__main__":
    sys.exit(main())
