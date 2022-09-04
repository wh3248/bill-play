#!/bin/bash
#SBATCH --job-name=hydrotest
#SBATCH --ntasks=1
#SBATCH --mem=1gb
#SBATCH --time=00:01:00
#SBATCH --gres=gpu:1
source hydro_env/bin/activate
python c2_test.py 2012 1 hydrodata
