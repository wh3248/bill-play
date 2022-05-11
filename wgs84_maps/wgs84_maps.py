"""
Mapping from WGS84 lat/lon coordindates to Conus1/Conus2 coordindates using Geodesic mapping.

You must call the method to load the grid->WGS84 map files before calling the method to map points.
Call the load_maps method with the parameter either 'conus1' or 'conus2' then call either
map_to_wgs84() or map_to_grid(). For example,

    mapping = WGS84Mapping()
    mapping.load_maps('conus1')
    (x, y) = mapping.map_to_grid(-112.07, 40.62)
    Will return x = 538, y = 904.
"""

import parflow as pf
import json
import numpy as np
import time
import math

class WGS84Mapping:
    """Methods to convert lat/lon to Conus1/Conus2 grid coordindates"""

    def __init__(self):
        """Constructor"""

        self.lat_map = None
        self.lon_map = None
        self.grid_bounds = None
        self.wgs84_bounds = None

    def map_to_wgs84(self, x, y):
        """Map an x,y conus grid point to lat long. Return [lon, lat]"""

        lat = self.lat_map[y, x]
        lon = self.lon_map[y, x]
        return [lon, lat]

    def map_to_grid(self, lon_point, lat_point):
        """Map a lat/lon point and return a conus grid point (x,y)"""

        nx = self.lat_map.shape[1]
        ny = self.lat_map.shape[0]
        row_indices = np.tile(np.matrix(np.linspace(0,ny-1,ny)).T, (1, nx))
        col_indices = np.tile(np.matrix(np.linspace(0,nx-1,nx)), (ny, 1))

        performance_option = True
        if performance_option:
            # subset the maps and indices to improve performance of closest
            buffer_degrees = 2
            conus_shape = self.lat_map.shape
            mask_subset = np.ones(conus_shape)
            mask_subset[self.lat_map < lat_point - buffer_degrees] = 0
            mask_subset[self.lat_map > lat_point + buffer_degrees] = 0
            mask_subset[self.lon_map < lon_point - buffer_degrees] = 0
            mask_subset[self.lon_map > lon_point + buffer_degrees] = 0

            subset_lat_map = self.lat_map[mask_subset>0]
            subset_lon_map = self.lon_map[mask_subset>0]
            subset_row_indices = np.squeeze(np.array(row_indices[mask_subset>0]))
            subset_col_indices = np.squeeze(np.array(col_indices[mask_subset>0]))
        else:
            # Do not use performance option, use full maps in call to closest
            subset_lat_map = self.lat_map
            subset_lon_map = self.lon_map
            subset_row_indices = np.squeeze(np.array(row_indices))
            subset_col_indices = np.squeeze(np.array(col_indices))

        result = self.closest(lat_point, lon_point, subset_lat_map, subset_lon_map, subset_row_indices, subset_col_indices)
        return result

    def load_maps(self, conus="conus1"):
        """Load the conus1 or conus2 lat/lon map files"""

        if conus.lower() == "conus1":
            lat_map_path = "/home/HYDROAPP/common/shapefiles/CONUS1/Latitude_CONUS1.pfb"
            lon_map_path = "/home/HYDROAPP/common/shapefiles/CONUS1/Longitude_CONUS1.pfb"
        else:
            lat_map_path = "/home/HYDROAPP/common/shapefiles/CONUS2/Latitude_CONUS2.pfb"
            lon_map_path = "/home/HYDROAPP/common/shapefiles/CONUS2/Longitude_CONUS2.pfb"
        self.lat_map = pf.read_pfb(lat_map_path)
        self.lon_map = pf.read_pfb(lon_map_path)
        self.lat_map = np.squeeze(self.lat_map)
        self.lon_map = np.squeeze(self.lon_map)


    def distance(self, lat1, lon1, lat2, lon2):
        """Compute the distance between two lat/lon points using geodesic distance"""

        p = math.pi/180
        earth_diameter = 12742 # in meters
        hav = 0.5 - np.cos((lat2-lat1)*p)/2 + np.cos(lat1*p)*np.cos(lat2*p) * (1-np.cos((lon2-lon1)*p)) / 2
        return earth_diameter * np.arcsin(np.sqrt(hav))

    def closest(self, lat_point, lon_point, lat_map, lon_map, row_indices, col_indices):
        """
            Find the closest conus index to the lat_point, lon_point. Return [x, y].

            Use the lat_map, lon_map that map grid points to lat/lon points.
            Use the row_indicies, col_indicies that contain the grid index.
            The lat_map, lon_map, row_indices, col_indices have the same dimensions.
            These dimensions could be subset for performance prior to calling this method.
        """

        dist_ = self.distance(lat_point,lon_point,lat_map,lon_map)

        x = col_indices[dist_ == np.nanmin(dist_)]
        y = row_indices[dist_ == np.nanmin(dist_)]
        return (int(x), int(y))

