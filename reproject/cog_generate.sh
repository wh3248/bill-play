#!/bin/bash
#SBATCH --job-name=cog_generate
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=4G
#SBATCH --time=03:00:00
module load parflow-shared
source ~/anaconda3/bin/activate
python cog_generate.py
