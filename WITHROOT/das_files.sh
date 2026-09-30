#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "usage: $0 '<dataset pattern>' [max files per dataset]" >&2
    exit 1
fi

pattern="$1"
maxFiles="${2:-0}"
redirector="root://cms-xrd-global.cern.ch/"

for dataset in $(dasgoclient -query="dataset=${pattern}"); do
    echo "dataset: ${dataset}" >&2
    files=$(dasgoclient -query="file dataset=${dataset}")
    if [ "$maxFiles" -gt 0 ]; then
        files=$(echo "$files" | head -n "$maxFiles")
    fi
    echo "$files"
done | grep '^/store/' | sort -u | sed "s|^|${redirector}|"
