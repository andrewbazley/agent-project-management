#!/usr/bin/env bash
#
# verify_all.sh -- run every verifier in the project from one command.
#
# Asserts: every stream verifier passes, every cited path resolves, every
# frozen manifest still matches its files, every indexed output directory
# names exactly what it holds, and every offloaded set is intact where it is
# stored. Also shows survey.py's budget warnings, which never fail the run.
#
# Why: checks that each have to be remembered separately are not run. One
# command, run before and after any change to results or records, makes "all
# checks pass" a statement that can be made and repeated, and a skipped check
# is reported as skipped rather than quietly counted as a pass.
#
# Steps, discovered by convention so a new stream needs no edit here:
#   - each tools/verify_*.py|sh at the root and in every top-level stream
#     (*/tools/), run with no arguments from the folder above its tools/;
#     it must exit non-zero on failure, and each output line starting with
#     SKIP is counted as a skipped check;
#   - check_citations.py over the whole repository;
#   - check_frozen.py --check on each *manifest*.json under */results/;
#   - make_index.py --check on every directory under */results/ and */spec/
#     that holds an INDEX.md;
#   - offload.py check (sizes only; a store not mounted here is a SKIP);
#   - survey.py --budget, whose WARN lines are counted and shown.
# Anything under an archive/ directory is left out.
#
# Reads: the repository. Writes: nothing.
# Exit status: 0 if every step passed (skips and warnings included), 1 otherwise.
#
# Usage: tools/verify_all.sh [-v]        -v prints every step's full output
#        PYTHON=/path/to/python3 tools/verify_all.sh

set -o pipefail

here=$(cd "$(dirname "$0")" && pwd)
root=$here
while [ ! -e "$root/CLAUDE.md" ] && [ ! -e "$root/.git" ]; do
    if [ "$root" = "/" ]; then
        echo "verify_all: no CLAUDE.md or .git above $here" >&2
        exit 2
    fi
    root=$(dirname "$root")
done

PYTHON=${PYTHON:-python3}
verbose=0
[ "${1:-}" = "-v" ] && verbose=1

steps=0 failed=0 skipped_steps=0 skipped_checks=0 warnings=0

run_step() {
    local name=$1 dir=$2 out status skips warns
    shift 2
    out=$(cd "$dir" && "$@" </dev/null 2>&1)
    status=$?
    skips=$(printf '%s\n' "$out" | grep -c '^SKIP')
    warns=$(printf '%s\n' "$out" | grep -c '^WARN')
    warnings=$((warnings + warns))
    steps=$((steps + 1))
    if [ "$status" -ne 0 ]; then
        failed=$((failed + 1))
        printf 'FAIL  %s (exit %d)\n' "$name" "$status"
        [ "$verbose" -eq 1 ] || printf '%s\n' "$out" | tail -n 40 | sed 's/^/      /'
    elif [ "$skips" -gt 0 ]; then
        skipped_steps=$((skipped_steps + 1))
        skipped_checks=$((skipped_checks + skips))
        printf 'SKIP  %s (passed, %d checks skipped)\n' "$name" "$skips"
        [ "$verbose" -eq 1 ] || printf '%s\n' "$out" | grep '^SKIP' | sed 's/^/      /'
    elif [ "$warns" -gt 0 ]; then
        printf 'WARN  %s (passed, %d warnings)\n' "$name" "$warns"
        [ "$verbose" -eq 1 ] || printf '%s\n' "$out" | grep '^WARN' | sed 's/^/      /'
    else
        printf 'PASS  %s\n' "$name"
    fi
    [ "$verbose" -eq 1 ] && printf '%s\n' "$out" | sed 's/^/      /'
    return 0
}

echo "verify_all: $root"

for v in "$root"/tools/verify_*.py "$root"/tools/verify_*.sh \
         "$root"/*/tools/verify_*.py "$root"/*/tools/verify_*.sh; do
    [ -f "$v" ] || continue
    [ "$(basename "$v")" = verify_all.sh ] && continue
    case $v in
        "$root"/archive/*) continue ;;
        *.py) run_step "${v#"$root"/}" "$(dirname "$(dirname "$v")")" "$PYTHON" "$v" ;;
        *.sh) run_step "${v#"$root"/}" "$(dirname "$(dirname "$v")")" bash "$v" ;;
    esac
done

run_step "citations" "$root" "$PYTHON" -I "$here/check_citations.py" --root "$root"

for results in "$root"/*/results; do
    [ -d "$results" ] || continue
    while IFS= read -r -d '' m; do
        run_step "frozen ${m#"$root"/}" "$root" \
            "$PYTHON" -I "$here/check_frozen.py" --root "$root" --check "$m"
    done < <(find "$results" -type f -name '*manifest*.json' \
                 -not -path '*/archive/*' -print0 | sort -z)
done

index_dirs=()
for base in "$root"/*/results "$root"/*/spec; do
    [ -d "$base" ] || continue
    while IFS= read -r -d '' f; do
        index_dirs+=("$(dirname "$f")")
    done < <(find "$base" -type f -name INDEX.md -not -path '*/archive/*' \
                 -print0 | sort -z)
done
if [ "${#index_dirs[@]}" -gt 0 ]; then
    run_step "indexes (${#index_dirs[@]} directories)" "$root" \
        "$PYTHON" -I "$here/make_index.py" --root "$root" --check "${index_dirs[@]}"
fi

if [ -f "$root/DATA_INVENTORY.md" ]; then
    run_step "offloaded data" "$root" "$PYTHON" -I "$here/offload.py" --root "$root" check
fi
run_step "budget" "$root" "$PYTHON" -I "$here/survey.py" --root "$root" --budget

printf 'verify_all: %d steps, %d failed, %d with skipped checks (%d checks skipped), %d warnings\n' \
    "$steps" "$failed" "$skipped_steps" "$skipped_checks" "$warnings"
[ "$failed" -eq 0 ]
