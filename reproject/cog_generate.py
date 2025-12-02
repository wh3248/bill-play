
import sys
import time
import subprocess

input_tif = "/hydrodata/temp/high_resolution_data/WTD_estimates/30m/compressed_data/wtd_mean_estimate_RF_additional_inputs_dummy_drop0LP_1s_CONUS2_m_remapped_unflip_compressed.tif"
output_cog = "us_30m_cog.tif"
output_dir= "/scratch/network/wh3248"
output_cog = f"{output_dir}/wtd_mean_cog.tif"
# Input 36,629,642,613 bytes = 36 GB
# Output 19,197,452,109 bytes = 19 GB

print(f"Input file = '{input_tif}'")
print(f"Output file = '{output_cog}'")
sys.stdout.flush()
time.sleep(1)

# Use rio-cogeo to create a COG
subprocess.run([
    "rio", "cogeo", "create",
    input_tif, output_cog,
    "--overview-level", "5",  # Add pyramids for zooming
    "--web-optimized"         # Optimize for web
])
print(f"COG created: {output_cog}")
