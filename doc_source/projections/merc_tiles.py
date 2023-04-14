"""
Utility functions to support projections into Mercantile images.
"""


import mercantile
import pyproj
import json
import PIL.Image
import numpy as np
import IPython.display


def convert_conic_to_conus(conic: list):
    """Convert from conic to Conus 1 coordinates.

    Args:
        conus: An array of [x,y] in ESRI:10204 coordinates

    Returns:
        An array of [x,y] in CONUS 1 coordinates.
    """
    x = conic[0]
    y = conic[1]

    # Convert from meters to Kilometers and adjust to origin of conus1 on world map.
    x_origin = -1885055.4994999999180436
    y_origin = -604957.0653999999631196
    x = int((x - x_origin) / 1000)
    y = int((y - y_origin) / 1000)
    return (x, y)


def convert_grid_to_conus(
    grid_x: int, grid_y: int, merc_bounds, conic_transformer, rect_size: int
) -> list:
    """Convert a mercantile x,y grid point to conus 1 x,y point.

    Args:
        grid_x:             X coordinate within a mercantile tile.
        grid_y:             Y coordinate within a mercantile tile.
        merc_bounds:        tile bounding box with attributes north,south.east,west in lat/lng.
        conic_transformer:  a pyproj transformer from lat/lng to conic
        rect_size:          the width and height of the mercantile tile.

    Returns:
        An array [x,y] in conus 1 coordinates.
    """

    lng_width = merc_bounds.east - merc_bounds.west
    lat_height = merc_bounds.north - merc_bounds.south
    lat = merc_bounds.south + grid_y * lat_height / rect_size
    lng = merc_bounds.west + grid_x * lng_width / rect_size
    (x, y) = convert_conic_to_conus(conic_transformer.transform(lat, lng))
    return (x, y)


def convert_grid_from_conus(
    conus_x: int, conus_y: int, merc_bounds, transformer, rect_size: int = 32
) -> list:
    """Convert a conus x,y point to a mercantile x,y point to reverse convert_grid_to_conus (debugging only).

    Args:
        conus_x:    Conus X coordinate
    """

    result_x = None
    result_y = None
    result_dist = 1000000
    for grid_x in range(0, rect_size):
        for grid_y in range(0, rect_size):
            (x, y) = convert_grid_to_conus(
                grid_x, grid_y, merc_bounds, transformer, rect_size
            )
            dist = (x - conus_x) ** 2 + (y - conus_y) ** 2
            if dist < result_dist:
                if dist < 5:
                    print(x, y, dist)
                result_dist = dist
                result_x = grid_x
                result_y = grid_y
    return (result_x, result_y)


def load_domain_mask(environment_name, user_id, domain_id):
    """Load a domain mask as a numpy array. Return the mask and the conus bounds."""

    domain_path = f"/home/HYDROAPP/{environment_name}/{user_id}/{domain_id}"
    with open(f"{domain_path}/domain_state.json", "r") as stream:
        contents = stream.read()
        domain_state = json.loads(contents)

    # Get bounds from domain_state
    grid_bounds = domain_state.get("grid_bounds")

    # Load a domain mask png file without any projection information into a numpy array
    domain_mask_path = f"{domain_path}/domain_files/domain_mask.png"
    mask_image = PIL.Image.open(domain_mask_path)
    mask_data = np.array(mask_image)
    return (mask_data, grid_bounds)
