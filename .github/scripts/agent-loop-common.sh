#!/usr/bin/env bash
set -euo pipefail

MANIFEST_PATH="${MANIFEST_PATH:-.agents/loops/manifest.yml}"

manifest_default() {
  local key="$1"
  jq -r --arg key "$key" '.defaults[$key]' "$MANIFEST_PATH"
}

manifest_loop_exists() {
  local loop="$1"
  jq -e --arg loop "$loop" '.loops[$loop] != null' "$MANIFEST_PATH" >/dev/null
}

manifest_risk_requires_human() {
  local label="$1"
  jq -e --arg label "$label" \
    '.defaults.risk_labels_requiring_human_review | index($label)' \
    "$MANIFEST_PATH" >/dev/null
}

json_has_label() {
  local json_file="$1"
  local label="$2"
  jq -e --arg label "$label" \
    'any(.labels[]?; (.name // .) == $label)' \
    "$json_file" >/dev/null
}

json_label_value() {
  local json_file="$1"
  local prefix="$2"
  jq -r --arg prefix "$prefix" \
    '[.labels[]? | (.name // .) | select(startswith($prefix))][0] // ""' \
    "$json_file"
}

section_value() {
  local heading="$1"
  awk -v heading="### $heading" '
    $0 == heading { found = 1; next }
    found && /^### / { exit }
    found { print }
  ' | sed '/<!--.*-->/d' | sed 's/[[:space:]]*$//' | sed '/^$/d' | sed '/^_No response_$/d'
}

checked_values() {
  local heading="$1"
  section_value "$heading" | sed -nE 's/^[[:space:]]*-[[:space:]]*\[[xX]\][[:space:]]+//p'
}

slug_value() {
  tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//'
}

slug_lines() {
  local slugged
  while IFS= read -r line; do
    slugged="$(printf '%s\n' "$line" | slug_value)"
    [[ -n "$slugged" ]] && printf '%s\n' "$slugged"
  done
}

csv_join() {
  paste -sd, -
}

apply_issue_labels() {
  local issue_number="$1"
  local add_csv="$2"
  local remove_csv="$3"

  if [[ "${APPLY_LABELS:-true}" != "true" ]]; then
    echo "DRY_RUN add-labels=$add_csv remove-labels=$remove_csv"
    return 0
  fi

  if [[ -n "$remove_csv" ]]; then
    gh issue edit "$issue_number" --remove-label "$remove_csv" || true
  fi

  if [[ -n "$add_csv" ]]; then
    gh issue edit "$issue_number" --add-label "$add_csv"
  fi
}

apply_pr_labels() {
  local pr_number="$1"
  local add_csv="$2"
  local remove_csv="$3"

  if [[ -n "$remove_csv" ]]; then
    gh pr edit "$pr_number" --remove-label "$remove_csv" || true
  fi

  if [[ -n "$add_csv" ]]; then
    gh pr edit "$pr_number" --add-label "$add_csv"
  fi
}
