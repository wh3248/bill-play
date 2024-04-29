"""
Run parflow for a transient run using PFB files collected by this script.
"""
import os
import pathlib
import parflow as pf
import numpy as np
import hf_hydrodata as hf

def main():
    """Collect PFB input files and run parflow with a transient run template."""

    parflow_output_dir = os.path.abspath("test_output")
    os.makedirs(parflow_output_dir, exist_ok=True)

    parflow_run = pf.Run.from_definition(pathlib.Path("transient.yaml"))

    huc_ids= ["1019000404"]
    start_time = "2005-01-01"
    end_time = "2005-01-03"

    print("Collect static inputs...")
    (nz, ny, nx) = collect_static_inputs(huc_ids, parflow_output_dir)

    print("Collect forcing files...")
    collect_forcing(huc_ids, parflow_output_dir, start_time, end_time)

    print(f"Run parflow on grid {nz}, {ny}, {nx}")
    parflow_run.ComputationalGrid.NX = nx
    parflow_run.ComputationalGrid.NY = ny
    parflow_run.ComputationalGrid.NZ = nz
    parflow_run.Process.Topology.P = 1
    parflow_run.Process.Topology.Q = 1
    parflow_run.Process.Topology.R = 1
    parflow_run.TimingInfo.StopTime = 48.0
    parflow_run.TimingInfo.DumpInterval = 24.0
    parflow_run.Solver.MaxConvergenceFailures = 5
    parflow_run.Solver.BinaryOutDir= None
    parflow_run.Solver.CLM.MetFileName = "CW3E"

    # Run parflow simulation
    parflow_run.run(parflow_output_dir)

def collect_static_inputs(huc_ids, parflow_output_dir):
    """Collect static input pfb input files from hf_hydrodata and subset to the huc_id list."""

    huc_id = ",".join(huc_ids)
    # Create a rename map to rename files that do not have the same name as the variable
    rename_map = {"ss_pressure_head": "press_init",
                  "pf_flowbarrier": "depth_to_bedrock"}

    for variable in ["slope_x", "slope_y", "pf_indicator", "ss_pressure_head", "pme", "mannings", "pf_flowbarrier"]:
        filter_options = dict(dataset="conus2_domain", variable=variable, huc_id=huc_id)
        data = hf.get_gridded_data(filter_options)
        parflow_variable_name = rename_map.get(variable) if rename_map.get(variable) else variable
        if len(data.shape) == 2:
            # PFB files require shape with 3 dimensions
            data = np.reshape(data, (1, data.shape[0], data.shape[1]))

        pf.write_pfb(f"{parflow_output_dir}/{parflow_variable_name}.pfb", data, dist=True)
        result = data.shape
    return result

def collect_forcing(huc_ids, parflow_output_dir, start_time, end_time):
    """Collect forcing files from hf_hydrodata into parflow_output_dir directory."""

    huc_id = ",".join(huc_ids)
    dataset = "CW3E"
    variables = ["precipitation", "downward_shortwave", "downward_longwave", "air_temp"]
    filter_options = dict(dataset=dataset, huc_id=huc_id, start_time=start_time, end_time=end_time, temporal_resolution="hourly")
    output_template = "{dataset}.{dataset_var}.{hour_start:06d}_to_{hour_end:06d}.pfb"
    output_template = f"test_output/{output_template}"
    hf.get_gridded_files(filter_options, variables=variables, filename_template=output_template)

    # Create P,Q,R dist files for the downloaded forcing files
    for file_name in os.listdir(parflow_output_dir):
        if file_name.startswith(dataset) and file_name.endswith(".pfb"):
            data = pf.read_pfb(f"{parflow_output_dir}/{file_name}")
            pf.write_pfb(f"{parflow_output_dir}/{file_name}", data, dist=True)
if __name__ == "__main__":
    main()
