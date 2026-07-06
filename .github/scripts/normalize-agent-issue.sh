#!/usr/bin/env bash
set -euo pipefail

source .github/scripts/agent-loop-common.sh

issue_json="${ISSUE_JSON:-.codex-run/issue.json}"
issue_number="${ISSUE_NUMBER:-$(jq -r '.number' "$issue_json")}"
event_name="${EVENT_NAME:-}"
dispatch_loop="${DISPATCH_LOOP:-}"
body_file="$(mktemp)"
trap 'rm -f "$body_file"' EXIT

jq -r '.body // ""' "$issue_json" > "$body_file"

body_has_form=false
if grep -qx '### User-visible outcome' "$body_file" &&
  grep -qx '### Acceptance criteria' "$body_file"; then
  body_has_form=true
fi

section_from_body() {
  local heading="$1"
  section_value "$heading" < "$body_file"
}

checked_from_body() {
  local heading="$1"
  checked_values "$heading" < "$body_file"
}

loop="$(section_from_body "Loop" | head -n 1 | slug_value)"
priority="$(section_from_body "Priority" | head -n 1 | slug_value)"
work_type="$(section_from_body "Type" | head -n 1 | slug_value)"

if [[ -z "$loop" ]]; then
  loop="$(json_label_value "$issue_json" "loop:" | sed 's/^loop://')"
fi
if [[ -z "$loop" ]]; then
  loop="$dispatch_loop"
fi
if [[ -z "$priority" ]]; then
  priority="$(json_label_value "$issue_json" "priority:" | sed 's/^priority://')"
fi
if [[ -z "$priority" ]]; then
  priority="p2"
fi
if [[ -z "$work_type" ]]; then
  work_type="$(json_label_value "$issue_json" "type:" | sed 's/^type://')"
fi

surfaces=()
while IFS= read -r surface; do
  surfaces+=("$surface")
done < <(checked_from_body "Surfaces" | slug_lines | sed '/^$/d')
if [[ "${#surfaces[@]}" -eq 0 ]]; then
  existing_surface="$(json_label_value "$issue_json" "surface:" | sed 's/^surface://')"
  if [[ -n "$existing_surface" ]]; then
    surfaces=("$existing_surface")
  fi
fi

risks=()
while IFS= read -r risk; do
  risks+=("$risk")
done < <(checked_from_body "Risk flags" | slug_lines | sed '/^$/d' | sed 's/^/risk:/')
if [[ "${#risks[@]}" -eq 0 ]]; then
  while IFS= read -r risk_label; do
    [[ -n "$risk_label" ]] && risks+=("$risk_label")
  done < <(jq -r '[.labels[]? | (.name // .) | select(startswith("risk:"))][]?' "$issue_json")
fi

missing=()
[[ -z "$loop" ]] && missing+=("loop")
[[ -z "$priority" ]] && missing+=("priority")
[[ -z "$work_type" ]] && missing+=("type")
[[ "${#surfaces[@]}" -eq 0 ]] && missing+=("surface")

if [[ "$body_has_form" == "true" ]]; then
  for heading in \
    "User-visible outcome" \
    "Acceptance criteria" \
    "Budget" \
    "Stop condition" \
    "Artifact expectations"; do
    if [[ -z "$(section_from_body "$heading")" ]]; then
      missing+=("$heading")
    fi
  done
elif [[ "$event_name" != "workflow_dispatch" ]]; then
  missing+=("agent-loop issue form")
fi

if [[ -n "$loop" ]] && ! manifest_loop_exists "$loop"; then
  missing+=("known loop")
fi

high_risk=false
for risk in "${risks[@]-}"; do
  [[ -z "$risk" ]] && continue
  if manifest_risk_requires_human "$risk"; then
    high_risk=true
  fi
done

has_ready=false
json_has_label "$issue_json" "agent:ready" && has_ready=true
has_human_review=false
json_has_label "$issue_json" "review:human" && has_human_review=true
is_active=false
for active_label in agent:working agent:reviewing agent:merge-ready; do
  if json_has_label "$issue_json" "$active_label"; then
    is_active=true
  fi
done

add_labels=()
remove_labels=()

if [[ -n "$loop" ]]; then
  add_labels+=("loop:$loop")
fi
if [[ -n "$priority" ]]; then
  add_labels+=("priority:$priority")
fi
if [[ -n "$work_type" ]]; then
  add_labels+=("type:$work_type")
fi
for surface in "${surfaces[@]-}"; do
  [[ -z "$surface" ]] && continue
  add_labels+=("surface:$surface")
done
for risk in "${risks[@]-}"; do
  [[ -z "$risk" ]] && continue
  add_labels+=("$risk")
done

while IFS= read -r existing_label; do
  case "$existing_label" in
    loop:*|priority:*|type:*|surface:*|risk:*)
      keep=false
      for desired_label in "${add_labels[@]-}"; do
        if [[ "$existing_label" == "$desired_label" ]]; then
          keep=true
        fi
      done
      [[ "$keep" == "false" ]] && remove_labels+=("$existing_label")
      ;;
  esac
done < <(jq -r '.labels[]? | (.name // .)' "$issue_json")

valid=false
should_run=false
reason="ready"

if [[ "${#missing[@]}" -gt 0 ]]; then
  add_labels+=("agent:needs-human")
  remove_labels+=("agent:ready")
  reason="missing: $(printf '%s, ' "${missing[@]}" | sed 's/, $//')"
elif [[ "$is_active" == "true" ]]; then
  valid=true
  should_run=false
  reason="already active"
elif [[ "$high_risk" == "true" && "$event_name" != "workflow_dispatch" && "$has_human_review" != "true" ]]; then
  add_labels+=("agent:needs-human" "review:human")
  remove_labels+=("agent:ready")
  valid=true
  should_run=false
  reason="high risk requires human review"
else
  valid=true
  remove_labels+=("agent:needs-human")
  if [[ "$event_name" == "workflow_dispatch" || "$has_ready" == "true" || "$high_risk" == "false" ]]; then
    add_labels+=("agent:ready")
    should_run=true
  fi
fi

if [[ "${#add_labels[@]}" -gt 0 ]]; then
  add_csv="$(printf '%s\n' "${add_labels[@]}" | sed '/^$/d' | sort -u | csv_join)"
else
  add_csv=""
fi
if [[ "${#remove_labels[@]}" -gt 0 ]]; then
  remove_csv="$(printf '%s\n' "${remove_labels[@]}" | sed '/^$/d' | sort -u | csv_join)"
else
  remove_csv=""
fi
apply_issue_labels "$issue_number" "$add_csv" "$remove_csv"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "valid=$valid"
    echo "should_run=$should_run"
    echo "loop=$loop"
    echo "high_risk=$high_risk"
    echo "reason=$reason"
    printf 'risk_labels<<EOF\n'
    if [[ "${#risks[@]}" -gt 0 ]]; then
      printf '%s\n' "${risks[@]}"
    fi
    printf 'EOF\n'
  } >> "$GITHUB_OUTPUT"
fi

echo "Issue #$issue_number normalized: valid=$valid should_run=$should_run reason=$reason"
