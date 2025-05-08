"""
    API endpoint to return a byte stream of a call to get_gridded_data() using numpy savez method.
    This is a prototype to compare with other methods. This would need to be improved to add
    api logging and user data limit checking to be used in production. For now this is only used
    to compare performance with other methods of returning data.
"""

# pylint: disable=C0103,W0703,E0401,C0301,R0914,R1702,W0702,E0633,R1732,R0915,W0632,R0912
import json
import datetime
import io
import logging
import flask
import numpy as np
import xarray as xr
import hf_hydrodata as hf
import base_app


@base_app.app.route(
    "/api/gridded-data",
    methods=["GET"],
)
def gridded_data_route() -> flask.Response:
    """
    Get a byte stream of a call to get_gridded_data().
    Returns:
        A compressed zip byte stream of a numpy array created by numpy.savez with allow_pickle=False.
    Query parameters may be any filter options passed go hf_hydrodata.get_gridded_data().
    """

    try:
        query_parameters = flask.request.args
        options = _convert_strings_to_json(query_parameters)

        bytes_data = generate_netcdf(options)
        response = base_app.app.response_class(
            flask.stream_with_context(_response_generator(bytes_data)),
            mimetype="application/octet-stream",
        )
        response.headers.set(
            "Content-Disposition", "attachment", filename="variable"
        )
        return response

        data = hf_hydrodata.get_gridded_data(options)
        byte_io = io.BytesIO()
        np.savez(byte_io, variable=data, allow_pickle=False)
        result = byte_io.getvalue()
        byte_io.close()
        response = base_app.app.response_class(
            flask.stream_with_context(_response_generator(result)),
            mimetype="application/octet-stream",
        )
        response.headers.set(
            "Content-Disposition", "attachment", filename="variable"
        )
        return response
    except Exception as e:
        logging.exception("Error while downloading requested national data.")
        response = {"status": "fail", "message": str(e)}
        return flask.Response(json.dumps(response), status=400)


def _convert_strings_to_json(options):
    options = dict(options)
    for key, value in options.items():
        if key == "latlng_bounds":
            if isinstance(value, str):
                options[key] = json.loads(value)
        if key == "latlon_bounds":
            if isinstance(value, str):
                options["latlng_bounds"] = json.loads(value)
        if key == "grid_bounds":
            if isinstance(value, str):
                options[key] = json.loads(value)
        if key == "grid_point":
            if isinstance(value, str):
                options[key] = json.loads(value)
        if key == "latlon_point":
            if isinstance(value, str):
                options[key] = json.loads(value)
        if key == "latlng_point":
            if isinstance(value, str):
                options["latlon_point"] = json.loads(value)
        if key == "time_values":
            if isinstance(value, str):
                options[key] = json.loads(value)
        if key == "start_time":
            if isinstance(value, str):
                options[key] = datetime.datetime.strptime(value, "%Y-%m-%d")
        if key == "end_time":
            if isinstance(value, str):
                options[key] = datetime.datetime.strptime(value, "%Y-%m-%d")
    return options


def _response_generator(dataset_bytes):
    chunk_size = 100000
    offset = 0

    while offset < len(dataset_bytes):
        end = min(offset + chunk_size, len(dataset_bytes))
        chunk = dataset_bytes[offset:end]
        offset = end
        yield chunk

def generate_netcdf(options):
    """Generate NetCDF file from numpy data array"""

    data = hf.get_gridded_data(options)
    dims = ["time", "x", "y"]
    variable = options.get("variable")
    metadata = {}
    data_da = xr.DataArray(
        data=data,
        dims=dims,
        name=variable,
        attrs=metadata)
    data_ds = data_da.to_dataset(promote_attrs=True)
    dataset_bytes = data_ds.to_netcdf()
    return dataset_bytes

