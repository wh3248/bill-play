# Build script for CUDA Parflow BUILD
module purge
module load anaconda3/2022.5
module load cudatoolkit/11.1
module load ucx/1.10.0
module load openmpi/cuda-11.1/gcc/4.1.1
module load cmake/3.18.2
source pf_env.sh

# Download and install CUDA memory model, RMM
mkdir -p $BASE                                                                                     
cd $BASE
git clone -b branch-0.10 --single-branch --recurse-submodules https://github.com/hokkanen/rmm
cd rmm/
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$RMM_DIR
make -j
make install
make test

# Download and install HYPER
export HYPRE_DIR=$BASE/hypre
mkdir -p $HYPRE_DIR

cd $HYPRE_DIR
curl -L https://github.com/hypre-space/hypre/archive/v2.31.0.tar.gz | tar --strip-components=1 -xzv && \
cd src && ./configure --prefix=$HYPRE_DIR && \
make install

# Download and install ParFlow                                                                                                                    
cd $BASE
echo $BASE
pwd
git clone https://github.com/parflow/parflow.git
echo "CLONED PARFLOW"
cd parflow/
mkdir build
cd build/
cmake .. \
      -DCMAKE_C_FLAGS=-lcuda \
      -DPARFLOW_ENABLE_PYTHON=TRUE \
      -DPARFLOW_AMPS_LAYER=mpi1 \
      -DHYPRE_ROOT=$HYPRE_DIR                         \
      -DHYPRE_DIR=$HYPRE_DIR                         \
      -DPARFLOW_AMPS_SEQUENTIAL_IO=TRUE \
      -DPARFLOW_ENABLE_TIMING=TRUE \
      -DCMAKE_INSTALL_PREFIX=$PARFLOW_DIR \
      -DPARFLOW_ACCELERATOR_BACKEND=cuda \
      -DPARFLOW_HAVE_CLM=TRUE \
      -DRMM_ROOT=$RMM_DIR
#      -DHYPRE_ROOT=$HYPRE_DIR                                                                                                                    
#      -DPARFLOW_ENABLE_HDF5=TRUE \     

make
make install