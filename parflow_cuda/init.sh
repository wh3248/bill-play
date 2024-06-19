module purge
module load anaconda3/2022.5
#module load ucx/1.10.0

#module load openmpi/cuda-11.1/gcc/4.1.1
module load openmpi/cuda-12.4/gcc/4.1.6
module load cudatoolkit/12.4
#module load nsight-systems/2024.4.1
#module load nvhpc/24.5
#module load openmpi/cuda-12.4/nvhpc-24.5/4.1.6
# CASUES ERRORS module load nvhpc-hpcx-cuda12/24.5
#module load cmake/3.18.2
source /home/wh3248/workspaces/bill-play/parflow_cuda/pf_env.sh
conda activate myenv

