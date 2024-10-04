"""Well it's a flask app so... gotta initialize it somewhere!"""

import logging
import flask
from .appsession import AppSession

logging.basicConfig(level=logging.INFO)

app = flask.Flask(__name__)
session = AppSession()

session.initialize()
if not session.musicarr_initialized:
    logging.error(
        "Application can't run without enabling at least one download source")
