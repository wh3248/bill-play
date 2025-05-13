"""
    Utility to get pyproj projection constants from a tiff file.
"""
import sys
import os
import pyproj
import rasterio

def main():
    tiff_file_path = sys.argv[1] if len(sys.argv) > 1 else None
    if tiff_file_path is None:
        print("Specify tiff path as argument.")
        return
    if not os.path.exists(tiff_file_path):
        print(f"File '{tiff_file_path}' does not exist.")
        return

    with rasterio.open(tiff_file_path) as dataset:
        crs = dataset.crs
        projection_constants = crs.to_dict()
        crs = pyproj.CRS.from_dict(projection_constants)
        proj_string = crs.to_proj4()
        to_latlon_transformer = pyproj.Transformer.from_crs(crs, pyproj.CRS.from_epsg(4326), always_xy=True)
        to_xy_transformer = pyproj.Transformer.from_crs(pyproj.CRS.from_epsg(4326), crs, always_xy=True)
        x = 0
        y = 0
        lon, lat = to_latlon_transformer.transform(x, y)
        print()
        print("PROJ4", proj_string)
        print()
        print(f"X,Y = ({x}, {y})")
        print(f"LAT,LON = ({lat}, {lon})")
        x, y = to_xy_transformer.transform(lon, lat)
        x = int(x)
        y = int(y)
        print(f"X,Y = ({x}, {y})")

main()
