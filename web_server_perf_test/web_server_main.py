"""
main.py
    This is the main routine for the demo flask API web server
"""

# pylint: disable=W0611,W0718

import logging
import base_app
import gridded_data
import wait

app = base_app.app

if __name__ == "__main__":
    try:
        PORT = 5300
        app.run(host="0.0.0.0", port=PORT)
    except Exception as e:
        logging.exception("Fatal error in web server. Stopping web-server.")
