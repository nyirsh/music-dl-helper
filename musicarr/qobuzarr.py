"""This module provides all the login for qobuz"""

import logging
import io
import os
from flask import jsonify, request
from qobuz_dl.core import QobuzDL
from .stringutils import is_string_none_or_empty, get_last_string_line
from . import app, session


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


def initialize_quobuz():
    """
    Initialize the qobuz downloader. If qobuz_username or qobuz_password aren't provided
    it will try to read them from the environment variables.
    Returns True if the downloader has been successfully initialized
    """
    if not session.qobuz_enabled:
        return None
    if session.qobuz_app is not None:
        return session.qobuz_app

    qobuz_app = QobuzDL()
    qobuz_app.get_tokens()
    qobuz_app.directory = "/app/downloads/qobuz"
    qobuz_app.folder_format = os.environ.get(
        "QOBUZ_FOLDERFORMAT", qobuz_app.folder_format)
    qobuz_app.track_format = os.environ.get(
        "QOBUZ_TRACKFORMAT", qobuz_app.track_format)
    qobuz_app.quality = os.environ.get("QOBUZ_QUALITY", qobuz_app.quality)
    qobuz_app.initialize_client(
        session.qobuz_username, session.qobuz_password, qobuz_app.app_id, qobuz_app.secrets)

    return qobuz_app


def download_from_qobuz(url: str | None):
    """
    Given the URL of a song/album/playlist, it actually performs the download
    and provides a status for it
    """
    if not session.is_qobuz_initialized():
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
        session.qobuz_app.handle_url(url)

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
