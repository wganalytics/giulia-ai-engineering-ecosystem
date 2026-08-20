#!/bin/bash

set -e

source "$(dirname "$0")/../../config/migration.env"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"

LOG_FILE="$LOG_DIR/$(basename "$0" .sh)_${TIMESTAMP}.log"

exec > >(tee -a "$LOG_FILE") 2>&1

print_header() {

    echo ""
    echo "================================================="
    echo "$1"
    echo "================================================="
    echo ""

}

validate_directory() {

    if [ ! -d "$1" ]; then

        echo "❌ Missing directory: $1"
        exit 1

    fi

}

execute_or_dry_run() {

    local LABEL="$1"
    local COMMAND="$2"

    echo "🚀 Executing: $LABEL"

    if [ "$DRY_RUN" = true ]; then

        echo "[DRY RUN]"
        echo "$COMMAND"

    else

        eval "$COMMAND"

    fi

    echo ""

}

echo "🧠 Common migration framework loaded."
echo "📄 Log file:"
echo "$LOG_FILE"