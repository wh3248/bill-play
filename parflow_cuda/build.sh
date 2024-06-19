# Build script for CUDA Parflow BUILD
source init.sh

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
cd src && ./configure --with-cuda --with-cuda-home=$CUDA_HOME --with-gpu-arch='80' --prefix=$HYPRE_DIR && \
make install

# Download and install ParFlow                                                                                                                    
cd $BASE
echo $BASE
#git clone git@github.com:mfahdaz/parflow.git
# git clone https://github.com/parflow/parflow.git
git clone git@github.com:gartavanis/parflow.git
cd parflow/
git checkout hackathon-bill
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
      '-DCMAKE_CUDA_ARCHITECTURES=80;86'  \
      -DCMAKE_DEBUG_FLAG=Debug   \
      -DPARFLOW_HAVE_CLM=TRUE \
      -DRMM_ROOT=$RMM_DIR
#      -DPARFLOW_ENABLE_HDF5=TRUE \     

make
make install