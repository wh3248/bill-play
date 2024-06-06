#!/bin/bash                                                                                                                                           
#SBATCH --job-name=parflow_cuda  # create a short name for your job                                                                               
#SBATCH --nodes=1                # node count                                                                                                         
#SBATCH --ntasks=1               # total number of tasks across all nodes                                                                             
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)                                                                    
#SBATCH --mem-per-cpu=4G         # memory per cpu-core (4G is default)                                                                                
#SBATCH --time=00:30:00          # total run time limit (HH:MM:SS)                                                                                    
#SBATCH --gres=gpu:1                                                                                                                                  
#SBATCH --constraint=gpu80                                                                                                                          
#SBATCH --mail-type=begin        # send email when job begins                                                                                         
#SBATCH --mail-type=end          # send email when job ends                                                                                           
#SBATCH --mail-type=fail         # send email if job fails                                                                                            
#SBATCH --mail-user=wh3248@princeton.edu
cd $HOME/workspaces/bill-play/parflow_cuda
module purge
source init.sh
cd test_output
ls ${PARFLOW_DIR}/bin/parflow
nsys profile --output transient.nsys-rep ${PARFLOW_DIR}/bin/parflow transient
