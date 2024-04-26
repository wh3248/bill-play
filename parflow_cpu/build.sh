module purge
module load anaconda3/2022.5
module load cudatoolkit/11.1
module load ucx/1.10.0
module load openmpi/cuda-11.1/gcc/4.1.1
module load cmake/3.18.2
source pf_env.sh

# Download and install HYPER
export HYPRE_DIR=$BASE/hypre
mkdir -p $HYPRE_DIR

cd $HYPRE_DIR
curl -L https://github.com/hypre-space/hypre/archive/v2.17.0.tar.gz | tar --strip-components=1 -xzv && \
cd src && ./configure --prefix=$HYPRE_DIR --with-MPI && \
make install


# Download and install ParFlow                                                                                                                    
cd $BASE
git clone https://github.com/parflow/parflow.git
cd parflow/
mkdir build
cd build/
cmake .. \
      -DCMAKE_INSTALL_PREFIX=$PARFLOW_DIR             \
      -DHYPRE_ROOT=$HYPRE_DIR                         \
      -DPARFLOW_ENABLE_PYTHON=TRUE                    \
      -DPARFLOW_HAVE_CLM=TRUE                         \
      -DHYPRE_ROOT=./hypre                            \
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