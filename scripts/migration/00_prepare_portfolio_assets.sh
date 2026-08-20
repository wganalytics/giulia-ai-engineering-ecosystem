#!/bin/bash

# =========================================================
# GIULIA AI ENGINEERING ECOSYSTEM
# PORTFOLIO ASSETS PREPARATION
# =========================================================

set -e

# =========================================================
# LOAD FRAMEWORK
# =========================================================

source "$(dirname "$0")/common.sh"

# =========================================================
# HEADER
# =========================================================

print_header "🚀 PREPARING PORTFOLIO ASSETS"

# =========================================================
# PORTFOLIO ASSETS DIRECTORY
# =========================================================

PORTFOLIO_ASSETS="$SOURCE/PORTFOLIO_ASSETS"

echo "📁 Creating portfolio assets structure..."

mkdir -p "$PORTFOLIO_ASSETS"

mkdir -p "$PORTFOLIO_ASSETS/diagrams"
mkdir -p "$PORTFOLIO_ASSETS/screenshots"
mkdir -p "$PORTFOLIO_ASSETS/drawio"
mkdir -p "$PORTFOLIO_ASSETS/public_images"

echo "✅ Portfolio assets structure ready."

# =========================================================
# VALIDATE SOURCE DIRECTORY
# =========================================================

if [ ! -d "$SOURCE" ]; then

    echo "❌ SOURCE directory not found."
    exit 1

fi

# =========================================================
# DRAWIO FILES
# =========================================================

echo ""
echo "🧠 Searching drawio files..."

find "$SOURCE" -type f \( \
-name '*.drawio' \
\) \
-not -path "*/venv/*" \
-not -path "*/__pycache__/*" \
-not -path "*/node_modules/*" \
-not -path "*/logs/*" \
-not -path "*/cache/*" \
-not -path "*/vector_db/*" \
-not -path "*/PORTFOLIO_ASSETS/*" \
| while read file
do

    FILE_NAME=$(basename "$file")

    execute_or_dry_run \
    "Copy DrawIO: $FILE_NAME" \
    "cp '$file' '$PORTFOLIO_ASSETS/drawio/'"

done

# =========================================================
# SVG DIAGRAMS
# =========================================================

echo ""
echo "📊 Searching svg diagrams..."

find "$SOURCE" -type f \( \
-name '*.svg' \
\) \
-not -path "*/venv/*" \
-not -path "*/__pycache__/*" \
-not -path "*/node_modules/*" \
-not -path "*/logs/*" \
-not -path "*/cache/*" \
-not -path "*/vector_db/*" \
-not -path "*/PORTFOLIO_ASSETS/*" \
| while read file
do

    FILE_NAME=$(basename "$file")

    execute_or_dry_run \
    "Copy SVG Diagram: $FILE_NAME" \
    "cp '$file' '$PORTFOLIO_ASSETS/diagrams/'"

done

# =========================================================
# SCREENSHOTS
# =========================================================

echo ""
echo "🖼️ Searching screenshots..."

find "$SOURCE" -type f \( \
-name '*screenshot*.png' -o \
-name '*dashboard*.png' -o \
-name '*architecture*.png' -o \
-name '*rag*.png' \
\) \
-not -path "*/venv/*" \
-not -path "*/__pycache__/*" \
-not -path "*/node_modules/*" \
-not -path "*/logs/*" \
-not -path "*/cache/*" \
-not -path "*/vector_db/*" \
-not -path "*/PORTFOLIO_ASSETS/*" \
| while read file
do

    FILE_NAME=$(basename "$file")

    execute_or_dry_run \
    "Copy Screenshot: $FILE_NAME" \
    "cp '$file' '$PORTFOLIO_ASSETS/screenshots/'"

done

# =========================================================
# PUBLIC IMAGES
# =========================================================

echo ""
echo "🌎 Searching public portfolio images..."

find "$SOURCE" -type f \( \
-name '*.png' -o \
-name '*.jpg' -o \
-name '*.jpeg' \
\) \
-not -name '*screenshot*' \
-not -name '*dashboard*' \
-not -name '*architecture*' \
-not -name '*rag*' \
-not -path "*/venv/*" \
-not -path "*/__pycache__/*" \
-not -path "*/node_modules/*" \
-not -path "*/logs/*" \
-not -path "*/cache/*" \
-not -path "*/vector_db/*" \
-not -path "*/uploads/*" \
-not -path "*/private/*" \
-not -path "*/PORTFOLIO_ASSETS/*" \
| while read file
do

    FILE_NAME=$(basename "$file")

    execute_or_dry_run \
    "Copy Public Image: $FILE_NAME" \
    "cp '$file' '$PORTFOLIO_ASSETS/public_images/'"

done

# =========================================================
# VALIDATION
# =========================================================

echo ""
echo "🔎 Validating portfolio assets..."

validate_directory "$PORTFOLIO_ASSETS"

ASSET_DIRS=(
"$PORTFOLIO_ASSETS/diagrams"
"$PORTFOLIO_ASSETS/screenshots"
"$PORTFOLIO_ASSETS/drawio"
"$PORTFOLIO_ASSETS/public_images"
)

for dir in "${ASSET_DIRS[@]}"
do

    validate_directory "$dir"

    echo "✅ Validated:"
    echo "$dir"

done

# =========================================================
# REPORT
# =========================================================

REPORT_FILE="$REPORT_DIR/portfolio_assets_preparation_${TIMESTAMP}.md"

DRAWIO_COUNT=$(find "$PORTFOLIO_ASSETS/drawio" | wc -l)
DIAGRAM_COUNT=$(find "$PORTFOLIO_ASSETS/diagrams" | wc -l)
SCREENSHOT_COUNT=$(find "$PORTFOLIO_ASSETS/screenshots" | wc -l)
IMAGE_COUNT=$(find "$PORTFOLIO_ASSETS/public_images" | wc -l)

cat > "$REPORT_FILE" <<EOF
# Portfolio Assets Preparation Report

## Timestamp
$TIMESTAMP

---

# Source
$SOURCE

---

# Portfolio Assets
$PORTFOLIO_ASSETS

---

# Migration Mode

DRY_RUN=$DRY_RUN

---

# Collected Assets

## DrawIO Files
$DRAWIO_COUNT

## SVG Diagrams
$DIAGRAM_COUNT

## Screenshots
$SCREENSHOT_COUNT

## Public Images
$IMAGE_COUNT

---

# Excluded Paths

- venv
- __pycache__
- node_modules
- logs
- cache
- vector_db
- uploads
- private

---

# Result

Portfolio assets preparation executed successfully.

EOF

echo ""
echo "📝 Report generated:"
echo "$REPORT_FILE"

# =========================================================
# FINAL
# =========================================================

print_header "✅ PORTFOLIO ASSETS PREPARATION COMPLETED"

echo "🎨 Portfolio assets organized successfully."
echo ""