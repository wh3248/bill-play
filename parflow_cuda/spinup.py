"""
Run parflow for a spinup run using PFB files collected from hf_hydrodata.
"""

# pylint: disable=W0212, E1101
import sys
import os
import time
from typing import List, Tuple
import datetime
import pathlib
import parflow as pf
import numpy as np
import hf_hydrodata as hf
import subsettools.subsettools
import subsettools.subset_utils


def main():
    """Execute a parflow simulation using data collected from hf_hydrodata."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    parflow_output_dir = os.path.abspath("test_output")
    os.makedirs(parflow_output_dir, exist_ok=True)

    huc_ids = ["15060202"]
    start_time = "2005-10-01"
    end_time = "2005-10-02"
    topology = (1, 1, 1)
    shape = get_forcing_shape(parflow_output_dir)

    if not mode == "run":
        if shape is None:
            print("Collect static inputs...")
            shape = collect_static_inputs(
                huc_ids, topology, parflow_output_dir, start_time, end_time
            )

            print("Collect forcing files...")
            collect_forcing(huc_ids, topology, parflow_output_dir, start_time, end_time)

    if mode in ["run", "all"]:
        print(f"Run parflow on grid ({shape})")
        run_parflow(shape, topology, parflow_output_dir, start_time, end_time)


def collect_static_inputs(
    huc_ids: List[str],
    topology: Tuple[int],
    parflow_output_dir: str,
    start_time: str,
    end_time: str,
):
    """
    Collect static input pfb input files from hf_hydrodata and subset to the huc_id list.
    Parameters:
        huc_ids:                List of HUC ids to be used for subsetting.
        parflow_output_dir:     Path to parflow input/output directory.
        start_time:             Start time of the simulation as string YYYY-MM-DD.
        end_time:               End time of the simulation as string YYYY-MM-DD.
    """

    huc_id = ",".join(huc_ids)

    for variable in [
        "slope_x",
        "slope_y",
        "pf_indicator",
        "ss_pressure_head",
        "pme",
        "mannings",
        "pf_flowbarrier",
    ]:
        filter_options = {
            "dataset": "conus2_domain",
            "variable": variable,
            "huc_id": huc_id,
        }
        data = hf.get_gridded_data(filter_options)
        if len(data.shape) == 2:
            # PFB files require shape with 3 dimensions
            data = np.reshape(data, (1, data.shape[0], data.shape[1]))
        else:
            result = data.shape
        pf.write_pfb(
            f"{parflow_output_dir}/{variable}.pfb",
            data,
            dx=1000,
            dy=1000,
            yz=100,
            p=topology[0],
            q=topology[1],
            r=topology[2],
            dist=True,
        )

    hf.get_raw_file(
        f"{parflow_output_dir}/drv_vegp.dat",
        dataset="conus2_domain",
        variable="clm_run",
        file_type="vegp",
    )
    vegm_data = hf.get_gridded_data(
        dataset="conus2_domain", variable="clm_run", file_type="pfb", huc_id=huc_id
    )
    land_cover_data = subsettools.subsettools._reshape_ndarray_to_vegm_format(vegm_data)
    subsettools.subset_utils.write_land_cover(land_cover_data, parflow_output_dir)

    drv_clm_path = f"{parflow_output_dir}/drv_clmin.dat"
    hf.get_raw_file(
        drv_clm_path,
        dataset="conus2_domain",
        variable="clm_run",
        file_type="drv_clm",
    )
    subsettools.subset_utils.edit_drvclmin(
        file_path=drv_clm_path, start=start_time, end=end_time, time_zone="UTC")
    subsettools.create_mask_solid(
        huc_ids,
        "conus2",
        parflow_output_dir
    )
    return result


def collect_forcing(
    huc_ids: List[str],
    topology: Tuple[int],
    parflow_output_dir: str,
    start_time: str,
    end_time: str,
):
    """
    Collect forcing files from hf_hydrodata into parflow_output_dir directory.
    Parameters:
        huc_ids:                List of HUC ids to be used for subsetting.
        topology:               Parflow execution topology as (P, Q, R).
        parflow_output_dir:     Path to parflow input/output directory.
        start_time:             Start time of the simulation as string YYYY-MM-DD.
        end_time:               End time of the simulation as string YYYY-MM-DD.
    """

    huc_id = ",".join(huc_ids)
    dataset = "CW3E"
    variables = [
        "precipitation",
        "downward_shortwave",
        "downward_longwave",
        "air_temp",
        "east_windspeed",
        "north_windspeed",
        "atmospheric_pressure",
        "specific_humidity",
    ]
    filter_options = {
        "dataset": dataset,
        "huc_id": huc_id,
        "start_time": start_time,
        "end_time": end_time,
        "temporal_resolution": "hourly",
    }
    output_template = "{dataset}.{dataset_var}.{hour_start:06d}_to_{hour_end:06d}.pfb"
    output_template = f"test_output/{output_template}"
    hf.get_gridded_files(
        filter_options, variables=variables, filename_template=output_template
    )

    # Create P,Q,R dist files for the downloaded forcing files
    for file_name in os.listdir(parflow_output_dir):
        if file_name.startswith(dataset) and file_name.endswith(".pfb"):
            data = pf.read_pfb(f"{parflow_output_dir}/{file_name}")
            pf.write_pfb(
                f"{parflow_output_dir}/{file_name}",
                data,
                dx=1000,
                dy=1000,
                yz=100,
                p=topology[0],
                q=topology[1],
                r=topology[2],
                dist=True,
            )


def run_parflow(
    shape: Tuple[int],
    topology: Tuple[int],
    parflow_output_dir,
    start_time: str,
    end_time: str,
):
    """
    Run a parflow simulation using pftools interface to parflow.

    Parameters:
        shape:                  Subset domain shape as (z, y, x) tuple.
        topology:               Processor topology as (p, q, r) tuple.
        parflow_output_dir:     Path to parflow input/output directory.
        start_time:             Start time of the simulation as string YYYY-MM-DD.
        end_time:               End time of the simulation as string YYYY-MM-DD.
    """
    duration_start = time.time()
    parflow_run = pf.Run.from_definition(pathlib.Path("conus2_spinup_solid.yaml"))
    days = (
        (datetime.datetime.strptime(end_time, "%Y-%m-%d")
        - datetime.datetime.strptime(start_time, "%Y-%m-%d")).days
    )

    parflow_run.ComputationalGrid.NX = shape[2]
    parflow_run.ComputationalGrid.NY = shape[1]
    parflow_run.ComputationalGrid.NZ = shape[0]
    parflow_run.Process.Topology.P = topology[0]
    parflow_run.Process.Topology.Q = topology[1]
    parflow_run.Process.Topology.R = topology[2]
    parflow_run.TimingInfo.StopTime = days * 24
    parflow_run.Solver.MaxIter = 50
    parflow_run.Solver.Linear.Preconditioner = "MGSemi"   #MGSemi  #PFMG
    parflow_run.Solver.Linear.Preconditioner.PCMatrixType = 'PFSymmetric'

    parflow_run.Solver.Nonlinear.EtaChoice = 'EtaConstant'
    parflow_run.Solver.Nonlinear.EtaValue = 0.01
    parflow_run.Solver.Nonlinear.UseJacobian = True
    parflow_run.Solver.Nonlinear.StepTol = 1e-15
    parflow_run.Solver.Nonlinear.Globalization = 'LineSearch'
    parflow_run.Solver.Linear.KrylovDimension = 500
    parflow_run.Solver.Linear.MaxRestarts = 8

    parflow_run.TimingInfo.DumpInterval = 1.0
    parflow_run.Solver.MaxRestarts = 2
    parflow_run.Solver.MaxConvergenceFailures = 3
    parflow_run.Geom.domain.Upper.X = shape[2] * 1000
    parflow_run.Geom.domain.Upper.Y = shape[1] * 1000
    parflow_run.Solver.CLM.MetFileName = "CW3E"
    parflow_run.Solver.CLM.MetFilePath = parflow_output_dir
    parflow_run.Geom.domain.FBz.FileName = "pf_flowbarrier.pfb"
    parflow_run.Geom.domain.ICPressure.FileName = "ss_pressure_head.pfb"
    parflow_run.Geom.indi_input.FileName = "pf_indicator.pfb"
    parflow_run.Mannings.FileName = "mannings.pfb"

    # Run parflow simulation
    parflow_run.run(parflow_output_dir)
    duration = round(time.time() - duration_start, 2)
    print(f"Parflow run duration = {duration} seconds.")

def get_forcing_shape(parflow_output_dir:str):
    """
    Get the forcing files shape if they already exists
    Parameters:
            parflow_output_dir:     Path to parflow input/output directory.
    """

    result = None
    path = f"{parflow_output_dir}/CW3E.APCP.000001_to_000024.pfb"
    if os.path.exists(path):
        data = pf.read_pfb(path)
        result = (10, data.shape[1], data.shape[2])
    return result

if __name__ == "__main__":
    main()
