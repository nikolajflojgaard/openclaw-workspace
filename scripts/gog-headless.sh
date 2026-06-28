#!/usr/bin/env bash
set -euo pipefail

KEYRING_PASSWORD_FILE="${HOME}/Library/Application Support/gogcli/keyring-password"

if ! command -v gog >/dev/null 2>&1; then
  echo "gog CLI not found in PATH" >&2
  exit 127
fi

if [[ -z "${GOG_KEYRING_PASSWORD:-}" ]]; then
  if [[ ! -f "${KEYRING_PASSWORD_FILE}" ]]; then
    echo "Missing ${KEYRING_PASSWORD_FILE}; run scripts/gog-remote-auth.sh after initializing the file keyring" >&2
    exit 1
  fi

  perms="$(stat -f '%Lp' "${KEYRING_PASSWORD_FILE}")"
  if [[ "${perms}" != "600" ]]; then
    echo "Refusing to use ${KEYRING_PASSWORD_FILE}: expected mode 600, got ${perms}" >&2
    exit 1
  fi

  export GOG_KEYRING_PASSWORD
  GOG_KEYRING_PASSWORD="$(<"${KEYRING_PASSWORD_FILE}")"
fi

exec gog "$@"
