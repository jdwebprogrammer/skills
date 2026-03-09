#!/bin/bash
# Run a low-frequency reconciliation watcher.
# Usage:
#   bash ~/skills/team-dispatch/scripts/watch.sh
#   INTERVAL=90 GRACE=20 bash ~/skills/team-dispatch/scripts/watch.sh

set -e

INTERVAL=${INTERVAL:-60}
GRACE=${GRACE:-15}

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$SKILL_DIR/scripts/watch.py" --interval "$INTERVAL" --grace "$GRACE"
