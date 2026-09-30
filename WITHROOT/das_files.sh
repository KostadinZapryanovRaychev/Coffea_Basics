#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "usage: $0 '<dataset pattern>' [max files per dataset]" >&2
    exit 1
fi

pattern="$1"
maxFiles="${2:-0}"
redirector="root://cms-xrd-global.cern.ch/"

outDir="outputs"
mkdir -p "$outDir"
safeName=$(echo "$pattern" | tr -c 'A-Za-z0-9' '_' | sed 's/_\{2,\}/_/g; s/^_//; s/_$//')
outFile="${outDir}/das_files_${safeName}.txt"

for dataset in $(dasgoclient -query="dataset=${pattern}"); do
    echo "dataset: ${dataset}" >&2
    files=$(dasgoclient -query="file dataset=${dataset}")
    if [ "$maxFiles" -gt 0 ]; then
        files=$(echo "$files" | head -n "$maxFiles")
    fi
    echo "$files"
done | grep '^/store/' | sort -u | sed "s|^|${redirector}|" | tee "$outFile"

echo "wrote $(wc -l < "$outFile" | tr -d ' ') path(s) to ${outFile}" >&2
