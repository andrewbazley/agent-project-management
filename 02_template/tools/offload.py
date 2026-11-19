#!/usr/bin/env python3
"""
offload.py -- keep costly outputs on lab storage, with a verified copy and a
committed record of where they went.

Commands
    copy SRC --to BASE --cost TEXT
        Copy SRC, a file or directory inside the project, to BASE/<SRC's
        project-relative path>. Each file is hashed as it is read and again
        after it is written, and the copy fails on any difference. The digests
        go into OFFLOAD_MANIFEST.json at the destination (inside the copied
        directory, or beside a copied file), and a row in DATA_INVENTORY.md
        "Offloaded" records the location, the counts, the manifest's own
        digest and what regenerating the data would cost. Nothing local
        changes. A rerun after an interruption keeps the files already copied.
    prune SRC [--keep-under SIZE] [--yes]
        Remove the local copy of an offloaded set, once the stored copy has
        been re-hashed against its manifest. A local file is removed only if
        its digest matches the manifest. Markdown files, manifests and files no
        larger than --keep-under (default 1MB) stay, so the index, reports and
        summary tables can still be read here, and OFFLOADED.md is written in
        place of the rest saying where it went. Without --yes, prune only
        lists what it would remove.
    restore SRC [--yes]
        Copy the stored files back, verifying each, without overwriting a
        local file that differs. Without --yes, lists what it would copy.
    check [SRC ...] [--full] [--record]
        For every Offloaded row, or the ones named: the manifest at the
        location is the one recorded, and every file is there at its recorded
        size. --full re-hashes every file; --record, with --full, writes
        today's date into the row's "checked" column. A location that cannot
        be reached from this machine is reported on a line beginning SKIP,
        which verify_all.sh counts as a skipped check, never as a pass.

Why
    Some outputs take hours of download and compute to make again and are too
    large for git. Deleting them throws the hours away, and keeping them on a
    laptop leaves the only copy on the least safe disk. Moving them is safe only
    if the copy is verified before anything local is removed, and only useful if
    the record of where they went is committed, so a later session can find
    them without anyone remembering. The manifest's digest is in that record,
    so a stored copy that was changed or replaced afterwards is detected.

Where BASE should be
    A directory on backed-up storage mounted on this machine (a lab server
    share, or the cluster file system when run there), named for the project in
    README.md section 6. copy refuses a BASE on the same volume as the project
    unless --same-volume is given, because a second copy on the same disk does
    not survive the disk. check reports a missing location as SKIP when its
    nearest existing parent is on the project's volume (the share is not
    mounted) and as FAIL when it is on another volume (the share is mounted
    and the copy is gone); a set copied with --same-volume is therefore
    reported as SKIP, not FAIL, if it disappears.

Reads
    SRC, the stored copy, DATA_INVENTORY.md.
Writes
    The stored copy and its manifest; DATA_INVENTORY.md; with prune --yes, the
    removal of local files and OFFLOADED.md; with restore --yes, local files.
Exit status
    0 on success, 1 if a copy or check failed, 2 on a usage error.

Usage
    python3 tools/offload.py copy 01_align/work/bam --to /mnt/lab/me/project \\
        --cost "6 h download (data/DOWNLOAD_LOG.md) and 9 h alignment (hpc/align.sbatch)"
    python3 tools/offload.py prune 01_align/work/bam [--yes]
    python3 tools/offload.py restore 01_align/work/bam [--yes]
    python3 tools/offload.py check [--full --record] [SRC ...]
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import records  # noqa: E402

PROG = "offload"
MANIFEST = "OFFLOAD_MANIFEST.json"
STUB = "OFFLOADED.md"
CHUNK = 1 << 20
IGNORED_NAMES = frozenset({".DS_Store"})


class Failure(Exception):
    pass


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


def today():
    return datetime.date.today().isoformat()


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


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def manifest_path(location, kind):
    return os.path.join(location, MANIFEST) if kind == "dir" \
        else location + "." + MANIFEST


def stub_path(local, kind):
    return os.path.join(local, STUB) if kind == "dir" else local + "." + STUB


def members(src):
    """(name relative to the set's directory, absolute path) of each member."""
    if not os.path.isdir(src) or os.path.islink(src):
        return [(os.path.basename(src), src)]
    out = []
    for d, dirs, files in os.walk(src):
        for name in sorted(dirs):
            if os.path.islink(os.path.join(d, name)):
                files.append(name)
        dirs[:] = sorted(x for x in dirs if not os.path.islink(os.path.join(d, x)))
        for f in files:
            p = os.path.join(d, f)
            rel = os.path.relpath(p, src).replace(os.sep, "/")
            if f in IGNORED_NAMES or rel in (MANIFEST, STUB):
                continue
            out.append((rel, p))
    return sorted(out)


def copy_file(src, dst, expect=None):
    """Copy src to dst, verify the written bytes, and return the digest."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if expect is None and os.path.isfile(dst) and \
            os.path.getsize(dst) == os.path.getsize(src):
        digest = sha256(src)
        if sha256(dst) == digest:
            return digest
    tmp = dst + ".partial"
    h = hashlib.sha256()
    with open(src, "rb") as fin, open(tmp, "wb") as fout:
        for block in iter(lambda: fin.read(CHUNK), b""):
            h.update(block)
            fout.write(block)
        fout.flush()
        os.fsync(fout.fileno())
    digest = h.hexdigest()
    if sha256(tmp) != digest or (expect and digest != expect):
        os.remove(tmp)
        raise Failure("%s: copy does not match its source" % dst)
    os.replace(tmp, dst)
    try:
        os.utime(dst, (os.stat(src).st_atime, os.stat(src).st_mtime))
    except OSError:
        pass  # some network shares refuse timestamps; the content is what matters
    return digest


def project_rel(root, src):
    """SRC as a project-relative path, whether given from here or from the root."""
    p = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(src))),
                     os.path.basename(os.path.abspath(src)))
    rel = os.path.relpath(p, root)
    if rel.startswith("..") and not os.path.isabs(src):
        rel = src
    return records.norm(rel)


def layout(root, rel, location, kind):
    """(local path, local directory of the members, stored directory of them)."""
    local = os.path.join(root, *rel.split("/"))
    if kind == "dir":
        return local, local, location
    return local, os.path.dirname(local), os.path.dirname(location)


def reachable(location, root):
    """Whether the volume a location lives on is mounted here."""
    d = location
    while not os.path.exists(d):
        parent = os.path.dirname(d)
        if parent == d:
            return False
        d = parent
    return os.stat(d).st_dev != os.stat(root).st_dev


def load_manifest(row, root):
    """The stored manifest, after checking its digest against the record."""
    location = row["stored at"]
    for kind in ("dir", "file"):
        mpath = manifest_path(location, kind)
        if os.path.isfile(mpath):
            break
    else:
        return None, None
    with open(mpath, "rb") as fh:
        data = fh.read()
    if hashlib.sha256(data).hexdigest()[:16] != row.get("manifest", ""):
        raise Failure("the manifest at %s is not the one recorded (digest %s)"
                      % (mpath, row.get("manifest", "")))
    return json.loads(data.decode("utf-8")), mpath


def verify(row, root, full):
    """('OK' | 'FAIL' | 'SKIP', detail lines, manifest)."""
    try:
        man, _ = load_manifest(row, root)
    except (Failure, ValueError, OSError) as e:
        return "FAIL", [str(e)], None
    if man is None:
        if reachable(row["stored at"], root):
            return "FAIL", ["the storage is mounted but nothing is at %s"
                            % row["stored at"]], None
        return "SKIP", ["%s is not reachable from this machine"
                        % row["stored at"]], None
    _, _, dest_dir = layout(root, row["local path"], row["stored at"], man["kind"])
    problems = []
    for name, e in sorted(man["files"].items()):
        p = os.path.join(dest_dir, *name.split("/"))
        if "link" in e:
            if not os.path.islink(p) or os.readlink(p) != e["link"]:
                problems.append("link differs: %s" % name)
        elif not os.path.isfile(p):
            problems.append("missing: %s" % name)
        elif os.path.getsize(p) != e["bytes"]:
            problems.append("size differs: %s" % name)
        elif full and sha256(p) != e["sha256"]:
            problems.append("content differs: %s" % name)
    return ("FAIL" if problems else "OK"), problems, man


def find_row(root, src):
    rel = project_rel(root, src)
    for row in records.offloaded(root):
        if row["local path"] == rel:
            return row
    raise Failure("%s has no row in %s; run copy first" % (rel, records.FILE))


def cmd_copy(root, args):
    rel = project_rel(root, args.src)
    src = os.path.join(root, *rel.split("/"))
    if rel == "." or rel.startswith(".."):
        raise Failure("%s is not inside the project" % args.src)
    if not os.path.lexists(src):
        raise Failure("%s does not exist" % args.src)
    base = os.path.realpath(os.path.expanduser(args.to))
    if not os.path.isdir(base):
        raise Failure("%s is not a directory here; is the storage mounted?"
                      % args.to)
    if (base + os.sep).startswith(root + os.sep):
        raise Failure("the destination is inside the project")
    if os.stat(base).st_dev == os.stat(root).st_dev and not args.same_volume:
        raise Failure("%s is on the same volume as the project, so it is not a "
                      "second copy; pass --same-volume if that is intended"
                      % base)
    for row in records.offloaded(root):
        if row["local path"] == rel and row.get("local copy", "") \
                .startswith("removed"):
            raise Failure("%s was offloaded and pruned; restore it before "
                          "copying again" % rel)

    kind = "dir" if os.path.isdir(src) and not os.path.islink(src) else "file"
    location = os.path.join(base, *rel.split("/"))
    _, _, dest_dir = layout(root, rel, location, kind)
    items = members(src)
    mpath = manifest_path(location, kind)
    if os.path.isfile(mpath) and not args.replace:
        with open(mpath, encoding="utf-8") as fh:
            old = set(json.load(fh)["files"])
        dropped = old - {m for m, _ in items}
        if dropped:
            raise Failure("the stored copy holds %d files that %s no longer "
                          "has (e.g. %s); pass --replace to drop them from the "
                          "record" % (len(dropped), rel, sorted(dropped)[0]))

    entries, total = {}, 0
    for i, (name, path) in enumerate(items, 1):
        target = os.path.join(dest_dir, *name.split("/"))
        if os.path.islink(path):
            link = os.readlink(path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if os.path.lexists(target) and not (
                    os.path.islink(target) and os.readlink(target) == link):
                os.remove(target)
            if not os.path.lexists(target):
                os.symlink(link, target)
            entries[name] = {"link": link}
            continue
        size = os.path.getsize(path)
        entries[name] = {"bytes": size, "sha256": copy_file(path, target)}
        total += size
        if args.verbose or i % 200 == 0:
            print("  %d/%d %s" % (i, len(items), name), file=sys.stderr)

    manifest = {"format": 1, "kind": kind, "source": rel,
                "written": datetime.datetime.now().astimezone()
                .isoformat(timespec="seconds"),
                "files": entries}
    data = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("utf-8")
    with open(mpath, "wb") as fh:
        fh.write(data)
    nfiles = sum(1 for e in entries.values() if "sha256" in e)
    records.upsert_offloaded(root, {
        "local path": rel, "stored at": location, "files": nfiles,
        "size": human(total), "manifest": hashlib.sha256(data).hexdigest()[:16],
        "copied": today(), "checked": today(), "local copy": "present",
        "regenerate": args.cost})
    print("%s: copied and verified %d files (%s) of %s to %s; recorded in %s"
          % (PROG, nfiles, human(total), rel, location, records.FILE))
    return 0


def keep(name, size, keep_under):
    base = os.path.basename(name).lower()
    return base.endswith(".md") or ("manifest" in base and base.endswith(".json")) \
        or size <= keep_under


def cmd_prune(root, args):
    row = find_row(root, args.src)
    if row.get("local copy", "").startswith("removed"):
        raise Failure("%s is already pruned (%s)" % (row["local path"],
                                                      row["local copy"]))
    status, problems, man = verify(row, root, full=True)
    if status != "OK":
        raise Failure("the stored copy of %s did not verify (%s); nothing "
                      "removed" % (row["local path"], "; ".join(problems[:3])))
    local, local_dir, _ = layout(root, row["local path"], row["stored at"],
                                 man["kind"])
    remove, kept, differ, freed = [], 0, [], 0
    for name, e in sorted(man["files"].items()):
        p = os.path.join(local_dir, *name.split("/"))
        if "link" in e or not os.path.isfile(p) or os.path.islink(p):
            continue
        size = os.path.getsize(p)
        if keep(name, size, args.keep_under):
            kept += 1
        elif sha256(p) != e["sha256"]:
            differ.append(name)
        else:
            remove.append(p)
            freed += size
    print("%s: %s: remove %d files (%s); keep %d small files and documents%s"
          % (PROG, row["local path"], len(remove), human(freed), kept,
             "; keep %d that differ from the stored copy" % len(differ)
             if differ else ""))
    for name in differ:
        print("  differs from the stored copy, kept: %s" % name)
    if not args.yes:
        print("%s: nothing removed; pass --yes to remove" % PROG)
        return 0

    for p in remove:
        os.remove(p)
    if man["kind"] == "dir":
        for d, _, _ in sorted(os.walk(local_dir), key=lambda t: -len(t[0])):
            if d != local_dir and not os.listdir(d):
                os.rmdir(d)
    with open(stub_path(local, man["kind"]), "w", encoding="utf-8") as fh:
        fh.write(
            "# Offloaded %s\n\n"
            "%d files (%s) of this %s are stored at `%s`, verified against the "
            "manifest kept there (digest %s). Markdown files, manifests and "
            "files of %s or less were kept here.\n\n"
            "Restore with `python3 tools/offload.py restore %s --yes`.\n\n"
            "Regenerating it would take: %s\n\n"
            "The record is the Offloaded table in `%s`.\n"
            % (today(), len(remove), human(freed),
               "directory" if man["kind"] == "dir" else "file's set",
               row["stored at"], row["manifest"], human(args.keep_under),
               row["local path"], row.get("regenerate", ""), records.FILE))
    row["local copy"] = "removed %s" % today()
    row["checked"] = today()
    records.upsert_offloaded(root, row)
    print("%s: removed %d files; wrote %s"
          % (PROG, len(remove), os.path.relpath(stub_path(local, man["kind"]),
                                                root)))
    return 0


def cmd_restore(root, args):
    row = find_row(root, args.src)
    status, problems, man = verify(row, root, full=True)
    if status != "OK":
        raise Failure("the stored copy of %s did not verify (%s)"
                      % (row["local path"], "; ".join(problems[:3])))
    local, local_dir, dest_dir = layout(root, row["local path"],
                                        row["stored at"], man["kind"])
    todo, conflicts, size = [], [], 0
    for name, e in sorted(man["files"].items()):
        p = os.path.join(local_dir, *name.split("/"))
        src = os.path.join(dest_dir, *name.split("/"))
        if "link" in e:
            if not os.path.lexists(p):
                todo.append((name, src, p, e))
            continue
        if os.path.isfile(p):
            if os.path.getsize(p) != e["bytes"] or sha256(p) != e["sha256"]:
                conflicts.append(name)
            continue
        todo.append((name, src, p, e))
        size += e["bytes"]
    print("%s: %s: copy back %d files (%s)%s"
          % (PROG, row["local path"], len(todo), human(size),
             "; %d local files differ and are left alone" % len(conflicts)
             if conflicts else ""))
    for name in conflicts:
        print("  local file differs, not overwritten: %s" % name)
    if not args.yes:
        print("%s: nothing copied; pass --yes to restore" % PROG)
        return 0
    for name, src, p, e in todo:
        if "link" in e:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            os.symlink(e["link"], p)
        else:
            copy_file(src, p, expect=e["sha256"])
    stub = stub_path(local, man["kind"])
    if os.path.isfile(stub):
        os.remove(stub)
    row["local copy"] = "restored %s" % today()
    records.upsert_offloaded(root, row)
    print("%s: restored %d files" % (PROG, len(todo)))
    return 0


def cmd_check(root, args):
    rows = records.offloaded(root)
    if args.src:
        wanted = {project_rel(root, s) for s in args.src}
        unknown = wanted - {r["local path"] for r in rows}
        if unknown:
            raise Failure("no Offloaded row for %s" % ", ".join(sorted(unknown)))
        rows = [r for r in rows if r["local path"] in wanted]
    failed = 0
    for row in rows:
        status, problems, man = verify(row, root, args.full)
        if status == "SKIP":
            print("SKIP      %s: %s" % (row["local path"], problems[0]))
            continue
        if status == "FAIL":
            failed += 1
            print("FAIL      %s" % row["local path"])
            for line in problems[:10]:
                print("  " + line)
            if len(problems) > 10:
                print("  and %d more" % (len(problems) - 10))
            continue
        print("OK        %s: %d files at %s%s"
              % (row["local path"], len(man["files"]), row["stored at"],
                 ", re-hashed" if args.full else ", sizes only"))
        if args.record and args.full:
            row["checked"] = today()
            records.upsert_offloaded(root, row)
    print("%s: %d offloaded sets checked, %d failing" % (PROG, len(rows), failed))
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="project root (default: found by walking up "
                    "from this script to CLAUDE.md or .git)")
    sub = ap.add_subparsers(dest="command")

    p = sub.add_parser("copy", help="copy a set to storage and record it")
    p.add_argument("src")
    p.add_argument("--to", required=True, metavar="BASE")
    p.add_argument("--cost", required=True,
                   help="what regenerating it would take, with the scripts")
    p.add_argument("--same-volume", action="store_true")
    p.add_argument("--replace", action="store_true",
                   help="allow the new manifest to drop files the stored one has")
    p.add_argument("-v", "--verbose", action="store_true")

    p = sub.add_parser("prune", help="remove the local copy of an offloaded set")
    p.add_argument("src")
    p.add_argument("--keep-under", type=parse_size, default=parse_size("1MB"),
                   metavar="SIZE")
    p.add_argument("--yes", action="store_true")

    p = sub.add_parser("restore", help="copy an offloaded set back")
    p.add_argument("src")
    p.add_argument("--yes", action="store_true")

    p = sub.add_parser("check", help="confirm the stored copies are intact")
    p.add_argument("src", nargs="*")
    p.add_argument("--full", action="store_true")
    p.add_argument("--record", action="store_true")

    args = ap.parse_args(argv)
    if not args.command:
        ap.print_help()
        return 2
    root = os.path.realpath(args.root) if args.root else \
        os.path.realpath(find_root(os.path.dirname(os.path.abspath(__file__))))
    try:
        return {"copy": cmd_copy, "prune": cmd_prune, "restore": cmd_restore,
                "check": cmd_check}[args.command](root, args)
    except Failure as e:
        print("%s: %s" % (PROG, e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
