#!/usr/bin/env python3
"""
check_frozen.py -- frozen files must stay byte-for-byte what a manifest records.

Asserts
    Every file a manifest names still exists and has the SHA-256 digest the
    manifest recorded when it was written.

Why
    Once a specification, threshold table or reference output is frozen, later
    work is measured against it. A rerun that silently rewrites it, or an edit
    made to "fix" a number, breaks every comparison drawn since, and nothing
    else in the repository notices. A difference is not necessarily wrong, but
    it must never be discovered later: it means an input or the code changed,
    and the change needs a dated decision before results are compared again.

    Many generators stamp the time they ran into their output, so a faithful
    rerun differs in bytes and in nothing else. Calling that drift teaches
    people to ignore the check, so each file also gets a content digest that
    ignores text matching a volatile pattern (by default ISO-8601 date-times).
    The matched text, not the whole line, is replaced before hashing; a
    pattern matching whole lines (e.g. `^# generated .*$`) ignores the line.
    A file whose bytes differ but whose content digest matches is reported as
    VOLATILE and passes unless --strict is given. Files larger than 256 MiB get
    a byte digest only.

Manifest
    JSON: the volatile pattern, the time written, and for each file its path
    relative to the repository root, size, byte digest and content digest.
    Paths are root-relative so the check runs from any working directory.

Reads
    --write: the files and globs given (a directory means every file under it).
    --check: each manifest and the files it names.
Writes
    --write: the manifest. It refuses to overwrite an existing manifest
    without --force, because re-freezing is a decision, not a repair.
    --check: nothing. Exits 1 on any CHANGED or MISSING file.

Usage
    python3 tools/check_frozen.py --write MANIFEST FILE|DIR|GLOB [...]
           [--volatile REGEX | --no-volatile] [--force]
    python3 tools/check_frozen.py --check MANIFEST [MANIFEST ...] [--strict]
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import sys

PROG = "check_frozen"

DEFAULT_VOLATILE = (r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?"
                    r"(?:Z|[+-]\d{2}:?\d{2})?")
CONTENT_DIGEST_MAX_BYTES = 256 * 1024 * 1024
CHUNK = 1024 * 1024


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


def byte_digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def content_digest(path, volatile):
    """SHA-256 of the file with volatile text replaced, line by line."""
    if volatile is None or os.path.getsize(path) > CONTENT_DIGEST_MAX_BYTES:
        return None
    rx = re.compile(volatile.encode("utf-8"))
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for line in fh:
            h.update(rx.sub(b"<volatile>", line))
    return h.hexdigest()


def expand(patterns, exclude):
    files = []
    for pat in patterns:
        hits = sorted(glob.glob(pat, recursive=True)) if re.search(r"[*?\[]", pat) \
            else ([pat] if os.path.exists(pat) else [])
        if not hits:
            sys.exit("%s: nothing matches %s" % (PROG, pat))
        for hit in hits:
            if os.path.isdir(hit):
                for d, dirs, names in os.walk(hit):
                    dirs[:] = sorted(x for x in dirs if not x.startswith("."))
                    files += [os.path.join(d, n) for n in sorted(names)
                              if not n.startswith(".")]
            else:
                files.append(hit)
    seen, out = set(), []
    for f in files:
        f = os.path.realpath(f)
        if f not in seen and f != exclude:
            seen.add(f)
            out.append(f)
    return out


def write(manifest, patterns, root, volatile, force):
    manifest_abs = os.path.realpath(manifest)
    if os.path.exists(manifest_abs) and not force:
        sys.exit("%s: %s exists; re-freezing is deliberate, pass --force"
                 % (PROG, manifest))
    if volatile is not None:
        re.compile(volatile)
    entries = {}
    for f in expand(patterns, manifest_abs):
        rel = os.path.relpath(f, root)
        if rel.startswith(".."):
            sys.exit("%s: %s is outside the repository root %s" % (PROG, f, root))
        entries[rel.replace(os.sep, "/")] = {
            "bytes": os.path.getsize(f),
            "sha256": byte_digest(f),
            "content_sha256": content_digest(f, volatile),
        }
    record = {
        "format": 1,
        "written": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "volatile_pattern": volatile,
        "files": entries,
    }
    os.makedirs(os.path.dirname(manifest_abs), exist_ok=True)
    with open(manifest_abs, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("%s: froze %d files in %s" % (PROG, len(entries), manifest))
    return 0


def check(manifest, root, strict):
    """Check one manifest; returns the number of failing files."""
    shown = os.path.relpath(os.path.realpath(manifest), root)
    if shown.startswith(".."):
        shown = manifest
    try:
        with open(manifest, encoding="utf-8") as fh:
            record = json.load(fh)
        files = record["files"]
    except (OSError, ValueError, KeyError) as e:
        print("FAIL      %s: cannot read manifest (%s)" % (shown, e))
        return 1
    volatile = record.get("volatile_pattern")

    tally = {"identical": 0, "volatile": 0, "changed": 0, "missing": 0}
    lines = []
    for rel, rec in sorted(files.items()):
        path = os.path.join(root, *rel.split("/"))
        if not os.path.isfile(path):
            tally["missing"] += 1
            lines.append("  MISSING   %s" % rel)
            continue
        now = byte_digest(path)
        if now == rec["sha256"]:
            tally["identical"] += 1
            continue
        was_content = rec.get("content_sha256")
        if was_content and content_digest(path, volatile) == was_content:
            tally["volatile"] += 1
            lines.append("  VOLATILE  %s  differs only in text matching the "
                         "manifest's volatile pattern" % rel)
            continue
        tally["changed"] += 1
        lines.append("  CHANGED   %s  was %s... (%d bytes), now %s... (%d bytes)"
                     % (rel, rec["sha256"][:12], rec.get("bytes", -1), now[:12],
                        os.path.getsize(path)))

    failures = tally["changed"] + tally["missing"]
    if strict:
        failures += tally["volatile"]
    print("%-9s %s: %d files: %d identical, %d volatile-only, %d changed, "
          "%d missing" % ("FAIL" if failures else "OK", shown, len(files),
                          tally["identical"], tally["volatile"],
                          tally["changed"], tally["missing"]))
    for line in lines:
        print(line)
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", nargs="+", metavar="ARG",
                      help="MANIFEST followed by the files, dirs or globs to freeze")
    mode.add_argument("--check", nargs="+", metavar="MANIFEST")
    ap.add_argument("--volatile", default=DEFAULT_VOLATILE,
                    help="regex for text the content digest ignores "
                         "(default: ISO-8601 date-times)")
    ap.add_argument("--no-volatile", action="store_true",
                    help="record byte digests only")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing manifest")
    ap.add_argument("--strict", action="store_true",
                    help="treat a volatile-only difference as a failure")
    ap.add_argument("--root", help="repository root (default: found by walking "
                    "up from this script to CLAUDE.md or .git)")
    args = ap.parse_args(argv)

    root = os.path.realpath(args.root) if args.root else \
        os.path.realpath(find_root(os.path.dirname(os.path.abspath(__file__))))

    if args.write:
        if len(args.write) < 2:
            ap.error("--write needs a manifest and at least one file")
        return write(args.write[0], args.write[1:], root,
                     None if args.no_volatile else args.volatile, args.force)

    failures = sum(check(m, root, args.strict) for m in args.check)
    print("%s: %d manifests, %d failing files" % (PROG, len(args.check), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
