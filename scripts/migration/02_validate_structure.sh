#!/bin/bash

# =========================================================
# GIULIA AI ENGINEERING ECOSYSTEM
# STRUCTURE VALIDATION SCRIPT
# =========================================================

set -e

echo ""
echo "🚀 STARTING STRUCTURE VALIDATION..."
echo ""

# =========================================================
# CONFIG
# =========================================================

MONOREPO="$HOME/Developer/giulia-ai-engineering-ecosystem"

# =========================================================
# REQUIRED ROOT STRUCTURE
# =========================================================

REQUIRED_DIRS=(
"ecosystem"
"dev"
"governance"
"observability"
"portfolio"
"publishing"
"website"
"registry"
"shared"
"docs"
"scripts"
"deployment"
)

# =========================================================
# GOVERNANCE STRUCTURE
# =========================================================

GOVERNANCE_DIRS=(
"governance/operational-memory"
"governance/snapshots"
"governance/architecture-decisions"
"governance/onboarding"
"governance/standards"
"governance/sdd"
"governance/tdd"
"governance/traceability"
)

# =========================================================
# OBSERVABILITY STRUCTURE
# =========================================================

OBSERVABILITY_DIRS=(
"observability/metrics"
"observability/traces"
"observability/dashboards"
"observability/telemetry"
"observability/profiling"
"observability/reports"
)

# =========================================================
# PORTFOLIO STRUCTURE
# =========================================================

PORTFOLIO_DIRS=(
"portfolio/articles"
"portfolio/screenshots"
"portfolio/architecture-showcase"
"portfolio/project-pages"
)

# =========================================================
# VALIDATION FUNCTION
# =========================================================

validate_directory() {
    DIR_PATH="$1"

    if [ -d "$MONOREPO/$DIR_PATH" ]; then
        echo "✅ $DIR_PATH"
    else
        echo "❌ MISSING: $DIR_PATH"
        FAILED=1
    fi
}

# =========================================================
# START VALIDATION
# =========================================================

FAILED=0

echo ""
echo "📁 Validating root structure..."
echo ""

for dir in "${REQUIRED_DIRS[@]}"
do
    validate_directory "$dir"
done

# =========================================================
# GOVERNANCE VALIDATION
# =========================================================

echo ""
echo "🧠 Validating governance structure..."
echo ""

for dir in "${GOVERNANCE_DIRS[@]}"
do
    validate_directory "$dir"
done

# =========================================================
# OBSERVABILITY VALIDATION
# =========================================================

echo ""
echo "📊 Validating observability structure..."
echo ""

for dir in "${OBSERVABILITY_DIRS[@]}"
do
    validate_directory "$dir"
done

# =========================================================
# PORTFOLIO VALIDATION
# =========================================================

echo ""
echo "🎨 Validating portfolio structure..."
echo ""

for dir in "${PORTFOLIO_DIRS[@]}"
do
    validate_directory "$dir"
done

# =========================================================
# PROJECT VALIDATION
# =========================================================

echo ""
echo "🚀 Validating RAG projects..."
echo ""

for i in {1..9}
do
    PROJECT=$(printf "dev/rag/PRJ-%02d*" "$i")

    if ls $MONOREPO/$PROJECT 1> /dev/null 2>&1; then
        echo "✅ PRJ-$i detected"
    else
        echo "⚠️ PRJ-$i not found"
    fi
done

# =========================================================
# CRITICAL FILES
# =========================================================

echo ""
echo "📄 Validating critical migration files..."
echo ""

CRITICAL_FILES=(
"docs/migration/MIGRATION_BLUEPRINT_V1.md"
"docs/migration/CURRENT_STRUCTURE_MAP.md"
"docs/migration/TARGET_STRUCTURE_MAP.md"
"docs/migration/MIGRATION_MAPPING_TABLE.md"
"docs/migration/PRIVATE_FILES_POLICY.md"
"docs/migration/MIGRATION_EXECUTION_PLAN.md"
)

for file in "${CRITICAL_FILES[@]}"
do
    if [ -f "$MONOREPO/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        FAILED=1
    fi
done

# =========================================================
# SECURITY VALIDATION
# =========================================================

echo ""
echo "🔒 Validating sensitive exposure..."
echo ""

find "$MONOREPO" -name ".env" | while read file
do
    echo "⚠️ Sensitive file detected: $file"
done

# =========================================================
# FINAL RESULT
# =========================================================

echo ""
echo "================================================="

if [ "$FAILED" -eq 0 ]; then
    echo "✅ STRUCTURE VALIDATION SUCCESSFUL"
    echo "🚀 Safe to continue migration."
else
    echo "❌ STRUCTURE VALIDATION FAILED"
    echo "⚠️ Fix missing items before migration."
fi

echo "================================================="
echo ""