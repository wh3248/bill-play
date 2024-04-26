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
    (nz, ny, nx) = collect_static_inputs(huc_ids, parflow_output_dir)
    parflow_run.ComputationalGrid.NX = nx
    parflow_run.ComputationalGrid.NY = ny
    parflow_run.ComputationalGrid.NZ = nz
    parflow_run.Process.Topology.P = 1
    parflow_run.Process.Topology.Q = 1
    parflow_run.Process.Topology.R = 1
    parflow_run.TimingInfo.StopTime = 10
    print(nz, ny, nx)
    parflow_run.run(parflow_output_dir)

def collect_static_inputs(huc_ids, parflow_output_dir):
    """Collect static input pfb input files from hf_hydrodata and subset to the huc_id list."""

    huc_id = ",".join(huc_ids)
    variable_name_map = {"ss_pressure_head": "press_init"}

    for variable in ["slope_x", "slope_y", "pf_indicator", "ss_pressure_head", "pme"]:
        filter_options = dict(dataset="conus1_domain", variable=variable, huc_id=huc_id)
        data = hf.get_gridded_data(filter_options)
        parflow_variable_name = variable_name_map.get(variable) if variable_name_map.get(variable) else variable
        if len(data.shape) == 2:
            data = np.reshape(data, (1, data.shape[0], data.shape[1]))
        print(data.shape, parflow_variable_name)

        pf.write_pfb(f"{parflow_output_dir}/{parflow_variable_name}.pfb", data, dist=False)
        result = data.shape
    return result

if __name__ == "__main__":
    main()
