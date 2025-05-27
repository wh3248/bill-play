import hf_hydrodata as hf
import subsettools as st

#-----------------------------------------------------------------------------
# Datasets to Pull
#-----------------------------------------------------------------------------
hf.register_api_pin('bhasling@gmail.com', '0000')
runname = 'bayou' 
start = '1980-10-01'
start = '2020-10-01'
end = '2022-10-01'
grid = "conus2"
var_ds = 'conus2_domain'
forcing_ds = 'CW3E'

#-----------------------------------------------------------------------------
# HUC or Lat / Lon Box
#-----------------------------------------------------------------------------
lat_max = 37.20
lat_min = 37.05
lon_max = -88.74
lon_min = -88.89
llb = [[lat_min, lon_min],
       [lat_max, lon_max]]
ij_bounds, mask = st.define_latlon_domain(latlon_bounds=llb, grid='conus2')
nj = ij_bounds[3] - ij_bounds[1]
ni = ij_bounds[2] - ij_bounds[0]

#-----------------------------------------------------------------------------
# Directories
#-----------------------------------------------------------------------------
forcing_dir = 'tmp/'

#-----------------------------------------------------------------------------
# Download
#-----------------------------------------------------------------------------
options = {
          'dataset': 'CW3E',
          'temporal_resolution': 'hourly',
          'start_time': start,
          'end_time': end,
          'grid_bounds': ij_bounds,
          'grid': 'conus2',
          }
variables = hf.get_variables(options)
print(variables)
ft = forcing_dir + '{wy}/{dataset}.{dataset_var}.{hour_start:06d}_to_{hour_end:06d}.pfb'
ft = forcing_dir + 'forcing_files.{wy}.nc'
print(ft)
print(variables)
hf.get_gridded_files(options=options, variables=variables, filename_template=ft, verbose=True)