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
    parflow_run = getChenParflowRun(shape, topology, parflow_output_dir, start_time, end_time)

    if False:
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

def getChenParflowRun(shape, topology, parflow_output_dir, start_time, end_time):
    CONCN = pf.Run("spinup", parflow_output_dir)

    days = (
        (datetime.datetime.strptime(end_time, "%Y-%m-%d")
        - datetime.datetime.strptime(start_time, "%Y-%m-%d")).days
    )


    CONCN.FileVersion = 4

    #-----------------------------------------------------------------------------
    # Set Processor topology
    #-----------------------------------------------------------------------------
    CONCN.Process.Topology.P = topology[0]
    CONCN.Process.Topology.Q = topology[1]
    CONCN.Process.Topology.R = topology[2]

    #-----------------------------------------------------------------------------
    # Timing (time units is set by units of permeability)
    #-----------------------------------------------------------------------------

    CONCN.TimingInfo.BaseUnit = 1.0
    CONCN.TimingInfo.StartCount = 0
    CONCN.TimingInfo.StartTime = 0
    CONCN.TimingInfo.StopTime = days * 24
    #CONCN.TimingInfo.StopTime = 500
    CONCN.TimingInfo.DumpInterval = 1
    #CONCN.TimingInfo.DumpInterval = 100
    CONCN.TimeStep.Type = 'Constant'
    CONCN.TimeStep.Value = 1

    #-----------------------------------------------------------------------------
    # Computational Grid
    #-----------------------------------------------------------------------------

    CONCN.ComputationalGrid.Lower.X = 0.0
    CONCN.ComputationalGrid.Lower.Y = 0.0
    CONCN.ComputationalGrid.Lower.Z = 0.0

    CONCN.ComputationalGrid.DX = 1000
    CONCN.ComputationalGrid.DY = 1000
    CONCN.ComputationalGrid.DZ = 200.0


    CONCN.ComputationalGrid.NX = shape[2]
    CONCN.ComputationalGrid.NY = shape[1]
    CONCN.ComputationalGrid.NZ = shape[0]


    #-----------------------------------------------------------------------------
    # Names of the GeomInputs
    #-----------------------------------------------------------------------------

    CONCN.GeomInput.Names = "domaininput indi_input"

    #-----------------------------------------------------------------------------
    # Domain Geometry Input
    #-----------------------------------------------------------------------------

    # CONCN.GeomInput.domaininput.InputType = 'SolidFile'
    # CONCN.GeomInput.domaininput.GeomNames = 'domain'
    #CONCN.GeomInput.domaininput.FileName = 'solidfile.pfsol'

    CONCN.GeomInput.domaininput.InputType = 'Box'
    CONCN.GeomInput.domaininput.GeomName = 'domain'

    CONCN.Geom.domain.Lower.X = 0.0
    CONCN.Geom.domain.Lower.Y = 0.0
    CONCN.Geom.domain.Lower.Z = 0.0
    #
    CONCN.Geom.domain.Upper.X = shape[2] * 1000
    CONCN.Geom.domain.Upper.Y = shape[1] * 1000
    CONCN.Geom.domain.Upper.Z = 2000.0
    CONCN.Geom.domain.Patches = 'x_lower x_upper y_lower y_upper z_lower z_upper'
    #-----------------------------------------------------------------------------
    # Domain Geometry
    #-----------------------------------------------------------------------------

    # CONCN.Geom.domain.Patches = "top bottom side"

    #-----------------------------------------------------------------------------
    # Indicator Geometry Input
    #-----------------------------------------------------------------------------

    CONCN.GeomInput.indi_input.InputType = 'IndicatorField'
    CONCN.GeomInput.indi_input.GeomNames = 's1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 g1 g2 g3 g4 g5 g6 g7 g8 b1 b2'
    CONCN.Geom.indi_input.FileName = 'pf_indicator.pfb'

    CONCN.GeomInput.s1.Value = 1
    CONCN.GeomInput.s2.Value = 2
    CONCN.GeomInput.s3.Value = 3
    CONCN.GeomInput.s4.Value = 4
    CONCN.GeomInput.s5.Value = 5
    CONCN.GeomInput.s6.Value = 6
    CONCN.GeomInput.s7.Value = 7
    CONCN.GeomInput.s8.Value = 8
    CONCN.GeomInput.s9.Value = 9
    CONCN.GeomInput.s10.Value = 10
    CONCN.GeomInput.s11.Value = 11
    CONCN.GeomInput.s12.Value = 12

    CONCN.GeomInput.s13.Value = 13

    CONCN.GeomInput.b1.Value = 19
    CONCN.GeomInput.b2.Value = 20

    CONCN.GeomInput.g1.Value = 21
    CONCN.GeomInput.g2.Value = 22
    CONCN.GeomInput.g3.Value = 23
    CONCN.GeomInput.g4.Value = 24
    CONCN.GeomInput.g5.Value = 25
    CONCN.GeomInput.g6.Value = 26
    CONCN.GeomInput.g7.Value = 27
    CONCN.GeomInput.g8.Value = 28

    #--------------------------------------------
    # variable dz assignments
    #------------------------------------------
    CONCN.Solver.Nonlinear.VariableDz = True
    CONCN.dzScale.GeomNames = 'domain'
    CONCN.dzScale.Type = 'nzList'
    CONCN.dzScale.nzListNumber = 10

    # 10 layers, starts at 0 for the bottom to 9 at the top
    # note this is opposite Noah/WRF
    # layers are 0.1 m, 0.3 m, 0.6 m, 1.0 m, 5.0 m, 10.0 m, 25.0 m, 50.0 m, 100.0m, 200.0 m
    # 200 m * 1.5 = 200 m
    CONCN.Cell._0.dzScale.Value = 1
    # 200 m * .5 = 100 m
    CONCN.Cell._1.dzScale.Value = 0.5
    # 200 m * .25 = 50 m
    CONCN.Cell._2.dzScale.Value = 0.25
    # 200 m * 0.125 = 25 m
    CONCN.Cell._3.dzScale.Value = 0.125
    # 200 m * 0.05 = 10 m
    CONCN.Cell._4.dzScale.Value = 0.05
    # 200 m * .025 = 5 m
    CONCN.Cell._5.dzScale.Value = 0.025
    # 200 m * .005 = 1 m
    CONCN.Cell._6.dzScale.Value = 0.005
    # 200 m * 0.003 = 0.6 m
    CONCN.Cell._7.dzScale.Value = 0.003
    # 200 m * 0.0015 = 0.3 m
    CONCN.Cell._8.dzScale.Value = 0.0015
    # 200 m * 0.0005 = 0.1 m = 10 cm which is default top Noah layer
    CONCN.Cell._9.dzScale.Value = 0.0005

    #------------------------------------------------------------------------------
    # Flow Barrier defined by Shangguan Depth to Bedrock
    #--------------------------------------------------------------

    CONCN.Solver.Nonlinear.FlowBarrierZ = True
    CONCN.FBz.Type = 'PFBFile'
    CONCN.Geom.domain.FBz.FileName = 'pf_flowbarrier.pfb'
    #CONCN.dist('pf_flowbarrier.pfb')

    #-----------------------------------------------------------------------------
    # Permeability (values in m/hr)
    #-----------------------------------------------------------------------------

    CONCN.Geom.Perm.Names = 'domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 g1 g2 g3 g4 g5 g6 g7 g8 b1 b2'

    CONCN.Geom.domain.Perm.Type = 'Constant'
    CONCN.Geom.domain.Perm.Value = 0.02

    CONCN.Geom.s1.Perm.Type = 'Constant'
    CONCN.Geom.s1.Perm.Value = 0.269022595

    CONCN.Geom.s2.Perm.Type = 'Constant'
    CONCN.Geom.s2.Perm.Value = 0.043630356

    CONCN.Geom.s3.Perm.Type = 'Constant'
    CONCN.Geom.s3.Perm.Value = 0.015841225

    CONCN.Geom.s4.Perm.Type = 'Constant'
    CONCN.Geom.s4.Perm.Value = 0.007582087

    CONCN.Geom.s5.Perm.Type = 'Constant'
    CONCN.Geom.s5.Perm.Value = 0.01818816

    CONCN.Geom.s6.Perm.Type = 'Constant'
    CONCN.Geom.s6.Perm.Value = 0.005009435

    CONCN.Geom.s7.Perm.Type = 'Constant'
    CONCN.Geom.s7.Perm.Value = 0.005492736

    CONCN.Geom.s8.Perm.Type = 'Constant'
    CONCN.Geom.s8.Perm.Value = 0.004675077

    CONCN.Geom.s9.Perm.Type = 'Constant'
    CONCN.Geom.s9.Perm.Value = 0.003386794

    CONCN.Geom.s10.Perm.Type = 'Constant'
    CONCN.Geom.s10.Perm.Value = 0.004783973

    CONCN.Geom.s11.Perm.Type = 'Constant'
    CONCN.Geom.s11.Perm.Value = 0.003979136

    CONCN.Geom.s12.Perm.Type = 'Constant'
    CONCN.Geom.s12.Perm.Value = 0.006162952

    CONCN.Geom.s13.Perm.Type = 'Constant'
    CONCN.Geom.s13.Perm.Value = 0.005009435

    CONCN.Geom.b1.Perm.Type = 'Constant'
    CONCN.Geom.b1.Perm.Value = 0.005

    CONCN.Geom.b2.Perm.Type = 'Constant'
    CONCN.Geom.b2.Perm.Value = 0.01

    CONCN.Geom.g1.Perm.Type = 'Constant'
    CONCN.Geom.g1.Perm.Value = 0.02

    CONCN.Geom.g2.Perm.Type = 'Constant'
    CONCN.Geom.g2.Perm.Value = 0.03

    CONCN.Geom.g3.Perm.Type = 'Constant'
    CONCN.Geom.g3.Perm.Value = 0.04

    CONCN.Geom.g4.Perm.Type = 'Constant'
    CONCN.Geom.g4.Perm.Value = 0.05

    CONCN.Geom.g5.Perm.Type = 'Constant'
    CONCN.Geom.g5.Perm.Value = 0.06

    CONCN.Geom.g6.Perm.Type = 'Constant'
    CONCN.Geom.g6.Perm.Value = 0.08

    CONCN.Geom.g7.Perm.Type = 'Constant'
    CONCN.Geom.g7.Perm.Value = 0.1

    CONCN.Geom.g8.Perm.Type = 'Constant'
    CONCN.Geom.g8.Perm.Value = 0.2

    CONCN.Perm.TensorType = 'TensorByGeom'
    CONCN.Geom.Perm.TensorByGeom.Names = 'domain b1 b2 g1 g2 g4 g5 g6 g7'

    CONCN.Geom.domain.Perm.TensorValX = 1.0
    CONCN.Geom.domain.Perm.TensorValY = 1.0
    CONCN.Geom.domain.Perm.TensorValZ = 1.0

    CONCN.Geom.b1.Perm.TensorValX = 1.0
    CONCN.Geom.b1.Perm.TensorValY = 1.0
    CONCN.Geom.b1.Perm.TensorValZ = 0.1

    CONCN.Geom.b2.Perm.TensorValX = 1.0
    CONCN.Geom.b2.Perm.TensorValY = 1.0
    CONCN.Geom.b2.Perm.TensorValZ = 0.1

    CONCN.Geom.g1.Perm.TensorValX = 1.0
    CONCN.Geom.g1.Perm.TensorValY = 1.0
    CONCN.Geom.g1.Perm.TensorValZ = 0.1

    CONCN.Geom.g2.Perm.TensorValX = 1.0
    CONCN.Geom.g2.Perm.TensorValY = 1.0
    CONCN.Geom.g2.Perm.TensorValZ = 0.1

    CONCN.Geom.g4.Perm.TensorValX = 1.0
    CONCN.Geom.g4.Perm.TensorValY = 1.0
    CONCN.Geom.g4.Perm.TensorValZ = 0.1

    CONCN.Geom.g5.Perm.TensorValX = 1.0
    CONCN.Geom.g5.Perm.TensorValY = 1.0
    CONCN.Geom.g5.Perm.TensorValZ = 0.1

    CONCN.Geom.g6.Perm.TensorValX = 1.0
    CONCN.Geom.g6.Perm.TensorValY = 1.0
    CONCN.Geom.g6.Perm.TensorValZ = 0.1

    CONCN.Geom.g7.Perm.TensorValX = 1.0
    CONCN.Geom.g7.Perm.TensorValY = 1.0
    CONCN.Geom.g7.Perm.TensorValZ = 0.1

    #-----------------------------------------------------------------------------
    # Specific Storage
    #-----------------------------------------------------------------------------

    CONCN.SpecificStorage.Type = 'Constant'
    CONCN.SpecificStorage.GeomNames = 'domain'
    CONCN.Geom.domain.SpecificStorage.Value = 1.0e-4

    #-----------------------------------------------------------------------------
    # Phases
    #-----------------------------------------------------------------------------

    CONCN.Phase.Names = 'water'
    CONCN.Phase.water.Density.Type = 'Constant'
    CONCN.Phase.water.Density.Value = 1.0
    CONCN.Phase.water.Viscosity.Type = 'Constant'
    CONCN.Phase.water.Viscosity.Value = 1.0

    #-----------------------------------------------------------------------------
    # Contaminants
    #-----------------------------------------------------------------------------

    CONCN.Contaminants.Names = ''

    #-----------------------------------------------------------------------------
    # Gravity
    #-----------------------------------------------------------------------------

    CONCN.Gravity = 1.0

    #-----------------------------------------------------------------------------
    # Porosity
    #-----------------------------------------------------------------------------

    CONCN.Geom.Porosity.GeomNames = 'domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 g1 g2 g3 g4 g5 g6 g7 g8 b1 b2'

    CONCN.Geom.domain.Porosity.Type = 'Constant'
    CONCN.Geom.domain.Porosity.Value = 0.33

    CONCN.Geom.s1.Porosity.Type = 'Constant'
    CONCN.Geom.s1.Porosity.Value = 0.375

    CONCN.Geom.s2.Porosity.Type = 'Constant'
    CONCN.Geom.s2.Porosity.Value = 0.39

    CONCN.Geom.s3.Porosity.Type = 'Constant'
    CONCN.Geom.s3.Porosity.Value = 0.387

    CONCN.Geom.s4.Porosity.Type = 'Constant'
    CONCN.Geom.s4.Porosity.Value = 0.439

    CONCN.Geom.s5.Porosity.Type = 'Constant'
    CONCN.Geom.s5.Porosity.Value = 0.489

    CONCN.Geom.s6.Porosity.Type = 'Constant'
    CONCN.Geom.s6.Porosity.Value = 0.399

    CONCN.Geom.s7.Porosity.Type = 'Constant'
    CONCN.Geom.s7.Porosity.Value = 0.384

    CONCN.Geom.s8.Porosity.Type = 'Constant'
    CONCN.Geom.s8.Porosity.Value = 0.482

    CONCN.Geom.s9.Porosity.Type = 'Constant'
    CONCN.Geom.s9.Porosity.Value = 0.442

    CONCN.Geom.s10.Porosity.Type = 'Constant'
    CONCN.Geom.s10.Porosity.Value = 0.385

    CONCN.Geom.s11.Porosity.Type = 'Constant'
    CONCN.Geom.s11.Porosity.Value = 0.481

    CONCN.Geom.s12.Porosity.Type = 'Constant'
    CONCN.Geom.s12.Porosity.Value = 0.459

    CONCN.Geom.s13.Porosity.Type = 'Constant'
    CONCN.Geom.s13.Porosity.Value = 0.399

    CONCN.Geom.b1.Porosity.Type = 'Constant'
    CONCN.Geom.b1.Porosity.Value = 0.1

    CONCN.Geom.b2.Porosity.Type = 'Constant'
    CONCN.Geom.b2.Porosity.Value = 0.05

    CONCN.Geom.g1.Porosity.Type = 'Constant'
    CONCN.Geom.g1.Porosity.Value = 0.12

    CONCN.Geom.g2.Porosity.Type = 'Constant'
    CONCN.Geom.g2.Porosity.Value = 0.3

    CONCN.Geom.g3.Porosity.Type = 'Constant'
    CONCN.Geom.g3.Porosity.Value = 0.01

    CONCN.Geom.g4.Porosity.Type = 'Constant'
    CONCN.Geom.g4.Porosity.Value = 0.15

    CONCN.Geom.g5.Porosity.Type = 'Constant'
    CONCN.Geom.g5.Porosity.Value = 0.22

    CONCN.Geom.g6.Porosity.Type = 'Constant'
    CONCN.Geom.g6.Porosity.Value = 0.27

    CONCN.Geom.g7.Porosity.Type = 'Constant'
    CONCN.Geom.g7.Porosity.Value = 0.06

    CONCN.Geom.g8.Porosity.Type = 'Constant'
    CONCN.Geom.g8.Porosity.Value = 0.3

    #-----------------------------------------------------------------------------
    # Domain
    #-----------------------------------------------------------------------------

    CONCN.Domain.GeomName = 'domain'

    #----------------------------------------------------------------------------
    # Mobility
    #----------------------------------------------------------------------------

    CONCN.Phase.water.Mobility.Type = 'Constant'
    CONCN.Phase.water.Mobility.Value = 1.0

    #-----------------------------------------------------------------------------
    # Wells
    #-----------------------------------------------------------------------------

    CONCN.Wells.Names = ''

    #-----------------------------------------------------------------------------
    # Relative Permeability
    #-----------------------------------------------------------------------------

    CONCN.Phase.RelPerm.Type = 'VanGenuchten'
    CONCN.Phase.RelPerm.GeomNames = 'domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13'

    CONCN.Geom.domain.RelPerm.Alpha = 0.5
    CONCN.Geom.domain.RelPerm.N = 2.5
    CONCN.Geom.domain.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.domain.RelPerm.MinPressureHead = -500
    CONCN.Geom.domain.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s1.RelPerm.Alpha = 3.548
    CONCN.Geom.s1.RelPerm.N = 4.162
    CONCN.Geom.s1.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s1.RelPerm.MinPressureHead = -300
    CONCN.Geom.s1.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s2.RelPerm.Alpha = 3.467
    CONCN.Geom.s2.RelPerm.N = 2.738
    CONCN.Geom.s2.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s2.RelPerm.MinPressureHead = -300
    CONCN.Geom.s2.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s3.RelPerm.Alpha = 2.692
    CONCN.Geom.s3.RelPerm.N = 2.445
    CONCN.Geom.s3.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s3.RelPerm.MinPressureHead = -300
    CONCN.Geom.s3.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s4.RelPerm.Alpha = 0.501
    CONCN.Geom.s4.RelPerm.N = 2.659
    CONCN.Geom.s4.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s4.RelPerm.MinPressureHead = -300
    CONCN.Geom.s4.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s5.RelPerm.Alpha = 0.661
    CONCN.Geom.s5.RelPerm.N = 2.659
    CONCN.Geom.s5.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s5.RelPerm.MinPressureHead = -300
    CONCN.Geom.s5.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s6.RelPerm.Alpha = 1.122
    CONCN.Geom.s6.RelPerm.N = 2.479
    CONCN.Geom.s6.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s6.RelPerm.MinPressureHead = -300
    CONCN.Geom.s6.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s7.RelPerm.Alpha = 2.089
    CONCN.Geom.s7.RelPerm.N = 2.318
    CONCN.Geom.s7.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s7.RelPerm.MinPressureHead = -300
    CONCN.Geom.s7.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s8.RelPerm.Alpha = 0.832
    CONCN.Geom.s8.RelPerm.N = 2.514
    CONCN.Geom.s8.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s8.RelPerm.MinPressureHead = -300
    CONCN.Geom.s8.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s9.RelPerm.Alpha = 1.585
    CONCN.Geom.s9.RelPerm.N = 2.413
    CONCN.Geom.s9.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s9.RelPerm.MinPressureHead = -300
    CONCN.Geom.s9.RelPerm.InterpolationMethod = 'Linear'


    CONCN.Geom.s10.RelPerm.Alpha = 3.311
    CONCN.Geom.s10.RelPerm.N = 2.202
    CONCN.Geom.s10.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s10.RelPerm.MinPressureHead = -300
    CONCN.Geom.s10.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s11.RelPerm.Alpha = 1.622
    CONCN.Geom.s11.RelPerm.N = 2.318
    CONCN.Geom.s11.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s11.RelPerm.MinPressureHead = -300
    CONCN.Geom.s11.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s12.RelPerm.Alpha = 1.514
    CONCN.Geom.s12.RelPerm.N = 2.259
    CONCN.Geom.s12.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s12.RelPerm.MinPressureHead = -300
    CONCN.Geom.s12.RelPerm.InterpolationMethod = 'Linear'

    CONCN.Geom.s13.RelPerm.Alpha = 1.122
    CONCN.Geom.s13.RelPerm.N = 2.479
    CONCN.Geom.s13.RelPerm.NumSamplePoints = 20000
    CONCN.Geom.s13.RelPerm.MinPressureHead = -300
    CONCN.Geom.s13.RelPerm.InterpolationMethod = 'Linear'

    #-----------------------------------------------------------------------------
    # Saturation
    #-----------------------------------------------------------------------------

    CONCN.Phase.Saturation.Type = 'VanGenuchten'
    CONCN.Phase.Saturation.GeomNames = 'domain s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13'

    CONCN.Geom.domain.Saturation.Alpha = 0.5
    CONCN.Geom.domain.Saturation.N = 2.5
    CONCN.Geom.domain.Saturation.SRes = 0.00001
    CONCN.Geom.domain.Saturation.SSat = 1.0

    CONCN.Geom.s1.Saturation.Alpha = 3.548
    CONCN.Geom.s1.Saturation.N = 4.162
    CONCN.Geom.s1.Saturation.SRes = 0.0001
    CONCN.Geom.s1.Saturation.SSat = 1.0

    CONCN.Geom.s2.Saturation.Alpha = 3.467
    CONCN.Geom.s2.Saturation.N = 2.738
    CONCN.Geom.s2.Saturation.SRes = 0.0001
    CONCN.Geom.s2.Saturation.SSat = 1.0

    CONCN.Geom.s3.Saturation.Alpha = 2.692
    CONCN.Geom.s3.Saturation.N = 2.445
    CONCN.Geom.s3.Saturation.SRes = 0.0001
    CONCN.Geom.s3.Saturation.SSat = 1.0

    CONCN.Geom.s4.Saturation.Alpha = 0.501
    CONCN.Geom.s4.Saturation.N = 2.659
    CONCN.Geom.s4.Saturation.SRes = 0.0001
    CONCN.Geom.s4.Saturation.SSat = 1.0

    CONCN.Geom.s5.Saturation.Alpha = 0.661
    CONCN.Geom.s5.Saturation.N = 2.659
    CONCN.Geom.s5.Saturation.SRes = 0.0001
    CONCN.Geom.s5.Saturation.SSat = 1.0

    CONCN.Geom.s6.Saturation.Alpha = 1.122
    CONCN.Geom.s6.Saturation.N = 2.479
    CONCN.Geom.s6.Saturation.SRes = 0.0001
    CONCN.Geom.s6.Saturation.SSat = 1.0

    CONCN.Geom.s7.Saturation.Alpha = 2.089
    CONCN.Geom.s7.Saturation.N = 2.318
    CONCN.Geom.s7.Saturation.SRes = 0.0001
    CONCN.Geom.s7.Saturation.SSat = 1.0

    CONCN.Geom.s8.Saturation.Alpha = 0.832
    CONCN.Geom.s8.Saturation.N = 2.514
    CONCN.Geom.s8.Saturation.SRes = 0.0001
    CONCN.Geom.s8.Saturation.SSat = 1.0

    CONCN.Geom.s9.Saturation.Alpha = 1.585
    CONCN.Geom.s9.Saturation.N = 2.413
    CONCN.Geom.s9.Saturation.SRes = 0.0001
    CONCN.Geom.s9.Saturation.SSat = 1.0

    CONCN.Geom.s10.Saturation.Alpha = 3.311
    CONCN.Geom.s10.Saturation.N = 2.202
    CONCN.Geom.s10.Saturation.SRes = 0.0001
    CONCN.Geom.s10.Saturation.SSat = 1.0

    CONCN.Geom.s11.Saturation.Alpha = 1.622
    CONCN.Geom.s11.Saturation.N = 2.318
    CONCN.Geom.s11.Saturation.SRes = 0.0001
    CONCN.Geom.s11.Saturation.SSat = 1.0

    CONCN.Geom.s12.Saturation.Alpha = 1.514
    CONCN.Geom.s12.Saturation.N = 2.259
    CONCN.Geom.s12.Saturation.SRes = 0.0001
    CONCN.Geom.s12.Saturation.SSat = 1.0

    CONCN.Geom.s13.Saturation.Alpha = 1.122
    CONCN.Geom.s13.Saturation.N = 2.479
    CONCN.Geom.s13.Saturation.SRes = 0.0001
    CONCN.Geom.s13.Saturation.SSat = 1.0

    #-----------------------------------------------------------------------------
    # Time Cycles
    #-----------------------------------------------------------------------------

    CONCN.Cycle.Names = 'constant rainrec'
    CONCN.Cycle.constant.Names = 'alltime'
    CONCN.Cycle.constant.alltime.Length = 1
    CONCN.Cycle.constant.Repeat = -1

    CONCN.Cycle.rainrec.Names = 'rain rec'
    CONCN.Cycle.rainrec.rain.Length = 10
    CONCN.Cycle.rainrec.rec.Length = 150
    CONCN.Cycle.rainrec.Repeat = -1

    #-----------------------------------------------------------------------------
    # Boundary Conditions
    #-----------------------------------------------------------------------------

    CONCN.BCPressure.PatchNames = CONCN.Geom.domain.Patches

    # # CONCN.Patch.ocean.BCPressure.Type = 'DirEquilRefPatch'
    # CONCN.Patch.ocean.BCPressure.Type = 'FluxConst'
    # CONCN.Patch.ocean.BCPressure.Cycle = 'constant'
    # CONCN.Patch.ocean.BCPressure.RefGeom = 'domain'
    # CONCN.Patch.ocean.BCPressure.RefPatch = 'top'
    # CONCN.Patch.ocean.BCPressure.alltime.Value = 0.0

    # # CONCN.Patch.sink.BCPressure.Type = 'OverlandDiffusive'
    # CONCN.Patch.sink.BCPressure.Type = 'OverlandKinematic'
    # # CONCN.Patch.sink.BCPressure.Type = 'SeepageFace'
    # CONCN.Patch.sink.BCPressure.Cycle = 'constant'
    # CONCN.Patch.sink.BCPressure.RefGeom = 'domain'
    # CONCN.Patch.sink.BCPressure.RefPatch = 'top'
    # CONCN.Patch.sink.BCPressure.alltime.Value = 0.0

    # # CONCN.Patch.lake.BCPressure.Type = 'OverlandDiffusive'
    # CONCN.Patch.lake.BCPressure.Type = 'OverlandKinematic'
    # # CONCN.Patch.lake.BCPressure.Type = 'SeepageFace'
    # CONCN.Patch.lake.BCPressure.Cycle = 'constant'
    # CONCN.Patch.lake.BCPressure.RefGeom = 'domain'
    # CONCN.Patch.lake.BCPressure.RefPatch = 'top'
    # CONCN.Patch.lake.BCPressure.alltime.Value = 0.0

    # CONCN.Patch.land.BCPressure.Type = 'FluxConst'
    # CONCN.Patch.land.BCPressure.Cycle = 'constant'
    # CONCN.Patch.land.BCPressure.alltime.Value = 0.0

    # CONCN.Patch.bottom.BCPressure.Type = 'FluxConst'
    # CONCN.Patch.bottom.BCPressure.Cycle = 'constant'
    # CONCN.Patch.bottom.BCPressure.alltime.Value = 0.0

    # CONCN.Solver.OverlandKinematic.SeepageOne = 4  ## new key
    # CONCN.Solver.OverlandKinematic.SeepageTwo = 5 ## new key

    # CONCN.Patch.top.BCPressure.Type = 'OverlandDiffusive'
    # CONCN.Patch.top.BCPressure.Type = 'OverlandKinematic'
    # # CONCN.Patch.top.BCPressure.Type = 'SeepageFace'
    # CONCN.Patch.top.BCPressure.Cycle = 'constant'
    # CONCN.Patch.top.BCPressure.alltime.Value = 0
    # # CONCN.Patch.top.BCPressure.Cycle = 'rainrec'
    # # CONCN.Patch.top.BCPressure.rain.Value = -0.000001
    # # CONCN.Patch.top.BCPressure.rec.Value = 0.0

    # CONCN.Patch.side.BCPressure.Type = 'FluxConst'
    # CONCN.Patch.side.BCPressure.Cycle = 'constant'
    # CONCN.Patch.side.BCPressure.alltime.Value = 0.0

    # CONCN.Patch.bottom.BCPressure.Type = 'FluxConst'
    # CONCN.Patch.bottom.BCPressure.Cycle = 'constant'
    # CONCN.Patch.bottom.BCPressure.alltime.Value = 0.0

    # CONCN.Patch.top.BCPressure.Type = 'OverlandKinematic'
    # CONCN.Patch.top.BCPressure.Cycle = 'constant'
    # CONCN.Patch.top.BCPressure.alltime.Value = 0.0

    CONCN.Patch.z_upper.BCPressure.Type = 'OverlandKinematic'
    CONCN.Patch.z_upper.BCPressure.Cycle = 'constant'
    CONCN.Patch.z_upper.BCPressure.alltime.Value = 0.0

    CONCN.Patch.z_lower.BCPressure.Type = 'FluxConst'
    CONCN.Patch.z_lower.BCPressure.Cycle = 'constant'
    CONCN.Patch.z_lower.BCPressure.alltime.Value = 0.0

    CONCN.Patch.x_lower.BCPressure.Type = 'FluxConst'
    CONCN.Patch.x_lower.BCPressure.Cycle = 'constant'
    CONCN.Patch.x_lower.BCPressure.alltime.Value = 0.0

    CONCN.Patch.x_upper.BCPressure.Type = 'FluxConst'
    CONCN.Patch.x_upper.BCPressure.Cycle = 'constant'
    CONCN.Patch.x_upper.BCPressure.alltime.Value = 0.0

    CONCN.Patch.y_lower.BCPressure.Type = 'FluxConst'
    CONCN.Patch.y_lower.BCPressure.Cycle = 'constant'
    CONCN.Patch.y_lower.BCPressure.alltime.Value = 0.0

    CONCN.Patch.y_upper.BCPressure.Type = 'FluxConst'
    CONCN.Patch.y_upper.BCPressure.Cycle = 'constant'
    CONCN.Patch.y_upper.BCPressure.alltime.Value = 0.0

    CONCN.Solver.EvapTransFile = True
    CONCN.Solver.EvapTrans.FileName = 'pme.pfb'
    #CONCN.dist('pme.pfb')

    #-----------------------------------------------------------------------------
    # Topo slopes in x-direction
    #-----------------------------------------------------------------------------

    CONCN.TopoSlopesX.Type = 'PFBFile'
    CONCN.TopoSlopesX.GeomNames = 'domain'
    CONCN.TopoSlopesX.FileName = 'slope_x.pfb'

    #-----------------------------------------------------------------------------
    # Topo slopes in y-direction
    #-----------------------------------------------------------------------------

    CONCN.TopoSlopesY.Type = 'PFBFile'
    CONCN.TopoSlopesY.GeomNames = 'domain'
    CONCN.TopoSlopesY.FileName = 'slope_y.pfb'

    #-----------------------------------------------------------------------------
    # Initial conditions: water pressure
    #-----------------------------------------------------------------------------

    # CONCN.ICPressure.Type = 'PFBFile'
    # CONCN.ICPressure.GeomNames = 'domain'
    # CONCN.Geom.domain.ICPressure.FileName = ip
    # CONCN.dist(ip)

    # CONCN.ICPressure.Type = 'HydroStaticPatch'
    # CONCN.Geom.domain.ICPressure.RefPatch = 'z_upper'
    # CONCN.Geom.domain.ICPressure.RefGeom = 'domain'
    # CONCN.Geom.domain.ICPressure.Value = 372.

    CONCN.ICPressure.Type                                   = 'HydroStaticPatch'
    CONCN.ICPressure.GeomNames                              = 'domain'
    CONCN.Geom.domain.ICPressure.Value                      = -2.
    CONCN.Geom.domain.ICPressure.RefGeom                    = 'domain'
    CONCN.Geom.domain.ICPressure.RefPatch                   = 'z_upper'

    #-----------------------------------------------------------------------------
    # Distribute inputs
    #-----------------------------------------------------------------------------

    ##### TODO CONCN.dist('../inputs/OR_subsur.pfb')
    #CONCN.dist(ip)

    #-----------------------------------------------------------------------------
    # Phase sources:
    #-----------------------------------------------------------------------------

    CONCN.PhaseSources.water.Type = 'Constant'
    CONCN.PhaseSources.water.GeomNames = 'domain'
    CONCN.PhaseSources.water.Geom.domain.Value = 0.0

    #-----------------------------------------------------------------------------
    # Mannings coefficient
    #-----------------------------------------------------------------------------

    # TODO WE HAVE A MANNINGS FILE, we should use it

    CONCN.Mannings.Type = 'PFBFile'
    CONCN.Mannings.GeomNames = 'domain'
    CONCN.Mannings.FileName = 'mannings.pfb'
    # CONCN.dist('CONCN.0.Final1km_mannings_rv50_original_values.pfb')

    # CONCN.Mannings.Type = 'PFBFile'
    # CONCN.Mannings.GeomNames = 'domain'
    # # CONCN.Mannings.Geom.domain.Value = 1.0e-5
    # CONCN.Mannings.FileName = 'OR_man.pfb'
    # CONCN.dist('OR_man.pfb')

    #CONCN.Mannings.Type = 'Constant'
    #CONCN.Mannings.GeomNames = 'domain'
    CONCN.Mannings.Geom.domain.Value = 1.0e-5
    # CONCN.Mannings.FileName = 'OR_man.pfb'
    # CONCN.dist('OR_man.pfb')

    #-----------------------------------------------------------------------------
    # Exact solution specification for error calculations
    #-----------------------------------------------------------------------------

    CONCN.KnownSolution = 'NoKnownSolution'

    #-----------------------------------------------------------------------------
    # Set solver parameters
    #-----------------------------------------------------------------------------

    CONCN.Solver = 'Richards'
    CONCN.Solver.TerrainFollowingGrid = True
    CONCN.Solver.TerrainFollowingGrid.SlopeUpwindFormulation = 'Upwind'

    CONCN.Solver.MaxIter = 250000
    #CONCN.Solver.Drop = 1E-30
    CONCN.Solver.AbsTol = 1E-10
    CONCN.Solver.MaxConvergenceFailures = 5
    CONCN.Solver.Nonlinear.MaxIter = 250
    CONCN.Solver.Nonlinear.ResidualTol = 1e-5
    # CONCN.Solver.OverlandDiffusive.Epsilon = 0.1

    # CONCN.Solver.PrintTop = True
    ## new solver settings for Terrain Following Grid
    CONCN.Solver.Nonlinear.EtaChoice = 'EtaConstant'
    CONCN.Solver.Nonlinear.EtaValue = 0.01
    CONCN.Solver.Nonlinear.UseJacobian = False
    CONCN.Solver.Nonlinear.DerivativeEpsilon = 1e-16
    CONCN.Solver.Nonlinear.StepTol = 1e-15
    CONCN.Solver.Nonlinear.Globalization = 'LineSearch'
    CONCN.Solver.Linear.KrylovDimension = 500
    CONCN.Solver.Linear.MaxRestarts = 8

    CONCN.Solver.Linear.Preconditioner = 'MGSemi'
    # CONCN.Solver.Linear.Preconditioner = 'PFMG'
    # CONCN.Solver.Linear.Preconditioner.PCMatrixType = 'PFSymmetric'
    # CONCN.Solver.Linear.Preconditioner.PFMG.NumPreRelax = 3
    # CONCN.Solver.Linear.Preconditioner.PFMG.NumPostRelax = 2

    CONCN.Solver.PrintMask = True
    CONCN.Solver.PrintVelocities = False
    CONCN.Solver.PrintSaturation = True
    CONCN.Solver.PrintPressure = True
    #Writing output (no binary except Pressure, all silo):
    CONCN.Solver.PrintSubsurfData = True
    #pfset Solver.PrintLSMSink                        True
    CONCN.Solver.WriteCLMBinary = False
    #CONCN.Solver.PrintCLM = True

    CONCN.Solver.WriteSiloSpecificStorage = False
    CONCN.Solver.WriteSiloMannings = False
    CONCN.Solver.WriteSiloMask = False
    CONCN.Solver.WriteSiloSlopes = False
    CONCN.Solver.WriteSiloSubsurfData = False
    CONCN.Solver.WriteSiloPressure = False
    CONCN.Solver.WriteSiloSaturation = False
    CONCN.Solver.WriteSiloEvapTrans = False
    CONCN.Solver.WriteSiloEvapTransSum = False
    CONCN.Solver.WriteSiloOverlandSum = False
    CONCN.Solver.WriteSiloCLM = False

    # # surface pressure test, new solver settings
    # CONCN.Solver.ResetSurfacePressure = True
    # CONCN.Solver.ResetSurfacePressure.ThresholdPressure = 10.
    # CONCN.Solver.ResetSurfacePressure.ResetPressure  =  -0.00001

    # CONCN.Solver.SurfacePredictor = True
    # CONCN.Solver.SurfacePredictor.PrintValues = True
    # CONCN.Solver.SurfacePredictor.PressureValue = 0.00001

    CONCN.Solver.CLM.MetFileName = "CW3E"
    CONCN.Solver.CLM.MetFilePath = parflow_output_dir
    #CONCN.Geom.domain.FBz.FileName = "pf_flowbarrier.pfb"
    #CONCN.Geom.domain.ICPressure.FileName = "ss_pressure_head.pfb"

    return CONCN
if __name__ == "__main__":
    main()
