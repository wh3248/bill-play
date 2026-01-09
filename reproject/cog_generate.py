
"""
Generate a COG from an standard tiff file with projection.
Specify the input tiff and the output COG on the command line.

This requires python packages:
    rio
    rio-cogeo
These are both available in parflow-shared.

Curiously the output COG is smaller that an input tiff for the 30m WTD tiff
    TIFF SIZE:  36,629,642,613 bytes = 36 GB
    COG SIZE:   19,197,452,109 bytes = 19 GB

"""

import sys
import time
import subprocess

if len(sys.argv) < 3:
    print("Specify input_tiff and output_cog on command line");
    sys.exit(0)
input_tif = sys.argv[1]
output_cog = sys.argv[2]
print("Generate COG")
print("INPUT", input_tif)
print("OUTPUT", output_cog)

sys.stdout.flush()
time.sleep(1)

# Use rio-cogeo to create a COG
# Specify --overview-level to add pyramids to support zooming
# Specify --web-optimized to align supgrids in COG to mercantile tile grids
start_time = time.time()
subprocess.run([
    "rio", "cogeo", "create",
    input_tif, output_cog,
    "--overview-level", "5",
    "--web-optimized"
])
duration_min = round((time.time() - start_time)/60, 2)
print(f"COG created in {duration_min} minutes")
