#!/usr/bin/env bash
set -euo pipefail

result_path="${LOOP_RESULT_PATH:-.codex-run/loop-result.json}"
pr_number="${PR_NUMBER:?PR_NUMBER is required}"
body_file="$(mktemp)"
trap 'rm -f "$body_file"' EXIT

issue_number="$(jq -r '.issue_number // ""' "$result_path")"
loop="$(jq -r '.loop // ""' "$result_path")"
status="$(jq -r '.status // ""' "$result_path")"
model="$(jq -r '.model // ""' "$result_path")"
docs_updated="$(jq -r '.docs_updated // ""' "$result_path")"
blockers="$(jq -r '.blockers // ""' "$result_path")"
fix_pass_count="$(jq -r '.fix_pass_count // 0' "$result_path")"

{
  if [[ -n "$issue_number" ]]; then
    echo "Closes #$issue_number"
    echo
  fi
  echo "## Agent Loop"
  echo
  echo "- Loop: $loop"
  echo "- Status: $status"
  echo "- Model: $model"
  echo "- Fix passes: $fix_pass_count"
  echo "- Docs: $docs_updated"
  if [[ -n "$blockers" ]]; then
    echo "- Blockers: $blockers"
  fi
  echo
  echo "## Changed Files"
  echo
  jq -r '.changed_files[]? | "- `\(.)`"' "$result_path"
  echo
  echo "## Verification"
  echo
  jq -r '.verification // "Not reported."' "$result_path"
  echo
  echo "## Risk Labels"
  echo
  if ! jq -e '.risks | length > 0' "$result_path" >/dev/null; then
    echo "- none"
  else
    jq -r '.risks[] | "- `\(.)`"' "$result_path"
  fi
  echo
  echo "## Merge Gate"
  echo
  echo "No auto-merge. Human review, required checks, and branch protection remain mandatory."
} > "$body_file"

gh pr edit "$pr_number" --body-file "$body_file"
echo "Updated PR #$pr_number body from $result_path"
