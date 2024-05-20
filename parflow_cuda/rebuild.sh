module purge
module load anaconda3/2022.5
module load cudatoolkit/11.1
module load ucx/1.10.0
module load openmpi/cuda-11.1/gcc/4.1.1
module load cmake/3.18.2
source pf_env.sh

# Download and install ParFlow                                                                                                                    
cd $BASE
cd parflow/
mkdir build
cd build/
cmake .. \
      -DCMAKE_C_FLAGS=-lcuda \
      -DPARFLOW_ENABLE_PYTHON=TRUE \
      -DPARFLOW_AMPS_LAYER=mpi1 \
      -DPARFLOW_AMPS_SEQUENTIAL_IO=TRUE \
      -DPARFLOW_ENABLE_TIMING=TRUE \
      -DCMAKE_INSTALL_PREFIX=$PARFLOW_DIR \
      -DPARFLOW_ACCELERATOR_BACKEND=cuda \
      -DPARFLOW_HAVE_CLM=TRUE
#      -DRMM_ROOT=$RMM_DIR
#      -DHYPRE_ROOT=$HYPRE_DIR                                                                                                                    
#      -DPARFLOW_ENABLE_HDF5=TRUE \     

make
make install