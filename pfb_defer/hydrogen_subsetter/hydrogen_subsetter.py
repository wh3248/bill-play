"""
    Subsetter

    Hydrogen subsetter service class.
"""
import os
import numpy as np

class HydrogenSubSetter:
    """This class provides services to subset various types of files."""

    def __init__(self):
        """Define attributes."""

        self.source_grid_bounds = None
        self.target_grid_bounds = None

    def set_lat_lon_bounds(self, lat_lon_bounds, conus=None, mapping_sa_file=None):
        """
        Set the bounds for subsetting a numpy array in lat/lon coordinates.
        This is required before calling get_grid_bounds().

        The lat_lon_bounds is a bounding box array in lat/lon coordinates to be clipped.
        The lat_lon_bounds is an array [lon_low, lat_low, lon_high, lat_high].

        You must specify either the conus argument or the mapping_sa_file argument.

        If the conus argument is specified the value must be the string conus1 or conus2.

        The mapping_sa_file must be a text file containing the lat/lon coordinates of each 2D point in the input numpy grid.
        The first line of the mapping_sa_file must be dimensions of the input numpy grid "nx ny nz".
        The remaining lines in the file must be lines with "lon lat" values for each (x, y) point in the grid (nx * ny rows).
        The first row is (0, 0), the second row is (1, 0).
        """

        (lon_low, lat_low, lon_high, lat_high) = lat_lon_bounds
        grid_x_low = None
        grid_y_low = None
        grid_x_high = None
        grid_y_high = None
        if conus:
            if conus.lower() == "conus1":
                mapping_sa_file = "/home/HYDROAPP/common/shapefiles/CONUS1/Grid_Centers_Short_Deg.format.txt"
            elif conus.lower() == "conus2":
                mapping_sa_file = "/home/HYDROAPP/common/shapefiles/CONUS2/CONUS2.0.Final.LatLong.sa"
            else:
                raise Exception("The conus argument must be conus1 or conus2")
        if mapping_sa_file is None:
            raise Exception("Either the conus type or the mapping_sa_file must be specified.")
        if not os.path.exists(mapping_sa_file):
            raise Exception(f"Lat/Lon mapping file '{mapping_sa_file}' does not exist.")
        with open(mapping_sa_file, "r") as stream:
            line = stream.read()
            x = -1
            y = -1
            last_x = None
            last_y = None
            for line in line.split("\n"):
                if x < 0:
                    x = 0
                    y = 0
                    shape = line.split(" ")
                    nx = int(shape[0])
                    ny = int(shape[1])
                    self.source_grid_bounds = [nx, ny]
                elif line:
                    (c1, c2) = line.split(" ")
                    lat = float(c1)
                    lon = float(c2)
                    # (x, y) = (lon, lat)
                    if grid_x_low is None and grid_y_low is None:
                        if lat > lat_low and lon > lon_low:
                            grid_x_low = x
                            grid_y_low = y
                    elif grid_x_high is None and grid_y_high is None:
                        if lat > lat_high and lon > lon_high:
                            grid_x_high = last_x
                            grid_y_high = last_y
                            break
                    last_x = x
                    last_y = y
                    x = x + 1
                    if x >= nx:
                        x = 0
                        y = y + 1
                        
        self.target_grid_bounds = [grid_x_low, grid_y_low, grid_x_high, grid_y_high]

    def get_grid_bounds(self):
        """
        Return the target grid bounds in grid coordinates to be sliced from a numpy array
        to create a subset.  The bounds is an array [x_low, y_low, x_high, y_high]

        This requires the set_bounds method to be called first to set the bounds in lat/lon
        coordinates.
        """
        return self.target_grid_bounds

    def subset_np_array(self, input_array, grid_bounds=None, x_first=False):
        """
        Create a new numpy array that is subset from the input_array.
        Create the subset by slicing the x, y dimensions of the array to the grid_bounds.

        If x_first = true then the first two dimensions of the input_array must be (x, y)
        Otherwise, the last two dimensions of the input_array must be (y, x).

        If the grid_bounds is None then use the get_grid_bounds() method to get the grid bounds.

        Returns a new numpy array with the subset data.
        """

        if grid_bounds is None:
            grid_bounds = self.get_grid_bounds()
        if grid_bounds is None:
            raise Exception("The grid_bounds is not specified and set_lat_lon_bounding() was not called before.")
        (grid_x_low, grid_y_low, grid_x_high, grid_y_high) = grid_bounds
        shape = input_array.shape
        if x_first:
            if len(input_array.shape) == 3:
                if self.source_grid_bounds:
                    # Verify numpy input_array dimensions
                    if input_array.shape[0] != self.source_grid_bounds[0]:
                        raise Exception(f"The numpy input_array dimensions are not ({self.source_grid_bounds[0]}, {self.source_grid_bounds[1]}, :)")
                result = input_array[grid_x_low:grid_x_high, grid_y_low:grid_y_high, :]
            elif len(input_array.shape) == 2:
                result = input_array[grid_x_low:grid_x_high, grid_y_low:grid_y_high]
            else:
                raise Exception("The input array must have 2D or 3D shape")
        else:
            if len(input_array.shape) == 3:
                if self.source_grid_bounds:
                    # Verify numpy input_array dimensions
                    if input_array.shape[1] != self.source_grid_bounds[1]:
                        raise Exception(f"The numpy input_array dimensions are not (:, {self.source_grid_bounds[1]}, {self.source_grid_bounds[0]})")
                result = input_array[:, grid_y_low:grid_y_high, grid_x_low:grid_x_high]
            elif len(input_array.shape) == 2:
                result = input_array[grid_y_low:grid_y_high, grid_x_low:grid_x_high]
            else:
                raise Exception("The input array must have 2D or 3D shape")
        return result

if __name__ == "__main__":
    job = HydrogenSubSetter()
    bounds = [-105.6530823845043, 39.50687848028302, -105.02288986385359, 39.72148233874503]
    job.set_lat_lon_bounds(bounds, conus="conus1")
    grid_bounds = job.get_grid_bounds()
    print(grid_bounds)
    print(job.source_grid_bounds)
