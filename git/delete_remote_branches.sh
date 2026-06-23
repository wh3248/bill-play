#!/usr/bin/env bash
# Generates execute_deletes.sh containing git push --delete commands
# for all remote branches EXCEPT main and grid_lines.
# Review execute_deletes.sh, then run it to perform the deletions.

set -euo pipefail

REMOTE="origin"
KEEP=("main" "grid_lines")
OUTPUT="execute_deletes.sh"

branches_to_delete=$(git branch -r \
  | grep "^  ${REMOTE}/" \
  | grep -v "^  ${REMOTE}/HEAD" \
  | sed "s|^  ${REMOTE}/||" \
  | grep -vE "^($(IFS='|'; echo "${KEEP[*]}"))$")

if [[ -z "$branches_to_delete" ]]; then
  echo "No branches to delete."
  exit 0
fi

{
  echo "#!/usr/bin/env bash"
  echo "set -euo pipefail"
  echo ""
  while IFS= read -r branch; do
    echo "git push ${REMOTE} --delete \"${branch}\""
  done <<< "$branches_to_delete"
} > "$OUTPUT"

chmod +x "$OUTPUT"

echo "Written $(echo "$branches_to_delete" | wc -l | tr -d ' ') delete commands to ${OUTPUT}."
echo "Review it, then run: ./${OUTPUT}"
