#!/usr/bin/env bash
# Regenerate all courses that have an outline.md
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL="${1:-sonnet}"

echo "Training Hub — Full Rebuild (model: $MODEL)"
echo ""

for COURSE in azure aws data ai; do
  if [[ -f "courses/$COURSE/input/outline.md" ]]; then
    echo "→ Generating $COURSE..."
    python3 src/generator/generate.py --course "$COURSE" --model "$MODEL"
  else
    echo "→ Skipping $COURSE (no outline.md)"
  fi
done

echo ""
echo "Done. Serve with: npm start"
