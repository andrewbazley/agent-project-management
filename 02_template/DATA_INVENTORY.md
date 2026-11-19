# Data inventory

Every dataset and output that is not wholly in git: what it is, what it would cost to make again,
and where each copy lives. A path listed here may be absent from a clone without failing the
citation check, so list a path here when it leaves git, not afterwards. `CLAUDE.md` §13 says when
data may be removed and when it must be offloaded first.

## Only copies

<!-- Anything that cannot be regenerated in reasonable time: raw instrument data, samples' only
measurements, outputs whose inputs are gone. Never moved or removed until a second verified copy
exists. One row per item. -->

| path | what it is | why it cannot be regenerated | other verified copy |
|---|---|---|---|

## Kept outside git

<!-- Large inputs and outputs left out of git and still where the work runs (this machine or the
cluster). The regenerate column says how and how long: the script, the download log entry, the
hours. -->

| path | what it is | where it lives | regenerate |
|---|---|---|---|

## Offloaded

<!-- Written by `tools/offload.py`; edit only the regenerate column by hand. Each row is a set
copied to lab storage and verified file by file against a manifest stored with it, whose digest is
the manifest column. "local copy" says whether this machine still holds it. -->

| local path | stored at | files | size | manifest | copied | checked | local copy | regenerate |
|---|---|---|---|---|---|---|---|---|
