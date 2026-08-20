#!/bin/bash

set -e

source "$(dirname "$0")/common.sh"

print_header "🚀 GENERATING PORTFOLIO"

mkdir -p "$TARGET/portfolio/articles"
mkdir -p "$TARGET/portfolio/assets"
mkdir -p "$TARGET/portfolio/project-pages"

if [ -d "$SOURCE/PORTFOLIO_ASSETS" ]; then

execute_or_dry_run \
"Portfolio Assets Migration" \
"rsync -av \
'$SOURCE/PORTFOLIO_ASSETS/' \
'$TARGET/portfolio/assets/'"

fi

find "$SOURCE/DEV" -maxdepth 1 -type d -name "PRJ-*" | while read project

do

    PROJECT_NAME=$(basename "$project")

    mkdir -p "$TARGET/portfolio/project-pages/$PROJECT_NAME"

    execute_or_dry_run \
    "Portfolio Project Export: $PROJECT_NAME" \
    "rsync -av \
    --include='README.md' \
    --include='docs/***' \
    --exclude='*' \
    '$project/' \
    '$TARGET/portfolio/project-pages/$PROJECT_NAME/'"

 done

print_header "✅ PORTFOLIO GENERATION COMPLETED"