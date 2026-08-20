#!/bin/bash

# =========================================================
# GIULIA AI ENGINEERING ECOSYSTEM
# BACKUP FREEZE SCRIPT
# =========================================================
if ! command -v tree &> /dev/null
then
    echo "❌ tree command not installed."
    exit 1
fi

set -e

echo ""
echo "🚀 STARTING BACKUP FREEZE PROCESS..."
echo ""

# =========================================================
# CONFIG
# =========================================================

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

CURRENT_ECOSYSTEM="$HOME/Documents/PORTIFOLIO/AGENTES/RAG"
MONOREPO="$HOME/Developer/giulia-ai-engineering-ecosystem"

BACKUP_ROOT="$HOME/Developer/backups"
SNAPSHOT_DIR="$BACKUP_ROOT/ecosystem_snapshots"
ZIP_DIR="$BACKUP_ROOT/zip_exports"
CHECKPOINT_DIR="$BACKUP_ROOT/migration_checkpoints"

mkdir -p "$SNAPSHOT_DIR"
mkdir -p "$ZIP_DIR"
mkdir -p "$CHECKPOINT_DIR"

# =========================================================
# VALIDATION
# =========================================================

echo "🔍 Validating source ecosystem..."

if [ ! -d "$CURRENT_ECOSYSTEM" ]; then
    echo "❌ ERROR: Source ecosystem not found."
    echo "Expected path:"
    echo "$CURRENT_ECOSYSTEM"
    exit 1
fi

echo "✅ Source ecosystem found."

# =========================================================
# TREE SNAPSHOT
# =========================================================

echo ""
echo "📁 Generating structure snapshot..."

tree -L 4 "$CURRENT_ECOSYSTEM" > "$SNAPSHOT_DIR/tree_snapshot_$TIMESTAMP.txt"

echo "✅ Tree snapshot generated."

# =========================================================
# ZIP BACKUP
# =========================================================

echo ""
echo "📦 Creating ZIP backup..."

ZIP_NAME="ecosystem_backup_$TIMESTAMP.zip"

cd "$HOME/Documents/PORTIFOLIO/AGENTES"

zip -r "$ZIP_DIR/$ZIP_NAME" "RAG" \
-x "*.DS_Store" \
-x "*/venv/*" \
-x "*/__pycache__/*" \
-x "*.pyc" \
-x "*.sqlite" \
-x "*.db" \
-x "*/logs/*"

echo "✅ ZIP backup created:"
echo "$ZIP_DIR/$ZIP_NAME"

# =========================================================
# GIT CHECKPOINT
# =========================================================

echo ""
echo "🧠 Creating Git migration checkpoint..."

cd "$CURRENT_ECOSYSTEM"

git add .

git commit -m "MIGRATION_FREEZE_$TIMESTAMP" || true

git tag "MIGRATION_FREEZE_$TIMESTAMP"

echo "✅ Git checkpoint created."

# =========================================================
# CHECKPOINT REPORT
# =========================================================

echo ""
echo "📝 Generating migration checkpoint report..."

REPORT="$CHECKPOINT_DIR/migration_checkpoint_$TIMESTAMP.md"

cat > "$REPORT" <<EOF
# Migration Freeze Checkpoint

## Timestamp
$TIMESTAMP

---

# Source Ecosystem
$CURRENT_ECOSYSTEM

---

# Backup ZIP
$ZIP_DIR/$ZIP_NAME

---

# Git Tag
MIGRATION_FREEZE_$TIMESTAMP

---

# Snapshot
$SNAPSHOT_DIR/tree_snapshot_$TIMESTAMP.txt

---

# Status

✅ Backup completed
✅ ZIP generated
✅ Git checkpoint created
✅ Tree snapshot generated

EOF

echo "✅ Migration report generated."

# =========================================================
# FINAL
# =========================================================

echo ""
echo "================================================="
echo "✅ BACKUP FREEZE COMPLETED SUCCESSFULLY"
echo "================================================="
echo ""

echo "📦 ZIP:"
echo "$ZIP_DIR/$ZIP_NAME"

echo ""
echo "🧠 Git Tag:"
echo "MIGRATION_FREEZE_$TIMESTAMP"

echo ""
echo "📝 Report:"
echo "$REPORT"

echo ""
echo "🚀 Safe to start migration phases."
echo ""