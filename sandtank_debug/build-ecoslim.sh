#!/usr/bin/env bash
CURRENT_DIR=`dirname "$0"`

cd $CURRENT_DIR
ROOT_DIR=$PWD
CODE_DIR=$PWD/src

module load cmake/3.18.2
module load gcc/8
module load parflow/3.10.0

mkdir -p $CODE_DIR

# -----------------------------------------------------------------------------
# exit when any command fails
# -----------------------------------------------------------------------------

set -e

# -----------------------------------------------------------------------------
# Hypre
# -----------------------------------------------------------------------------

cd $CODE_DIR
git clone --recursive https://github.com/reedmaxwell/EcoSLIM.git
cd EcoSLIM

cmake .
cmake --build .
cmake --install . --prefix ${CURRENT_DIR}/ecoslim