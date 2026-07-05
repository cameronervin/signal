#!/usr/bin/env bash
set -euo pipefail

project_owner="${PROJECT_OWNER:?PROJECT_OWNER is required}"
project_number="${PROJECT_NUMBER:?PROJECT_NUMBER is required}"
item_url="${ITEM_URL:?ITEM_URL is required}"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

fields_file="$tmp_dir/fields.json"
metadata_file="$tmp_dir/item.json"
project_error_file="$tmp_dir/project-error.txt"

if ! project_json="$(gh project view "$project_number" --owner "$project_owner" --format json 2>"$project_error_file")"; then
  cat "$project_error_file" >&2
  echo "::error::Project label sync cannot access project $project_owner/$project_number. For user-owned Projects v2, add a repository secret named PROJECT_TOKEN with the project scope." >&2
  exit 1
fi

project_id="$(jq -r '.id' <<< "$project_json")"
item_id="$(gh project item-add "$project_number" --owner "$project_owner" --url "$item_url" --format json --jq '.id')"

gh project field-list "$project_number" --owner "$project_owner" --format json > "$fields_file"

if [[ "$item_url" == */pull/* ]]; then
  gh pr view "$item_url" --json labels,state,isDraft,reviewDecision,statusCheckRollup,url \
    --jq '{labels: [.labels[].name], state, isDraft, reviewDecision, url}' > "$metadata_file"
else
  gh issue view "$item_url" --json labels,state,url \
    --jq '{labels: [.labels[].name], state, url}' > "$metadata_file"
fi

has_label() {
  jq -e --arg label "$1" '.labels | index($label)' "$metadata_file" >/dev/null
}

field_id() {
  jq -r --arg field "$1" '.fields[] | select(.name == $field) | .id' "$fields_file"
}

option_id() {
  jq -r --arg field "$1" --arg option "$2" \
    '.fields[] | select(.name == $field) | .options[]? | select(.name == $option) | .id' \
    "$fields_file"
}

set_single_select() {
  local field="$1"
  local option="$2"
  local field option_id_value

  field="$(field_id "$field")"
  option_id_value="$(option_id "$1" "$option")"

  if [[ -z "$field" || -z "$option_id_value" ]]; then
    echo "Skipping missing project field option: $1 -> $option" >&2
    return 0
  fi

  gh project item-edit \
    --project-id "$project_id" \
    --id "$item_id" \
    --field-id "$field" \
    --single-select-option-id "$option_id_value" >/dev/null
}

item_state="$(jq -r '.state // ""' "$metadata_file")"

if [[ "$item_state" == "CLOSED" || "$item_state" == "MERGED" ]]; then
  agent_status="Done"
elif has_label "agent:blocked"; then
  agent_status="Blocked"
elif has_label "agent:merge-ready"; then
  agent_status="Merge Ready"
elif has_label "agent:needs-fix" || has_label "ci:failed"; then
  agent_status="Needs Fix"
elif has_label "agent:reviewing" || has_label "review:codex" || has_label "review:human"; then
  agent_status="Review"
elif has_label "agent:working"; then
  agent_status="Working"
elif has_label "agent:ready"; then
  agent_status="Ready"
else
  agent_status="Intake"
fi

set_single_select "Agent Status" "$agent_status"

if [[ "$agent_status" == "Done" ]]; then
  set_single_select "Status" "Done"
elif [[ "$agent_status" == "Working" || "$agent_status" == "Review" || "$agent_status" == "Needs Fix" ]]; then
  set_single_select "Status" "In Progress"
else
  set_single_select "Status" "Todo"
fi

for loop in feature-build bugfix eval-calibration frontend-fidelity; do
  if has_label "loop:$loop"; then
    set_single_select "Loop" "$loop"
    break
  fi
done

for priority in p0 p1 p2 p3; do
  if has_label "priority:$priority"; then
    set_single_select "Priority" "$priority"
    break
  fi
done

for surface in backend frontend agent-pipeline scoring integrations docs; do
  if has_label "surface:$surface"; then
    set_single_select "Surface" "$surface"
    break
  fi
done

risk="none"
for candidate in scoring-change outreach-gate data-handling external-api; do
  if has_label "risk:$candidate"; then
    risk="$candidate"
    break
  fi
done
set_single_select "Risk" "$risk"

if has_label "agent:merge-ready"; then
  review_gate="merge-ready"
elif has_label "ci:failed"; then
  review_gate="ci-failed"
elif has_label "ci:passing"; then
  review_gate="ci-passing"
elif has_label "review:human"; then
  review_gate="human"
elif has_label "review:codex"; then
  review_gate="codex"
else
  review_gate=""
fi

if [[ -n "$review_gate" ]]; then
  set_single_select "Review Gate" "$review_gate"
fi

echo "Synced $item_url to project $project_owner/$project_number with Agent Status: $agent_status"
