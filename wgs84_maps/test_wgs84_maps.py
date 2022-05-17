import json
import time
from wgs84_maps import WGS84Mapping

def read_bounds(domain_state_path):
    """
        Read the bounds from the state in a hydrogen domain directory.
        Returns (grid_bounds, wgs84_bounds, conus).
        The value of conus is either 'conus1' or 'conus2' depending on the domain.
        The grid_bounds in (min_x, min_y, max_x, max_y) in conus grid coordinates.
        The wgs84_bounds is (min_lon, min_lat, max_lon, max_lat) in WGS84 coords
    """

    grid_bounds = None
    wgs84_bounds = None
    conus = None
    with open(domain_state_path, "r") as stream:
        contents = stream.read()
        domain_state = json.loads(contents)
        grid_bounds = domain_state.get("grid_bounds")
        wgs84_bounds = domain_state.get("wgs84_bounds")
        shape_regions = domain_state.get("shape_regions")
        conus = shape_regions[0].get("shape_source")
    return (grid_bounds, wgs84_bounds, conus)

def compare_domain_answer(domain_state_path):
    """Compare the grid bounds from the domain_path with the computed bounds."""

    (grid_bounds, wgs84_bounds, conus) = read_bounds(domain_state_path)
    print(wgs84_bounds)
    print(grid_bounds)
    start_time = time.time()
    wgs84_mapping = WGS84Mapping()
    wgs84_mapping.load_maps(conus)
    (x1, y1) = wgs84_mapping.map_to_grid(wgs84_bounds[0], wgs84_bounds[1])
    (x2, y2) = wgs84_mapping.map_to_grid(wgs84_bounds[2], wgs84_bounds[3])
    result = [x1, y1, x2, y2]
    duration = time.time() - start_time
    print(result)
    print(f"Performed lat/lon map in {duration} seconds")
    (lon1, lat1) = wgs84_mapping.map_to_wgs84(x1, y1)
    (lon2, lat2) = wgs84_mapping.map_to_wgs84(x2, y2)
    map_back = [lon1, lat1, lon2, lat2]
    print("Map back")
    print(map_back)

def test_bosie_idaho():
    """Test Boise idaho"""


    wgs84_mapping = WGS84Mapping()
    wgs84_mapping.load_maps("conus1")
    lon =  -116.70570364923688
    lat = 43.48253132247869
    point = wgs84_mapping.map_to_grid(lon, lat)
    print(point)
    point = wgs84_mapping.map_to_wgs84(point[0], point[1])
    print(point)

# Compare the grid bounds from a hydrogen domain path to test the mapping algorithm
#compare_domain_answer("/home/HYDROAPP/bill/wh3248/bill2/domain_state.json")
test_bosie_idaho()


    

