#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "usage: $0 '<dataset pattern>' [max files per dataset] [data|mc]" >&2
    exit 1
fi

pattern="$1"
maxFiles="${2:-0}"
kind="${3:-any}"
redirector="root://cms-xrd-global.cern.ch/"

outDir="outputs"
mkdir -p "$outDir"
safeName=$(echo "$pattern" | tr -c 'A-Za-z0-9' '_' | sed 's/_\{2,\}/_/g; s/^_//; s/_$//')
outFile="${outDir}/das_files_${safeName}.txt"
jsonOutFile="${outDir}/das_files_${safeName}.paths.json.txt"

for dataset in $(dasgoclient -query="dataset=${pattern}"); do
    # real data tier is NANOAOD, MC tier is NANOAODSIM -- skip datasets that
    # don't match the requested kind, so a wildcard pattern can't accidentally
    # pull in the other kind
    tier="${dataset##*/}"
    if [ "$kind" = "data" ] && [ "$tier" = "NANOAODSIM" ]; then
        continue
    fi
    if [ "$kind" = "mc" ] && [ "$tier" != "NANOAODSIM" ]; then
        continue
    fi
    echo "dataset: ${dataset}" >&2
    files=$(dasgoclient -query="file dataset=${dataset}")
    if [ "$maxFiles" -gt 0 ]; then
        files=$(echo "$files" | head -n "$maxFiles")
    fi
    echo "$files"
done | grep '^/store/' | sort -u | sed "s|^|${redirector}|" | tee "$outFile" > /dev/null

cat "$outFile"

# same paths, quoted and comma-terminated, ready to paste into a
# file_config*.json "paths" array (last line has no trailing comma)
totalLines=$(wc -l < "$outFile" | tr -d ' ')
awk -v total="$totalLines" '{ printf "        \"%s\"%s\n", $0, (NR < total ? "," : "") }' "$outFile" > "$jsonOutFile"

echo "wrote $(wc -l < "$outFile" | tr -d ' ') path(s) to ${outFile}" >&2
echo "wrote JSON-ready paths to ${jsonOutFile}" >&2
