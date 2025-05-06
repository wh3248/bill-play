"""
    Package to define the flask app object so this can be shared to different routes.
"""

import flask
from flask_cors import CORS

app = flask.Flask(__name__)
"""Global constant. Imported by functions that define flask routes with @route."""
CORS(app)
