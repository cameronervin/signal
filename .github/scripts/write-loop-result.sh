#!/usr/bin/env bash
set -euo pipefail

result_path="${LOOP_RESULT_PATH:-.codex-run/loop-result.json}"
mkdir -p "$(dirname "$result_path")"
started_at="${STARTED_AT:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"

changed_file_source="${CHANGED_FILES_PATH:-.codex-run/changed-files.txt}"
if [[ -f "$changed_file_source" ]]; then
  changed_files_json="$(jq -R -s 'split("\n") | map(select(length > 0))' "$changed_file_source")"
else
  changed_files_json="[]"
fi

labels_json="[]"
if [[ -n "${RISK_LABELS:-}" ]]; then
  labels_json="$(printf '%s\n' "$RISK_LABELS" | jq -R -s 'split("\n") | map(select(length > 0))')"
fi

jq -n \
  --arg issue_number "${ISSUE_NUMBER:-}" \
  --arg pr_number "${PR_NUMBER:-}" \
  --arg loop "${LOOP:-}" \
  --arg status "${LOOP_STATUS:-completed}" \
  --arg model "${MODEL:-gpt-5.5}" \
  --arg started_at "$started_at" \
  --arg completed_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg verification "${VERIFICATION_SUMMARY:-}" \
  --arg docs_updated "${DOCS_UPDATED:-not reported}" \
  --arg blockers "${BLOCKERS:-}" \
  --arg fix_pass_count "${FIX_PASS_COUNT:-0}" \
  --argjson changed_files "$changed_files_json" \
  --argjson risks "$labels_json" \
  '{
    issue_number: $issue_number,
    pr_number: $pr_number,
    loop: $loop,
    status: $status,
    model: $model,
    started_at: $started_at,
    completed_at: $completed_at,
    changed_files: $changed_files,
    verification: $verification,
    docs_updated: $docs_updated,
    risks: $risks,
    blockers: $blockers,
    fix_pass_count: ($fix_pass_count | tonumber? // 0)
  }' > "$result_path"

echo "Wrote $result_path"
