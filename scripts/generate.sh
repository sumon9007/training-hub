#!/usr/bin/env bash
# Generate a single course presentation
# Usage: ./scripts/generate.sh <course> [model]
#   course: azure | aws | data | ai
#   model:  haiku | sonnet | opus  (default: sonnet)

set -euo pipefail
cd "$(dirname "$0")/.."

COURSE="${1:-}"
MODEL="${2:-sonnet}"

if [[ -z "$COURSE" ]]; then
  echo "Usage: $0 <course> [model]"
  echo "  course: azure | aws | data | ai"
  echo "  model:  haiku | sonnet | opus"
  exit 1
fi

echo "Training Hub Generator"
echo "  Course : $COURSE"
echo "  Model  : $MODEL"
echo ""

python3 src/generator/generate.py --course "$COURSE" --model "$MODEL"
