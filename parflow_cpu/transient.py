"""
Run parflow for a transient run using PFB files collected from hf_hydrodata.
"""
import os
import pathlib
import parflow as pf
from typing import List
import numpy as np
import hf_hydrodata as hf
import subsettools.subsettools
import subsettools.subset_utils

def main():
    """Execute a parflow simulation using data collected from hf_hydrodata."""

    parflow_output_dir = os.path.abspath("test_output")
    os.makedirs(parflow_output_dir, exist_ok=True)

    huc_ids= ["15060202"]
    start_time = "2005-10-01"
    end_time = "2005-10-03"

    print("Collect static inputs...")
    (nz, ny, nx) = collect_static_inputs(huc_ids, parflow_output_dir, start_time, end_time)

    print("Collect forcing files...")
    collect_forcing(huc_ids, parflow_output_dir, start_time, end_time)

    print(f"Run parflow on grid ({nz}, {ny}, {nx})")
    run_parflow(nx, ny, nz, parflow_output_dir)

def collect_static_inputs(huc_ids:List[str], parflow_output_dir:str, start_time:str, end_time:str):
    """
    Collect static input pfb input files from hf_hydrodata and subset to the huc_id list.
    Parameters:
        huc_ids:                List of HUC ids to be used for subsetting.
        parflow_output_dir:     Directory path to write parflow input and output files of the simulation.
        start_time:             Start time of the simulation as string YYYY-MM-DD.
        end_time:               End time of the simulation as string YYYY-MM-DD.
    """

    huc_id = ",".join(huc_ids)

    for variable in ["slope_x", "slope_y", "pf_indicator", "ss_pressure_head", "pme", "mannings", "pf_flowbarrier"]:
        filter_options = dict(dataset="conus2_domain", variable=variable, huc_id=huc_id)
        data = hf.get_gridded_data(filter_options)
        if len(data.shape) == 2:
            # PFB files require shape with 3 dimensions
            data = np.reshape(data, (1, data.shape[0], data.shape[1]))
        else:
            result = data.shape
        pf.write_pfb(f"{parflow_output_dir}/{variable}.pfb", data, dx=1000, dy=1000, yz=100, dist=True)
    
    hf.get_raw_file(f"{parflow_output_dir}/drv_vegp.dat", dict(dataset="conus2_domain", variable="clm_run", file_type="vegp"));
    vegm_data = hf.get_gridded_data(dataset="conus2_domain", variable="clm_run", file_type="pfb", huc_id=huc_id)
    land_cover_data = subsettools.subsettools._reshape_ndarray_to_vegm_format(vegm_data)
    file_path = subsettools.subset_utils.write_land_cover(land_cover_data, parflow_output_dir)

    drv_clm_path = f"{parflow_output_dir}/drv_clmin.dat"
    hf.get_raw_file(drv_clm_path, dict(dataset="conus2_domain", variable="clm_run", file_type="drv_clm"));
    subsettools.subset_utils.edit_drvclmin(file_path=drv_clm_path, start=start_time, end=end_time, time_zone="UTC")
    return result

def collect_forcing(huc_ids:List[str], parflow_output_dir:str, start_time:str, end_time:str):
    """
    Collect forcing files from hf_hydrodata into parflow_output_dir directory.
    Parameters:
        huc_ids:                List of HUC ids to be used for subsetting.
        parflow_output_dir:     Directory path to write parflow input and output files of the simulation.
        start_time:             Start time of the simulation as string YYYY-MM-DD.
        end_time:               End time of the simulation as string YYYY-MM-DD.
    """

    huc_id = ",".join(huc_ids)
    dataset = "CW3E"
    variables = ["precipitation", "downward_shortwave", "downward_longwave", "air_temp", "east_windspeed", "north_windspeed", "atmospheric_pressure", "specific_humidity"]
    filter_options = dict(dataset=dataset, huc_id=huc_id, start_time=start_time, end_time=end_time, temporal_resolution="hourly")
    output_template = "{dataset}.{dataset_var}.{hour_start:06d}_to_{hour_end:06d}.pfb"
    output_template = f"test_output/{output_template}"
    hf.get_gridded_files(filter_options, variables=variables, filename_template=output_template)

    # Create P,Q,R dist files for the downloaded forcing files
    for file_name in os.listdir(parflow_output_dir):
        if file_name.startswith(dataset) and file_name.endswith(".pfb"):
            data = pf.read_pfb(f"{parflow_output_dir}/{file_name}")
            pf.write_pfb(f"{parflow_output_dir}/{file_name}", data, dx=1000, dy=1000, yz=100, dist=True)

def run_parflow(nx, ny, nz, parflow_output_dir):
    """
    Run a parflow simulation using pftools interface to parflow.
        
    Parameters:
        nx:                     x dimension size of the subset domain.
        ny:                     y dimension size of the subset domain.
        nz:                     z dimension size of the subset domain for input/outputs that are 3D.
        parflow_output_dir:     Directory path to write parflow input and output files of the simulation.
    """
    print(nx, ny, nz)
    parflow_run = pf.Run.from_definition(pathlib.Path("transient.yaml"))
    parflow_run.ComputationalGrid.NX = nx
    parflow_run.ComputationalGrid.NY = ny
    parflow_run.ComputationalGrid.NZ = nz
    parflow_run.Process.Topology.P = 1
    parflow_run.Process.Topology.Q = 1
    parflow_run.Process.Topology.R = 1
    parflow_run.TimingInfo.StopTime = 10
    parflow_run.TimingInfo.DumpInterval = 1.0
    parflow_run.Solver.MaxConvergenceFailures = 20
    parflow_run.Geom.domain.Upper.X = nx * 1000
    parflow_run.Geom.domain.Upper.Y = ny * 1000
    parflow_run.Solver.CLM.MetFileName = "CW3E"
    parflow_run.Solver.CLM.MetFilePath = parflow_output_dir
    parflow_run.Geom.domain.FBz.FileName = "pf_flowbarrier.pfb"
    parflow_run.Geom.domain.ICPressure.FileName = "ss_pressure_head.pfb"
    parflow_run.Geom.indi_input.FileName = "pf_indicator.pfb"
    parflow_run.Mannings.FileName = "mannings.pfb"

    # Run parflow simulation
    parflow_run.run(parflow_output_dir)

if __name__ == "__main__":
    main()
