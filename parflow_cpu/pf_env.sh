export BASE=$HOME/workspaces/bill-play/parflow_cpu/build
mkdir -p $BASE
export RMM_DIR=$BASE/rmm
export PARFLOW_DIR=$BASE/parflow
export UCX_WARN_UNUSED_ENV_VARS=n
#export HYPRE_DIR=$BASE/hypre                                                                               
export LD_LIBRARY_PATH=$RMM_DIR/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$PARFLOW_DIR/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$HYPRE_DIR/lib:$LD_LIBRARY_PATH
export PATH=$PARFLOW_DIR/bin:$PATH
