#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Ensure this is a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "CONFLICT: Not a git repository: $REPO"
  exit 1
fi

# Ensure origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "No remote 'origin' configured"
  exit 0
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ -z "$BRANCH" || "$BRANCH" == "HEAD" ]]; then
  BRANCH="main"
fi

# Refresh remotes
if ! git fetch origin "$BRANCH" --quiet; then
  echo "CONFLICT: Failed to fetch origin/$BRANCH"
  exit 1
fi

LOCAL="$(git rev-parse @)"
REMOTE="$(git rev-parse "origin/$BRANCH")"
BASE="$(git merge-base @ "origin/$BRANCH")"

# Detect divergence (manual intervention required)
if [[ "$LOCAL" != "$REMOTE" && "$LOCAL" != "$BASE" && "$REMOTE" != "$BASE" ]]; then
  echo "CONFLICT: Local and origin/$BRANCH have diverged. No auto-resolution applied."
  exit 0
fi

# If behind only, fast-forward
if [[ "$LOCAL" == "$BASE" && "$REMOTE" != "$BASE" ]]; then
  if ! git pull --ff-only origin "$BRANCH" --quiet; then
    echo "CONFLICT: Fast-forward pull failed"
    exit 1
  fi
fi

MANIFEST="$REPO/.backup-manifest"
if [[ ! -f "$MANIFEST" ]]; then
  echo "CONFLICT: Missing backup manifest: $MANIFEST"
  exit 1
fi

PATHS=()
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" ]] && continue
  PATHS+=("$line")
done < "$MANIFEST"

# Stage/commit only the curated Jason backup surface
if ! git diff --quiet || ! git diff --cached --quiet || [[ -n "$(git ls-files --others --exclude-standard -- "${PATHS[@]}")" ]]; then
  git add -A -- "${PATHS[@]}"
  TS="$(date +"%Y-%m-%d %H:%M:%S")"
  if ! git commit -m "chore(sync): auto-sync Jason backup @ $TS" --quiet; then
    # Nothing to commit race safety
    :
  fi
fi

LOCAL_AFTER="$(git rev-parse @)"
REMOTE_AFTER="$(git rev-parse "origin/$BRANCH")"

# Push only if we are ahead
if [[ "$LOCAL_AFTER" != "$REMOTE_AFTER" ]]; then
  if git push origin "$BRANCH" --quiet; then
    SHORT="$(git rev-parse --short @)"
    echo "SYNC_OK branch=$BRANCH commit=$SHORT"
    exit 0
  else
    echo "CONFLICT: Push failed (possibly remote updated). No force push applied."
    exit 1
  fi
fi

echo "NO_CHANGES branch=$BRANCH"
