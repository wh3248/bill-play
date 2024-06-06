# Load modules for CPU version of parflow
module purge
module load anaconda3/2022.5
#module load cudatoolkit/11.1
#module load ucx/1.10.0
module load ucx/1.9.0
#module load openmpi/cuda-11.1/gcc/4.1.1
module load openmpi/gcc/4.1.2
module load cmake/3.18.2
source pf_env.sh
conda activate myenv

