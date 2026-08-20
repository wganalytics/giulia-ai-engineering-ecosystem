#!/bin/bash

set -e

source "$(dirname "$0")/common.sh"

print_header "🚀 STARTING OBSERVABILITY MIGRATION"

mkdir -p "$TARGET/observability/reports"
mkdir -p "$TARGET/observability/logs"
mkdir -p "$TARGET/observability/metrics"

if [ -d "$SOURCE/infra" ]; then

execute_or_dry_run \
"Infrastructure Reports Migration" \
rsync -av \
--exclude '__pycache__' \
--exclude '*.pyc' \
--exclude '.sync_state.json' \
--include='*.md' \
--include='*.json' \
--include='*/' \
--exclude='*' \
'$SOURCE/infra/' \
'$TARGET/observability/reports/'

fi

print_header "✅ OBSERVABILITY MIGRATION COMPLETED"