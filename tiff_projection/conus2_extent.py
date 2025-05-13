"""
    Compute CONUS2 LAT/LON extent in various different ways
"""
import hf_hydrodata as hf
import geopandas as gpd
import pyproj
import fiona
import parflow


def get_conus2_extent(offset_x, offset_y, only_masked=True, transform_function="hf_hydrodata"):
    """Find the lat,lon  bounds using the x,y offset to find the center or bottom,left, top right of cell."""

    options = {"variable": "mask", "grid": "conus2"}
    mask = hf.get_gridded_data(options)
    print(mask.shape)
    min_lat = 1000.0
    min_lon = 0.0
    max_lat = 0
    max_lon = -300
    for x in range(0, 4222):
        for y in range(0, 3256):
            if not only_masked or mask[y,x] == 1.0:
                lat, lon = to_latlon(transform_function, x+offset_x, y+offset_y)
                if lon < min_lon:
                    min_lon = lon
                if lon > max_lon:
                    max_lon = lon
                if lat > max_lat:
                    max_lat = lat
                if lat < min_lat:
                    min_lat = lat
    print(f"Bounds OnlyMasked {only_masked} {transform_function} Offset +{offset_x},+{offset_y} = {min_lon}, {min_lat}, {max_lon}, {max_lat}")

def get_latlon_centers_extent(only_masked=True):
    """Find the lat,lon bounds using the Latitude/Longitude files with cached centers of CONUS2."""

    latitude_centers = parflow.read_pfb("/hydrodata/national_mapping/CONUS2/Latitude_CONUS2.pfb")
    longitude_centers = parflow.read_pfb("/hydrodata/national_mapping/CONUS2/Longitude_CONUS2.pfb")
    print(latitude_centers.shape)
    print(longitude_centers.shape)

    options = {"variable": "mask", "grid": "conus2"}
    mask = hf.get_gridded_data(options)
    print(mask.shape)
    min_lat = 1000.0
    min_lon = 0.0
    max_lat = 0
    max_lon = -300
    for x in range(0, 4222):
        for y in range(0, 3256):
            if not only_masked or mask[y,x] == 1.0:
                lat = latitude_centers[0, y, x]
                lon = longitude_centers[0, y, x]
                if lon < min_lon:
                    min_lon = lon
                if lon > max_lon:
                    max_lon = lon
                if lat > max_lat:
                    max_lat = lat
                if lat < min_lat:
                    min_lat = lat
    print(f"Bounds PFB Files OnlyMasked {only_masked}  = {min_lon}, {min_lat}, {max_lon}, {max_lat}")

def get_shapefile_extent(path):
    """Find the lat/lon bounds from the shapefile path."""

    gdf = gpd.read_file(path)

    # Get the bounds
    bounds = gdf.total_bounds
    minx, miny, maxx, maxy = bounds

    print(f"Shapefile bounds: {miny}, {minx}, {maxy}, {maxx}")
    with fiona.open(path) as shp:
        crs = shp.crs
        print(crs)
        proj4 = pyproj.CRS.from_user_input(crs).to_proj4()
        print(proj4)

CONUS2_PROJ4 = "+proj=lcc +lat_1=30 +lat_2=60 +lon_0=-97.0 +lat_0=40.0000076294444 +a=6370000.0 +b=6370000"
CONUS2_ORIGIN_X = 2208000.30881173
CONUS2_ORIGIN_Y = 1668999.65483222
TO_METERS_TRANSFORM = pyproj.Transformer.from_crs(
         "epsg:4326", CONUS2_PROJ4, always_xy=True
    )
TO_LATLON_TRANSFORM = pyproj.Transformer.from_crs(
         CONUS2_PROJ4, "epsg:4326",always_xy=True
    )

def to_latlon(transform_function, x, y):
    if transform_function == "hf_hydrodata":
        lat, lon = hf.to_latlon("conus2", x, y)
    else:
        lon, lat = TO_LATLON_TRANSFORM.transform(x*1000 - CONUS2_ORIGIN_X, y*1000 - CONUS2_ORIGIN_Y)

    return [lat, lon]

def check():
    print("HF_HYDRODATA", to_latlon("hf_hydrodata", 0, 3255))
    #print("PYPROJ METERS", to_latlon("pyproj", 22.363684830466163, -117.85293938388841))
    print("PYPROJ LATLNG", to_latlon("pyproj", 0, 3255))

#check()
get_conus2_extent(1.0, 1.0, True, "hf_hydrodata")
#get_shapefile_extent("/hydrodata/national_mapping/CONUS2/HUC2_CONUS2_grid.shp")
#get_shapefile_extent("/hydrodata/temp/CONUS2_huc8fix/HUC2_CONUS2_grid.shp")
#get_latlon_centers_extent(False)