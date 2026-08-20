#!/bin/bash

set -e

source "$(dirname "$0")/common.sh"

print_header "🚀 STARTING PUBLIC EXPORT"

mkdir -p "$PUBLIC_EXPORT"

execute_or_dry_run \
"Portfolio Export" \
"rsync -av \
--exclude '.DS_Store' \
--exclude '.gitkeep' \
'$TARGET/portfolio/' \
'$PUBLIC_EXPORT/portfolio/'"

execute_or_dry_run \
"Projects Export" \
"rsync -av \
--exclude '.env' \
--exclude '.DS_Store' \
--exclude '.pytest_cache' \
--exclude '__pycache__' \
--exclude '*.pyc' \
--exclude '.gitkeep' \
--exclude 'data' \
--exclude 'vector_db' \
--exclude 'uploads' \
--exclude 'neo4j' \
'$TARGET/dev/rag/' \
'$PUBLIC_EXPORT/projects/'"

execute_or_dry_run \
"Governance Export" \
"rsync -av \
--exclude '.DS_Store' \
--exclude '.gitkeep' \
'$TARGET/governance/architecture-decisions/' \
'$PUBLIC_EXPORT/governance/architecture-decisions/'"

print_header "✅ PUBLIC EXPORT COMPLETED"