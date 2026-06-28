#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  restart_host.sh --check
  restart_host.sh --confirm

--check    Validate OS, shutdown path, and non-interactive sudo permission without restarting.
--confirm  Restart immediately. Requires exact single argument.
EOF
}

if [[ "$#" -ne 1 ]]; then
  usage
  exit 64
fi

mode="$1"
if [[ "$mode" != "--check" && "$mode" != "--confirm" ]]; then
  usage
  exit 64
fi

os="$(uname -s)"
case "$os" in
  Darwin)
    shutdown_path="/sbin/shutdown"
    sudoers_path="/private/etc/sudoers.d/openclaw-host-restart"
    ;;
  Linux)
    shutdown_path="$(command -v shutdown || true)"
    sudoers_path="/etc/sudoers.d/openclaw-host-restart"
    ;;
  *)
    echo "Unsupported OS: $os" >&2
    exit 70
    ;;
esac

if [[ -z "${shutdown_path:-}" || ! -x "$shutdown_path" ]]; then
  echo "shutdown command not found or not executable." >&2
  exit 69
fi

if ! sudo -n -l "$shutdown_path" >/dev/null 2>&1; then
  cat >&2 <<EOF
Non-interactive sudo is not configured for $shutdown_path.

Do not paste your password into chat. Configure a narrow sudoers rule locally.
Expected sudoers file: $sudoers_path
Expected command permission: $USER ALL=(root) NOPASSWD: $shutdown_path -r now
EOF
  exit 77
fi

if [[ "$mode" == "--check" ]]; then
  echo "Restart preflight OK: $os, $shutdown_path, non-interactive sudo allowed."
  exit 0
fi

exec sudo -n "$shutdown_path" -r now
