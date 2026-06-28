#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  authrestart.sh --check
  authrestart.sh --stage
  authrestart.sh --now

--check  Verify FileVault and authenticated restart support.
--stage  Authenticate once and stage FileVault unlock for the next restart.
--now    Authenticate once and restart immediately through FileVault.

This intentionally uses Apple's fdesetup prompt. Do not store the password in
OpenClaw, files, memory, env vars, or chat.
EOF
}

if [[ "$#" -ne 1 ]]; then
  usage
  exit 64
fi

mode="$1"
case "$mode" in
  --check)
    ;;
  --stage)
    ;;
  --now)
    ;;
  *)
    usage
    exit 64
    ;;
esac

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Authenticated restart helper is macOS-only." >&2
  exit 70
fi

if [[ "$(fdesetup status)" != "FileVault is On." ]]; then
  echo "FileVault is not on, or status was unexpected:" >&2
  fdesetup status >&2
  exit 78
fi

if [[ "$(fdesetup supportsauthrestart 2>/dev/null)" != "true" ]]; then
  echo "This Mac does not report support for fdesetup authrestart." >&2
  exit 78
fi

if [[ "$mode" == "--check" ]]; then
  echo "Authenticated restart supported and FileVault is on."
  exit 0
fi

cat >&2 <<'EOF'
Authenticated restart temporarily reduces FileVault protection until the next
restart completes. Apple stores a temporary unlock key so the next boot can pass
the FileVault unlock screen.

Continue only for planned maintenance/restart windows.
EOF

if [[ "$mode" == "--stage" ]]; then
  sudo fdesetup authrestart -delayminutes -1
else
  sudo fdesetup authrestart -delayminutes 0
fi
