#!/bin/bash

set -e

source "$(dirname "$0")/common.sh"

print_header "🚀 STARTING RUNTIME MIGRATION"

validate_directory "$SOURCE/DEV"

mkdir -p "$TARGET/dev/rag"

find "$SOURCE/DEV" -maxdepth 1 -type d -name "PRJ-*" | while read project

do

    PROJECT_NAME=$(basename "$project")

    mkdir -p "$TARGET/dev/rag/$PROJECT_NAME"

    execute_or_dry_run \
    "Runtime Migration: $PROJECT_NAME" \
    "rsync -av \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'vector_db' \
    --exclude 'uploads' \
    --exclude '*.sqlite3' \
    --exclude 'data/neo4j'
    --exclude 'data/neo4j/**'
    '$project/' \
    '$TARGET/dev/rag/$PROJECT_NAME/'"

 done

print_header "✅ RUNTIME MIGRATION COMPLETED"