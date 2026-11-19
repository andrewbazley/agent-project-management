# tools

Record-keeping checks shared by every stream. Python 3.8+ standard library and
bash 3.2; each finds the repository root by walking up to `CLAUDE.md` or `.git`,
and each opens with a docstring giving the full rules.

| tool | asserts | run |
|---|---|---|
| `check_citations.py` | Every path a Markdown document cites (code span or link) resolves from the document's directory, its stream folder or the root, or is declared in `citation_exceptions.txt`; an unused exception also fails. Ambiguous bare names are reported, not failed. | `python3 tools/check_citations.py [DOC.md ...]` |
| `check_frozen.py` | Frozen files match the SHA-256 digests in a manifest. A difference confined to timestamps is reported as volatile-only and passes unless `--strict`. | `python3 tools/check_frozen.py --write MANIFEST FILES...` then `--check MANIFEST...` |
| `make_index.py` | An output directory's INDEX.md names every file in it and nothing absent; `--draft` prints rows for missing files with the producing script found by searching the scripts. | `python3 tools/make_index.py --check DIR...` or `--draft DIR` |
| `verify_all.sh` | Runs every stream verifier and the three checks above; prints PASS, FAIL or SKIP per step and a summary line; exits non-zero if any step failed. | `tools/verify_all.sh [-v]` |

Streams add their own checks as `<stream>/tools/verify_<stage>.py` (or `.sh`).
`verify_all.sh` finds them by that name, runs each with no arguments from the
stream folder, and treats a non-zero exit as a failure. A verifier that cannot
run a check prints a line beginning `SKIP`; those are counted and shown, never
counted as passes.

Run `tools/verify_all.sh` before and after any change to results or records.
