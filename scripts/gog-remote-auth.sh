#!/usr/bin/env bash
set -euo pipefail

ACCOUNT="nikolaj.floejgaard@gmail.com"
SERVICES="docs,drive,sheets"
DRIVE_VERIFY_PARENT="1jfj6EqzSsUsyA2_cz6ui2PeObZaTyanD"
TIMEOUT="10m"
KEYRING_PASSWORD_FILE="${HOME}/Library/Application Support/gogcli/keyring-password"

usage() {
  cat <<USAGE
Usage:
  scripts/gog-remote-auth.sh --verify
  scripts/gog-remote-auth.sh --start
  scripts/gog-remote-auth.sh --finish '<redirect-url>'

Remote gog OAuth recovery for ${ACCOUNT}.

Flow:
  1. Run --start and send Nikolaj the printed auth_url.
  2. Nikolaj opens it on any signed-in browser/phone and approves Google.
  3. Google redirects to localhost; that page may fail, but the browser address
     bar contains the full redirect URL.
  4. Run --finish with that full redirect URL to exchange the one-time code.
  5. Run --verify to confirm Drive/Docs/Sheets auth works.

Do not ask for, store, or paste Google passwords, 2FA codes, or passkeys here.
USAGE
}

require_gog() {
  if ! command -v gog >/dev/null 2>&1; then
    echo "gog CLI not found in PATH" >&2
    exit 127
  fi
}

load_file_keyring_password() {
  if [[ -n "${GOG_KEYRING_PASSWORD:-}" ]]; then
    return
  fi

  if [[ -f "${KEYRING_PASSWORD_FILE}" ]]; then
    local perms
    perms="$(stat -f '%Lp' "${KEYRING_PASSWORD_FILE}")"
    if [[ "${perms}" != "600" ]]; then
      echo "Refusing to use ${KEYRING_PASSWORD_FILE}: expected mode 600, got ${perms}" >&2
      exit 1
    fi
    export GOG_KEYRING_PASSWORD
    GOG_KEYRING_PASSWORD="$(<"${KEYRING_PASSWORD_FILE}")"
  fi
}

gog_headless() {
  gog "$@"
}

verify() {
  gog_headless drive ls \
    --parent "${DRIVE_VERIFY_PARENT}" \
    --max 1 \
    --json \
    --no-input \
    -a "${ACCOUNT}" >/dev/null
  echo "gog auth OK for ${ACCOUNT}"
}

start() {
  gog_headless auth add "${ACCOUNT}" \
    --services "${SERVICES}" \
    --remote \
    --step 1 \
    --timeout "${TIMEOUT}" \
    --no-input
}

finish() {
  local redirect_url="${1:-}"
  if [[ -z "${redirect_url}" ]]; then
    echo "Missing redirect URL" >&2
    usage >&2
    exit 2
  fi

  gog_headless auth add "${ACCOUNT}" \
    --services "${SERVICES}" \
    --remote \
    --step 2 \
    --auth-url "${redirect_url}" \
    --timeout "${TIMEOUT}" \
    --no-input

  verify
}

main() {
  require_gog
  load_file_keyring_password

  case "${1:-}" in
    --verify)
      [[ "$#" -eq 1 ]] || { usage >&2; exit 2; }
      verify
      ;;
    --start)
      [[ "$#" -eq 1 ]] || { usage >&2; exit 2; }
      start
      ;;
    --finish)
      [[ "$#" -eq 2 ]] || { usage >&2; exit 2; }
      finish "$2"
      ;;
    -h|--help|"")
      usage
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
