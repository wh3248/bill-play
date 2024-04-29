# Import the required libraries

import matplotlib.pyplot as plt
import numpy as np
import os
from parflow import Run
from parflow.tools.io import read_pfb, read_clm
from parflow.tools.fs import mkdir
from parflow.tools.settings import set_working_directory
import subsettools as st
import hf_hydrodata as hf

def main():

    #####
    # 1. Define variables to access datasets in Hydrodata
    #####

    runname = "conus2_mjb"

    # provide a way to create a subset from the conus domain (huc, lat/lon bbox currently supported)
    huc_list = ["15060202"]
    # provide information about the datasets you want to access for run inputs using the data catalog
    start = "2005-10-01"
    end = "2005-10-03"
    grid = "conus2"
    var_ds = "conus2_domain"
    forcing_ds = "CW3E"
    # cluster topology
    P = 1
    Q = 1

    #####
    # set the directory paths where you want to write your subset files
    #####
    home = os.path.expanduser(os.path.abspath("."))
    base_dir = os.path.join(home, "sst_test_basedir")
    input_dir = os.path.join(base_dir, "inputs", f"{runname}_{grid}_{end[:4]}WY")
    output_dir = os.path.join(base_dir, "outputs")
    static_write_dir = os.path.join(input_dir, "static")
    print(base_dir)
    print(input_dir)
    print(output_dir)
    mkdir(static_write_dir)
    forcing_dir = os.path.join(input_dir, "forcing")
    mkdir(forcing_dir)
    pf_out_dir = os.path.join(output_dir, f"{runname}_{grid}_{end[:4]}WY")
    mkdir(pf_out_dir)

    # Set the PARFLOW_DIR path to your local installation of ParFlow.
    # This is only necessary if this environment variable is not already set.
    # os.environ["PARFLOW_DIR"] = "/path/to/your/parflow/installation"

    # load your preferred template runscript
    reference_run = st.get_template_runscript(grid, "transient", "box", pf_out_dir)
    print(f"Reference_run {reference_run}")

    ####
    # 2. Get the desired ParFlow i/j bbox
    ####

    ij_bounds = st.huc_to_ij(huc_list=huc_list, grid=grid)
    print("ij_bound returns [imin, jmin, imax, jmax]")
    print(f"bounding box: {ij_bounds}")

    nj = ij_bounds[3] - ij_bounds[1]
    ni = ij_bounds[2] - ij_bounds[0]
    print(f"nj: {nj}")
    print(f"ni: {ni}")

    #####
    # 3. Make the mask and solid file
    #####
    print("SKIP MASK")
    #mask_solid_paths = st.create_mask_solid(huc_list=huc_list, grid=grid, write_dir=static_write_dir)
    #print(mask_solid_paths)

    ####
    # 4. Subset the static ParFlow inputs
    static_paths = st.subset_static(ij_bounds, dataset=var_ds, write_dir=static_write_dir)
    ####

    ####
    # 5. Configure CLM drivers
    ####
    clm_paths = st.config_clm(ij_bounds, start=start, end=end, dataset=var_ds, write_dir=static_write_dir)


    ####
    # 6. Subset the climate forcing
    ####

    forcing_paths = st.subset_forcing(
        ij_bounds,
        grid=grid,
        start=start,
        end=end,
        dataset=forcing_ds,
        write_dir=forcing_dir,
    )

    ####
    # 7. Spot check subset static and climate forcing with plotting
    ####
    os.chdir(static_write_dir)
    file_name = "pf_indicator.pfb"
    data = read_pfb(file_name)[7] 
    print(data.shape)

    plt.imshow(data, cmap="Reds", origin="lower")
    plt.colorbar()
    plt.title(file_name, fontsize = 14)

    ####
    # 8. Set up a baseline run from a reference yaml
    ####
    runscript_path = st.edit_runscript_for_subset(
        ij_bounds,
        runscript_path=reference_run,
        runname=runname,
        forcing_dir=forcing_dir,
    )
    print(f"Runscript_path '{runscript_path}'")
    ####
    # 9. Copy over your static files to your run directory
    ###
    st.copy_files(read_dir=static_write_dir, write_dir=pf_out_dir)


    ####
    # 10. Change the file names in your runscript if desired
    ####
    init_press_path = os.path.basename(static_paths["ss_pressure_head"])
    depth_to_bedrock_path = os.path.basename(static_paths["pf_flowbarrier"])

    runscript_path = st.change_filename_values(
        runscript_path=runscript_path,
        init_press=init_press_path,
        depth_to_bedrock = depth_to_bedrock_path
    )

    ####
    # 11. Change processor topology if desired 
    ####
    runscript_path = st.dist_run(
        P=P,
        Q=Q,
        runscript_path=runscript_path,
        dist_clim_forcing=True,
    )

    ###
    # 12. Do a baseline run.
    ###
    set_working_directory(f"{pf_out_dir}")
    print(pf_out_dir)

    # load the specified run script
    run = Run.from_definition(runscript_path)
    print(f"Loaded run with runname: {run.get_name()}")

    # The following line is setting the run just for 10 hours for testing purposes
    run.TimingInfo.StopTime = 10

    # The following line updates the root name of your climate forcing. You can comment it out if using NLDAS datasets. 
    run.Solver.CLM.MetFileName = 'CW3E'

    run.run(working_directory=pf_out_dir)


main()
