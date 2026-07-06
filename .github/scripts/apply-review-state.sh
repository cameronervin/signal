#!/usr/bin/env bash
set -euo pipefail

source .github/scripts/agent-loop-common.sh

pr_number="${PR_NUMBER:?PR_NUMBER is required}"
message_file="$(mktemp)"
trap 'rm -f "$message_file"' EXIT
printf '%s\n' "${CODEX_FINAL_MESSAGE:-}" > "$message_file"

if grep -Eq '^REVIEW_STATUS:[[:space:]]*needs-fix' "$message_file"; then
  apply_pr_labels "$pr_number" "agent:needs-fix" "agent:merge-ready,ci:passing"
elif grep -Eq '^REVIEW_STATUS:[[:space:]]*human' "$message_file"; then
  apply_pr_labels "$pr_number" "review:human,agent:needs-human" "agent:merge-ready"
elif grep -Eq '^REVIEW_STATUS:[[:space:]]*clear' "$message_file"; then
  apply_pr_labels "$pr_number" "agent:reviewing" "agent:needs-fix,ci:failed"
else
  apply_pr_labels "$pr_number" "agent:needs-human" ""
fi
