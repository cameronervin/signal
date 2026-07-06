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
  pr_state="$(gh pr view "$pr_number" --json labels,statusCheckRollup)"
  needs_human="$(jq -r 'any(.labels[]?; .name == "review:human")' <<< "$pr_state")"
  backend_ok="$(jq -r 'any(.statusCheckRollup[]?; .name == "backend" and .conclusion == "SUCCESS")' <<< "$pr_state")"
  frontend_ok="$(jq -r 'any(.statusCheckRollup[]?; .name == "frontend" and .conclusion == "SUCCESS")' <<< "$pr_state")"

  if [[ "$needs_human" != "true" && "$backend_ok" == "true" && "$frontend_ok" == "true" ]]; then
    apply_pr_labels "$pr_number" "agent:merge-ready,ci:passing" "agent:reviewing,agent:needs-fix,ci:failed"
  else
    apply_pr_labels "$pr_number" "agent:reviewing" "agent:merge-ready,agent:needs-fix,ci:failed"
  fi
else
  apply_pr_labels "$pr_number" "agent:needs-human" ""
fi
