#!/bin/bash
# Runs on the worker node. CRAB has already rewritten PSet.py's
# process.source.fileNames with this job's assigned input file(s); we read
# that back with python instead of assuming an argument, since scriptExe is
# called as `crab_script.sh <jobId> <scriptArgs...>`, not with the input
# file as $1.
set -e

INPUT_FILE=$(python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('pset', 'PSet.py')
pset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pset)
print(pset.process.source.fileNames[0])
")

echo "crab_script.sh: input file = ${INPUT_FILE}"

root -l -b -q "BranchSummary.C(\"${INPUT_FILE}\")"

echo "crab_script.sh: done"
