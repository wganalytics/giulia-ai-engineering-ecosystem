#!/bin/bash

set -e

source "$(dirname "$0")/common.sh"

print_header "🚀 STARTING GOVERNANCE MIGRATION"

validate_directory "$SOURCE/governance"

mkdir -p "$TARGET/governance/operational-memory"
mkdir -p "$TARGET/governance/architecture-decisions"
mkdir -p "$TARGET/governance/projects"

execute_or_dry_run \
"Operational Memory Migration" \
"rsync -av \
'$SOURCE/governance/operational-memory/' \
'$TARGET/governance/operational-memory/'"

execute_or_dry_run \
"Architecture Decisions Migration" \
"rsync -av \
'$SOURCE/governance/architecture-decisions/' \
'$TARGET/governance/architecture-decisions/'"

execute_or_dry_run \
"Project Governance Migration" \
"rsync -av \
'$SOURCE/governance/projects/' \
'$TARGET/governance/projects/'"

print_header "✅ GOVERNANCE MIGRATION COMPLETED"