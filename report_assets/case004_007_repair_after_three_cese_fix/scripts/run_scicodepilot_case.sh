#!/usr/bin/env bash

set -uo pipefail

ROOT="/d/Git/My_Git_Project/BugsInPy_0616_2"
SCP="$ROOT/scicodepilot-dev-main"
WORK="$ROOT/BugsInPy_Workdir"
OUT="$ROOT/external_experiments_0616_2"

if [ "$#" -ne 2 ]; then
    echo "Usage: bash run_scicodepilot_case.sh CASE_NAME TEST_COMMAND"
    exit 2
fi

CASE_NAME="$1"
TEST_COMMAND="$2"

REPO="$WORK/$CASE_NAME/youtube-dl"
CASE_OUT="$OUT/$CASE_NAME"
LOG_DIR="$CASE_OUT/logs"
OUTPUT_DIR="$CASE_OUT/outputs"

mkdir -p "$LOG_DIR"
mkdir -p "$OUTPUT_DIR"

if [ ! -d "$REPO/youtube_dl" ]; then
    echo "ERROR: youtube_dl source directory not found:"
    echo "$REPO/youtube_dl"
    exit 3
fi

REPO_WIN="$(cygpath -w "$REPO")"

run_mode() {
    MODE="$1"

    MODE_OUT="$OUTPUT_DIR/$MODE"
    MODE_LOG="$LOG_DIR/${MODE}.log"

    rm -rf "$MODE_OUT"
    mkdir -p "$MODE_OUT"

    MODE_OUT_WIN="$(cygpath -w "$MODE_OUT")"

    cd "$SCP" || exit 4

    echo "========================================"
    echo "Case: $CASE_NAME"
    echo "Mode: $MODE"
    echo "Command: $TEST_COMMAND"
    echo "========================================"

    if [ "$MODE" = "repair" ]; then
        python scripts/run_external_repo_smoke.py \
            --repo-path "$REPO_WIN" \
            --command "$TEST_COMMAND" \
            --mode repair \
            --copy-workspace \
            --confirm-apply \
            --output-dir "$MODE_OUT_WIN" \
            > "$MODE_LOG" 2>&1
    else
        python scripts/run_external_repo_smoke.py \
            --repo-path "$REPO_WIN" \
            --command "$TEST_COMMAND" \
            --mode "$MODE" \
            --copy-workspace \
            --output-dir "$MODE_OUT_WIN" \
            > "$MODE_LOG" 2>&1
    fi

    RC=$?

    echo "$RC" \
        > "$LOG_DIR/${MODE}_script_return_code.txt"

    echo "$CASE_NAME / $MODE script return code: $RC"
}

run_mode diagnosis
run_mode repair-plan
run_mode repair

echo "Finished: $CASE_NAME"
echo "Results: $CASE_OUT"
