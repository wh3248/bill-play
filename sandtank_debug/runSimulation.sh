#!/bin/bash
set -e

# -----------------------------------------------------------------------------
# User input
# -----------------------------------------------------------------------------
# Expected args:
#   $1  runId
# -----------------------------------------------------------------------------

runId=$1
echo "Starting $runId"
export PARFLOW_DIR=/Users/wh3248/workspaces/trame-sandtank/parflow/opt/parflow

# -----------------------------------------------------------------------------
# Go to run directory
# -----------------------------------------------------------------------------

cd "/Users/wh3248/tmp/sandtank_container/temp/runs/$runId"

# -----------------------------------------------------------------------------
# Run ParFlow
# -----------------------------------------------------------------------------

echo EXECUTE
pwd
tclsh run.tcl $runId
echo "ParFlow Run Complete"


# -----------------------------------------------------------------------------
# Run EcoSLIM for particle tracking
# -----------------------------------------------------------------------------

export OMP_NUM_THREADS=2

FILE=./slimin.txt
if [[ -f "$FILE" ]]; then
  echo "Staring EcoSLIM"
  /Users/wh3248/workspaces/trame-sandtank/parflow/opt/ecoslim/bin/EcoSLIM.exe
  echo "EcoSLIM Run Complete"
fi

# -----------------------------------------------------------------------------
# Need to sleep in order to detect completion
# -----------------------------------------------------------------------------

echo "Complete All"
