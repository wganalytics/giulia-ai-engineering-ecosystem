#!/bin/bash

set -e

source "$(dirname "$0")/common.sh"

print_header "🚀 STARTING SHARED MIGRATION"

mkdir -p "$TARGET/shared/governance"
mkdir -p "$TARGET/shared/infra"
mkdir -p "$TARGET/shared/articles"

validate_directory "$SOURCE/governance"

execute_or_dry_run \
"Planning Docs Migration" \
"rsync -av \
'$SOURCE/governance/' \
'$TARGET/shared/governance/'"

if [ -d "$SOURCE/infra" ]; then

execute_or_dry_run \
"Infra Migration" \
"rsync -av \
'$SOURCE/infra/' \
'$TARGET/shared/infra/'"

fi

if [ -d "$SOURCE/ARTIGOS" ]; then

execute_or_dry_run \
"Articles Migration" \
"rsync -av \
'$SOURCE/ARTIGOS/' \
'$TARGET/shared/articles/'"

fi

print_header "✅ SHARED MIGRATION COMPLETED"