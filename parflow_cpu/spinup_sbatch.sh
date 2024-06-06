#!/bin/bash                                                                                                                                           
#SBATCH --job-name=parflow_cpu   # create a short name for your job                                                                               
#SBATCH --nodes=1                # node count                                                                                                         
#SBATCH --ntasks=1               # total number of tasks across all nodes                                                                             
#SBATCH --cpus-per-task=1       # cpu-cores per task (>1 if multi-threaded tasks)                                                                    
#SBATCH --mem-per-cpu=4G         # memory per cpu-core (4G is default)                                                                                
#SBATCH --time=00:30:00          # total run time limit (HH:MM:SS) 
                                                                                 
cd $HOME/workspaces/bill-play/parflow_cpu
echo "List directory"
ls /usr/local/share/Modules/modulefiles/ucx
module purge
source init.sh
python spinup.py run
