"""
records.py -- read and update DATA_INVENTORY.md for the other tools.

DATA_INVENTORY.md lists every dataset and output that is not wholly in git,
in tables whose first column holds a project-relative path in backticks. Its
"## Offloaded" section is written by offload.py with fixed columns, so that a
committed record says where each offloaded set went and how to check it.

The checks use it to tell a path that is missing from a path that is recorded
as living elsewhere: check_citations.py accepts a citation under any listed
path, and check_frozen.py and make_index.py accept a file absent under an
offloaded one.

Functions
    inventoried(root)           every listed path, with its section
    offloaded(root)             the Offloaded rows, as dicts keyed by column
    covering(rel, paths)        the listed path equal to or above rel, or None
    upsert_offloaded(root, row) add a row, or replace the one with its path
"""

import os
import re

FILE = "DATA_INVENTORY.md"
SECTION = "Offloaded"
COLUMNS = ("local path", "stored at", "files", "size", "manifest", "copied",
           "checked", "local copy", "regenerate")
PATH_COLUMNS = ("local path", "stored at", "manifest")

TICKED = re.compile(r"`([^`]+)`")
SEPARATOR = re.compile(r"^:?-+:?$")


def norm(p):
    p = p.strip().replace(os.sep, "/")
    while p.startswith("./"):
        p = p[2:]
    return p.rstrip("/") or p


def _read(root):
    path = os.path.join(root, FILE)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return fh.read().splitlines()


def _rows(lines):
    """(section, header, line number, cells) for every body row of a table."""
    section, header = None, None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            section, header = line[3:].strip(), None
            continue
        s = line.strip()
        if not s.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
        elif not all(SEPARATOR.match(c) for c in cells if c):
            yield section, header, i, cells


def inventoried(root):
    out = []
    for section, _, _, cells in _rows(_read(root)):
        for p in TICKED.findall(cells[0]):
            if not re.search(r"[<>*?]", p):
                out.append((norm(p), section))
    return out


def offloaded(root):
    out = []
    for section, header, _, cells in _rows(_read(root)):
        if (section or "").lower() != SECTION.lower():
            continue
        row = dict(zip(header, cells))
        for col in PATH_COLUMNS:
            if col in row:
                ticks = TICKED.findall(row[col])
                row[col] = ticks[0] if ticks else row[col]
        if TICKED.search(cells[0]) and not re.search(r"[<>]", cells[0]):
            row["local path"] = norm(row["local path"])
            out.append(row)
    return out


def covering(rel, paths):
    rel = norm(rel)
    for p in paths:
        if rel == p or rel.startswith(p + "/"):
            return p
    return None


def _format(row):
    cells = []
    for col in COLUMNS:
        v = str(row.get(col, "")).replace("|", "/").replace("\n", " ").strip()
        cells.append("`%s`" % v if col in PATH_COLUMNS and v else v)
    return "| " + " | ".join(cells) + " |"


def upsert_offloaded(root, row):
    path = os.path.join(root, FILE)
    lines = _read(root)
    if not lines:
        lines = ["# Data inventory", ""]
    line = _format(row)

    existing = [(i, cells) for section, _, i, cells in _rows(lines)
                if (section or "").lower() == SECTION.lower()]
    for i, cells in existing:
        if norm("".join(TICKED.findall(cells[0]))) == norm(row["local path"]):
            lines[i] = line
            break
    else:
        start = next((i for i, l in enumerate(lines)
                      if l.strip().lower() == "## " + SECTION.lower()), None)
        if start is None:
            lines += ["", "## " + SECTION, "",
                      "| " + " | ".join(COLUMNS) + " |",
                      "|" + "---|" * len(COLUMNS), line]
        else:
            # After the table's last row, or after its separator if it is empty.
            end = start + 1
            seen_table = False
            for j in range(start + 1, len(lines)):
                if lines[j].startswith("## "):
                    break
                if lines[j].strip().startswith("|"):
                    seen_table, end = True, j + 1
                elif seen_table:
                    break
            if not seen_table:
                lines[end:end] = ["", "| " + " | ".join(COLUMNS) + " |",
                                  "|" + "---|" * len(COLUMNS)]
                end += 3
            lines.insert(end, line)

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
