#!/bin/bash
#SBATCH --job-name=cog_generate
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=4G
#SBATCH --time=03:00:00
module load parflow-shared
source ~/anaconda3/bin/activate
#INPUT_FILE=/hydrodata/temp/high_resolution_data/WTD_estimates/30m/compressed_data/wtd_mean_estimate_RF_additional_inputs_dummy_drop0LP_1s_CONUS2_m_remapped_unflip_compressed.tif 
#OUTPUT_FILE=/scratch/network/wh3248/conus2_current_conditions/wtd_mean_cog.tif
INPUT_FILE=/hydrodata/national_obs/groundwater/data/ma_2025/wtd_mean_estimate_RF_additional_inputs_dummy_drop0LP_1s_CONUS2_m_v_20240813.tif
OUTPUT_FILE=/scratch/network/wh3248/ma2025/wtd_mean_cog.tif
python cog_generate.py $INPUT_FILE $OUTPUT_FILE
