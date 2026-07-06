#!/usr/bin/env bash
set -euo pipefail

source .github/scripts/agent-loop-common.sh

pr_number="${PR_NUMBER:?PR_NUMBER is required}"
max_passes="$(manifest_default max_fix_passes)"
labels_json="$(gh pr view "$pr_number" --json labels)"

current_pass=0
for pass in $(seq 1 "$max_passes"); do
  if jq -e --arg label "agent:fix-pass-$pass" \
    'any(.labels[]?; .name == $label)' <<< "$labels_json" >/dev/null; then
    current_pass="$pass"
  fi
done

if [[ "$current_pass" -ge "$max_passes" ]]; then
  apply_pr_labels "$pr_number" "agent:blocked" "agent:needs-fix"
  gh pr comment "$pr_number" --body "Codex fix pass budget is exhausted after $max_passes attempts. Marking this PR blocked for human review."
  if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    {
      echo "should_run=false"
      echo "next_pass=$current_pass"
    } >> "$GITHUB_OUTPUT"
  fi
  echo "Fix budget exhausted for PR #$pr_number"
  exit 0
fi

next_pass=$((current_pass + 1))
head_ref="$(gh pr view "$pr_number" --json headRefName --jq '.headRefName')"
labels_to_add="agent:needs-fix"
if [[ "${CI_FAILURE:-false}" == "true" ]]; then
  labels_to_add="$labels_to_add,ci:failed"
fi
apply_pr_labels "$pr_number" "$labels_to_add" "agent:blocked"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "should_run=true"
    echo "next_pass=$next_pass"
    echo "head_ref=$head_ref"
  } >> "$GITHUB_OUTPUT"
fi

echo "Prepared fix pass $next_pass for PR #$pr_number"
