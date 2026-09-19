#!/usr/bin/env bash
set -euo pipefail

project_dir="${1:-$PWD}"
if [[ ! -d "$project_dir" ]]; then
  printf 'Project directory not found: %s\n' "$project_dir" >&2
  exit 2
fi
project_dir="$(cd "$project_dir" && pwd)"

printf 'project\t%s\n' "$project_dir"
printf 'project_size\t'
du -sh "$project_dir" | awk '{print $1}'

printf 'candidate\tsize\tpath\n'
candidate_paths=(
  "$project_dir/node_modules"
  "$project_dir/client/node_modules"
  "$project_dir/server/node_modules"
  "$project_dir/cli/node_modules"
  "$project_dir/desktop/node_modules"
  "$project_dir/client/dist"
  "$project_dir/server/dist"
  "$project_dir/cli/dist"
  "$project_dir/desktop/build"
  "$project_dir/desktop/client-dist"
  "$project_dir/desktop/dist-electron"
)

for candidate in "${candidate_paths[@]}"; do
  if [[ -e "$candidate" ]]; then
    size="$(du -sh "$candidate" | awk '{print $1}')"
    printf 'reproducible\t%s\t%s\n' "$size" "$candidate"
  fi
done

printf 'top_level\tsize\tpath\n'
for entry in "$project_dir"/* "$project_dir"/.[!.]*; do
  [[ -e "$entry" ]] || continue
  [[ "$entry" == "$project_dir/.git" ]] && continue
  size="$(du -sh "$entry" 2>/dev/null | awk '{print $1}')"
  printf 'top_level\t%s\t%s\n' "$size" "$entry"
done | sort -k2,2h
