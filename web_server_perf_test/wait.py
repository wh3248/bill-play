"""
    API endpoint to return a byte stream of a call to get_gridded_data() using numpy savez method.
    This is a prototype to compare with other methods. This would need to be improved to add
    api logging and user data limit checking to be used in production. For now this is only used
    to compare performance with other methods of returning data.
"""

# pylint: disable=C0103,W0703,E0401,C0301,R0914,R1702,W0702,E0633,R1732,R0915,W0632,R0912
import os
import time
import flask
import base_app


@base_app.app.route(
    "/api/wait",
    methods=["GET"],
)
def wait_route() -> flask.Response:
    """
    Route to wait the specified number of seconds before returning. Defaults to 1 second.
    """
    
    query_parameters = flask.request.args
    nworkers = os.getenv("NWORKERS_ARG")
    nthreads = os.getenv("NTHREADS_ARG")
    gtype = os.getenv("GTYPE_ARG")

    wait_time = int(query_parameters.get("wait_time", "0"))
    if wait_time > 0:
        time.sleep(wait_time)
    return {"workers": nworkers, "threads": nthreads, "gtype": gtype, "wait_time": wait_time}
