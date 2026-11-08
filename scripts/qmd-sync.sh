#!/usr/bin/env bash
# Keep the vault's project-local qmd search index fresh.
#
#   scripts/qmd-sync.sh           re-index now (fast, BM25), embed in the background
#   scripts/qmd-sync.sh --wait    re-index and embed in the foreground (first run, CI)
#   scripts/qmd-sync.sh --status  show index status and whether an embed is running
#
# Safe to call any time: if qmd is not installed it does nothing and exits 0,
# and it never fails the calling flow (errors are printed as warnings).
# Collections are defined in .qmd/index.yml (committed); the index database is local.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 0

if ! command -v qmd >/dev/null 2>&1; then
  echo "qmd-sync: qmd not installed, skipping (search falls back to index.md + grep)"
  exit 0
fi
if [ ! -f .qmd/index.yml ]; then
  echo "qmd-sync: .qmd/index.yml missing, skipping"
  exit 0
fi

LOCK=.qmd/embed.lock
LOG=.qmd/embed.log

if [ "${1:-}" = "--status" ]; then
  qmd status 2>/dev/null | sed -n '1,40p'
  [ -d "$LOCK" ] && echo "qmd-sync: embedding in progress (log: $LOG)" || true
  exit 0
fi

# 1. Re-index (fast, keyword index; picks up adds, edits, renames, deletions)
if out=$(qmd update 2>&1); then
  echo "qmd-sync: $(printf '%s\n' "$out" | grep -E '^Indexed:' | awk '{n+=$2; u+=$4; r+=$8} END {printf "indexed %d new, %d updated, %d removed", n, u, r}')"
else
  echo "qmd-sync: warning: 'qmd update' failed:"; printf '%s\n' "$out" | tail -5
  exit 0
fi

# 2. Embed (vectors for semantic search). Incremental; first run downloads models.
if [ "${1:-}" = "--wait" ]; then
  qmd embed 2>&1 | grep -v ggml_metal | tail -2 || echo "qmd-sync: warning: 'qmd embed' failed"
  exit 0
fi
if mkdir "$LOCK" 2>/dev/null; then
  nohup bash -c "qmd embed >'$LOG' 2>&1; rmdir '$LOCK'" >/dev/null 2>&1 &
  echo "qmd-sync: embedding in background (log: $LOG)"
else
  echo "qmd-sync: embed already running, skipped"
fi
exit 0
