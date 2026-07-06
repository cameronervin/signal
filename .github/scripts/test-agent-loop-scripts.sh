#!/usr/bin/env bash
set -euo pipefail

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cat > "$tmp_dir/low-risk.json" <<'JSON'
{
  "number": 101,
  "body": "### Loop\n\nfeature-build\n\n### Priority\n\np2\n\n### Type\n\ndocs\n\n### Surfaces\n\n- [X] docs\n\n### Risk flags\n\n- [ ] scoring-change\n\n### User-visible outcome\n\nA maintainer can see loop docs.\n\n### Acceptance criteria\n\n- Contract exists\n- Manifest exists\n\n### Budget\n\nOne implementation pass.\n\n### Stop condition\n\nStop when docs are updated.\n\n### Artifact expectations\n\nWrite loop-result.json.\n",
  "labels": []
}
JSON

cat > "$tmp_dir/high-risk.json" <<'JSON'
{
  "number": 102,
  "body": "### Loop\n\neval-calibration\n\n### Priority\n\np1\n\n### Type\n\nfeature\n\n### Surfaces\n\n- [X] scoring\n\n### Risk flags\n\n- [X] scoring-change\n\n### User-visible outcome\n\nA manager can inspect scoring changes.\n\n### Acceptance criteria\n\n- Fixture covers the change\n\n### Budget\n\nOne implementation pass.\n\n### Stop condition\n\nStop when scoring is stable.\n\n### Artifact expectations\n\nWrite loop-result.json.\n",
  "labels": []
}
JSON

cat > "$tmp_dir/malformed.json" <<'JSON'
{
  "number": 103,
  "body": "### Loop\n\nfeature-build\n",
  "labels": []
}
JSON

cat > "$tmp_dir/ready.json" <<'JSON'
{
  "number": 104,
  "body": "Legacy issue",
  "labels": [
    {"name": "loop:bugfix"},
    {"name": "priority:p2"},
    {"name": "type:bug"},
    {"name": "surface:backend"},
    {"name": "agent:ready"}
  ]
}
JSON

run_case() {
  local name="$1"
  local expected="$2"
  local output_file="$tmp_dir/$name.out"
  GITHUB_OUTPUT="$output_file" APPLY_LABELS=false ISSUE_JSON="$tmp_dir/$name.json" EVENT_NAME="${3:-issues}" \
    bash .github/scripts/normalize-agent-issue.sh >/dev/null
  if ! grep -qx "should_run=$expected" "$output_file"; then
    echo "Expected $name should_run=$expected" >&2
    cat "$output_file" >&2
    exit 1
  fi
}

run_case low-risk true issues
run_case high-risk false issues
run_case malformed false issues
run_case ready true workflow_dispatch

bash -n .github/scripts/*.sh
echo "Agent loop script fixtures passed."
