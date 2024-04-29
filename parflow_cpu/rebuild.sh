module purge
module load anaconda3/2022.5
module load cudatoolkit/11.1
module load ucx/1.10.0
module load openmpi/cuda-11.1/gcc/4.1.1
module load cmake/3.18.2
source pf_env.sh

# Download and install ParFlow                                                                                                                    
cd $BASE/parflow/build
export HYPRE_DIR=$BASE/hypre
cmake .. \
      -DCMAKE_INSTALL_PREFIX=$PARFLOW_DIR             \
      -DHYPRE_ROOT=$HYPRE_DIR                         \
      -DHYPRE_DIR=$HYPRE_DIR                         \
      -DPARFLOW_ENABLE_PYTHON=TRUE                    \
      -DPARFLOW_HAVE_CLM=TRUE                         \
      -DCMAKE_BUILD_TYPE=Release                      \
      -DPARFLOW_AMPS_LAYER=mpi1                       \
      -DPARFLOW_AMPS_SEQUENTIAL_IO=ON                 \
      -DPARFLOW_ENABLE_HYPRE=ON                       \
      -DPARFLOW_ENABLE_SIMULATOR=ON                   \
      -DPARFLOW_ENABLE_SZLIB=ON                       \
      -DPARFLOW_ENABLE_TOOLS=ON                       \
      -DPARFLOW_ENABLE_ZLIB=ON

make
make install