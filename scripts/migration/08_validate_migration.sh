#!/bin/bash

set -e

source "$(dirname "$0")/common.sh"

print_header "🚀 VALIDATING MIGRATION"

REQUIRED=(
"$TARGET/governance"
"$TARGET/dev/rag"
"$TARGET/shared"
"$TARGET/observability"
"$TARGET/portfolio"
)

for item in "${REQUIRED[@]}"
do

    if [ -d "$item" ]; then

        echo "✅ Validated: $item"

    else

        echo "❌ Missing: $item"
        exit 1

    fi

done

print_header "✅ VALIDATION COMPLETED"