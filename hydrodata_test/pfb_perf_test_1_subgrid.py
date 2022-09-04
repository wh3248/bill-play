#
# Performance test for reading PFB files.
# This tests reads 1800 PFB files of 5 variables for 90 days for 4 water years
# For each PFB files it reads 1 file header, 1 subgrid header (first block) 1 subgrid block into a ndarray
#   (the contents of the subgrid header of the block is inferred from the file header and first subgrid header info)
# this taks about 60 seconds cold and 11 seconds hot reading from snake
#

FORCING_FILES_PATH = "/hydrodata/forcing/processed_data/CONUS2/NLDAS3/daily"
from parflow import read_pfb

import sys
import os
import time
import dask
import mmap
import math
import numpy as np

def main():
    start_time = time.time()
    water_years = [2001, 2002, 2003, 2004]
    variables = ["Temp.daily.mean", "Temp.daily.min", "Temp.daily.max", "APCP.daily.sum", "DSWR.daily.mean"]
    # variables = ["Temp.daily.mean"]
    days = range(0,90)
    dask_results = []
    for water_year in water_years:
        dir_path = f"{FORCING_FILES_PATH}/WY{water_year}"
        for variable in variables:
            for day in days:
                day_format = f"{day+1:03d}"
                pfb_path = f"{dir_path}/NLDAS.{variable}.{day_format}.pfb"
                if os.path.exists(pfb_path):
                    dask_results.append(read_file(pfb_path))
    dask.delayed(lambda x: x)(dask_results).compute(num_workers=4)
    duration = round(time.time() - start_time, 2)
    nfiles = len(dask_results)
    print(f"{nfiles} files in {duration} seconds.")

class PFBSubgridHeader:
    def __init__(self):
        self.ix = None
        self.iy = None
        self.iz = None
        self.nx = None
        self.ny = None
        self.nz = None
        self.rx = None
        self.ry = None
        self.rz = None
    def read_subgrid_header(self, f, position):
        dt32 = np.dtype(np.int32).newbyteorder(">")
        dt64 = np.dtype(np.int64).newbyteorder(">")
        dt32_size = 4
        dt64_size = 8
        data = read_block_into_np(f, position, dt32, dt32_size, 9)
        self.ix = data[0]
        self.iy = data[1]
        self.iz = data[2]
        self.nx = data[3]
        self.ny = data[4]
        self.nz = data[5]
        self.rx = data[6]
        self.ry = data[7]
        self.rz = data[8]
        return data


class PFBHeader:
    def __init__(self):
        self.nx = None
        self.ny = None
        self.nz = None
        self.p = None
        self.q = None
        self.r = None
        self.n_subgrids = 0
        self.sg_nx = None
        self.sg_ny = None
        self.sg_nz = None
    def read_header(self, f):
        dt32 = np.dtype(np.int32).newbyteorder(">")
        dt32_size = 4
        dt64_size = 8
        pos = dt64_size * 3
        data = read_block_into_np(f, pos, dt32, dt32_size, 3)
        self.nx = int(data[0])
        self.ny = int(data[1])
        self.nz = int(data[2])
        pos = dt64_size * 3 +  dt32_size * 3 + dt64_size * 3
        data = read_block_into_np(f, pos, dt32, 4, 1)
        self.n_subgrids = data[0]
        pos = pos + dt32_size
        first_subgrid_header = PFBSubgridHeader()
        first_subgrid_header.read_subgrid_header(f, pos)
        self.p = math.ceil(self.nx / first_subgrid_header.nx)
        self.q = math.ceil(self.ny / first_subgrid_header.ny)
        self.r = math.ceil(self.nz / first_subgrid_header.nz)
        self.sg_nx = first_subgrid_header.nx
        self.sg_ny = first_subgrid_header.ny
        self.sg_nz = first_subgrid_header.nz

def run_task(pfb_path):
    with open(pfb_path, "rb") as f:
        header = PFBHeader()
        header.read_header(f)
        grid_nx = header.sg_nx
        grid_ny = header.sg_ny
        grid_nz = header.sg_nz
        p = header.p
        q = header.q
        r = header.r
        n_subgrids = header.n_subgrids
        remainder_x = header.nx - p * (grid_nx - 1)
        remainder_x = remainder_x if remainder_x > 0 else p
        remainder_y = int(header.q - (grid_ny * q - header.ny))
        x = 24
        y = 24
        z = 0
        grid_number = z * header.p * header.q + y * header.p + x
        # there are 4 sizes of subgrids in the file. For example, assume a full grid size is 93x68
        # Assume p=48 and q=48 and remainder_x = 20 and remainer_y=8.
        # There are full sized subgrids, subgrids with remainder_x size, subgrids with reminder_y size, and both
        # Each subgrid has a subgrid header of 9 integers of 4 bytes each

        ##############################################################
        #   93x68  (28x40 subgrids)   #   93x68  ( 20x68 subgrids)   #
        ##############################################################
        #   93x67  (38x8 subgrids)    #   92x67  (20x67 subgrids)    #
        ##############################################################

        pos = 64 + grid_number * 4*9   # subgrid headers for subgrids up to this point
        # Add up position for fully completed rows
        pos = pos + 8 * grid_nx * grid_ny * min(y, remainder_y) * remainder_x # rows
        pos = pos + 8 * (grid_nx - 1) * (grid_ny) * min(y, remainder_y) * (p - remainder_x)
        pos = pos + 8 * grid_nx * (grid_ny-1) * max(y- remainder_y, 0) * remainder_x
        pos = pos + 8 * (grid_nx - 1) * (grid_ny - 1) * max(y- remainder_y, 0) * (p -remainder_x)
        # Add up position for partially completed rows
        if y < remainder_y:
            pos = pos + 8 * (grid_nx) * grid_ny * min(x, remainder_x)
            pos = pos + 8 * (grid_nx-1) * (grid_ny) * max(x - remainder_x, 0)
        else:
            pos = pos + 8 * (grid_nx) * (grid_ny-1) * min(x, remainder_x)
            pos = pos + 8 * (grid_nx-1) * (grid_ny -1) * max(x - remainder_x, 0)


        sg_nx = grid_nx if x <= remainder_x else grid_nx - 1
        sg_ny = grid_ny if y <= remainder_y else grid_ny - 1
        data = read_subgrid(f, pos, sg_nx, sg_ny)
                        
    return "Done"

def read_block_into_np(f, position, dtype, dtype_length, n_elements):
    f.seek(position)
    buffer = f.read(n_elements * dtype_length)
    data = np.frombuffer(buffer, dtype=dtype)
    return data

def read_subgrid(f, position, sg_nx, sg_ny):
    f.seek(position + 9 *4)
    dtype = np.dtype('f8').newbyteorder(">")
    buffer = f.read(sg_nx * sg_ny * 8)
    data = np.frombuffer(buffer, dtype=dtype)
    data = np.reshape(data, (sg_nx, sg_ny))
    return data

def read_file(pfb_path):
    return dask.delayed(run_task)(pfb_path)
main()

