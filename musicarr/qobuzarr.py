"""This module provides all the login for qobuz"""

import logging
import io
import os
from typing import Optional
from flask import jsonify, request
from qobuz_dl.core import QobuzDL
from .stringutils import is_string_none_or_empty, get_last_string_line
from . import app


@app.route('/qobuz', methods=['POST'])
def handle_qobuz():
    """
    Handles the route /qobuz which accepts a json containing a list of URLs
    that needs to be downloaded using `qobuz-dl`.
    It responds with a json that contains a status for all of the provided URLs
    """
    # Get the data from the POST request
    data = request.get_json()

    # Ensure 'urls' is provided and is a list
    if 'urls' not in data or not isinstance(data['urls'], list):
        return jsonify({"error": "No valid list of URLs provided"}), 400

    urls = data['urls']
    response_data = []

    # Loop through each URL and process it
    for url in urls:
        result = download_from_qobuz(url)
        response_data.append({
            "url": url,
            "output": result
        })

    return jsonify({"results": response_data}), 200


QOBUZ_APP: Optional[QobuzDL] = None


def initialize_quobuz(qobuz_username: str | None = None, qobuz_password: str | None = None):
    """
    Initialize the qobuz downloader. If qobuz_username or qobuz_password aren't provided
    it will try to read them from the environment variables.
    Returns True if the downloader has been successfully initialized
    """
    global QOBUZ_APP  # pylint: disable=global-statement
    if QOBUZ_APP is not None:
        return True
    if is_string_none_or_empty(qobuz_username):
        qobuz_username = os.environ.get("QOBUZ_USERNAME", None)
    if is_string_none_or_empty(qobuz_password):
        qobuz_password = os.environ.get("QOBUZ_PASSWORD", None)

    if is_string_none_or_empty(qobuz_username) or is_string_none_or_empty(qobuz_password):
        logging.error("Qobuzarr: Must specify username and password")
        return False

    QOBUZ_APP = QobuzDL()
    QOBUZ_APP.get_tokens()
    QOBUZ_APP.directory = "/downloads/qobuz"
    QOBUZ_APP.folder_format = os.environ.get(
        "QOBUZ_FOLDERFORMAT", QOBUZ_APP.folder_format)
    QOBUZ_APP.track_format = os.environ.get(
        "QOBUZ_TRACKFORMAT", QOBUZ_APP.track_format)
    QOBUZ_APP.quality = os.environ.get("QOBUZ_QUALITY", QOBUZ_APP.quality)
    QOBUZ_APP.initialize_client(
        qobuz_username, qobuz_password, QOBUZ_APP.app_id, QOBUZ_APP.secrets)

    return True


def download_from_qobuz(url: str | None):
    """
    Given the URL of a song/album/playlist, it actually performs the download
    and provides a status for it
    """
    global QOBUZ_APP  # pylint: disable=global-statement, global-variable-not-assigned
    if not initialize_quobuz():
        return "QobuzDL not initialized"
    if is_string_none_or_empty(url):
        return "Invalid URL"
    logging.info("Processing Qobuz URL: %s", url)

    # Create a StringIO object to capture log output
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)

    try:
        # Actually performs the download
        QOBUZ_APP.handle_url(url)

        # Store the captured log output in a string
        captured_log_output = log_stream.getvalue()
        result = get_last_string_line(captured_log_output)

        logging.info(result)
        return result if result else "Unknown"
    except AttributeError:
        logging.error("Invalid URL")
        return "Invalid URL"
    # I genuinely don't know what kind of exceptions qobuz-dl might generate
    # but I don't want the application to crash because of it, so I'm accepting
    # a broad exception to keep things simple
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error(e)
        return "Error"
    finally:
        logger.removeHandler(handler)
