import io
import re
import os
import sys
import logging
from flask import Flask, request, jsonify
from qobuz_dl.core import QobuzDL

def isStringNoneOrEmpty(var):
    return var is None or (isinstance(var, str) and len(var) == 0)

logging.basicConfig(level=logging.INFO)
email = os.environ.get("QOBUZ_USERNAME", None)
password = os.environ.get("QOBUZ_PASSWORD", None)

if isStringNoneOrEmpty(email) or isStringNoneOrEmpty(password):
    logging.error("Must specify username and password")
    sys.exit(1)

app = Flask(__name__)

qobuz = QobuzDL()
qobuz.get_tokens()

# Sets up the possible variables
qobuz.directory = "/downloads/qobuz"
qobuz.folder_format = os.environ.get("QOBUZ_FOLDERFORMAT", qobuz.folder_format)
qobuz.track_format = os.environ.get("QOBUZ_TRACKFORMAT", qobuz.track_format)
qobuz.quality = os.environ.get("QOBUZ_QUALITY", qobuz.quality)
qobuz.initialize_client(email, password, qobuz.app_id, qobuz.secrets)

@app.route('/qobuz', methods=['POST'])
def handle_qobuz():
    # Get the data from the POST request
    data = request.get_json()

    # Ensure 'urls' is provided and is a list
    if 'urls' not in data or not isinstance(data['urls'], list):
        return jsonify({"error": "No valid list of URLs provided"}), 400
    
    urls = data['urls']
    response_data = []

    # Loop through each URL and process it
    for url in urls:
        result = downloadFromQobuz(url)
        response_data.append({
            "url": url,
            "output": result
        })  

    return jsonify({"results": response_data}), 200


def getLastLogLine(multi_line_string):
    # Split the string into lines and strip whitespace
    lines = [line.strip() for line in multi_line_string.splitlines()]
    
    # Filter out empty lines
    non_empty_lines = [line for line in lines if line]

    # Return the last non-empty line, or None if there are no non-empty lines
    return remove_ansi_codes(non_empty_lines[-1]) if non_empty_lines else None

def remove_ansi_codes(text):
    ansi_escape_pattern = re.compile(r'\x1B\[[0-?9;]*[mK]')
    return ansi_escape_pattern.sub('', text)

def downloadFromQobuz(url):
    if isinstance(url, str):
        logging.info(f"Processing Qobuz URL: {url}")
            
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
            qobuz.handle_url(url)

            # Store the captured log output in a string
            captured_log_output = log_stream.getvalue()
            result = getLastLogLine(captured_log_output)

            logging.info(result)
            return result if result else "Unknown"
        except Exception as e:
            logging.error(e)
            return "Error"
        finally:
            logger.removeHandler(handler)
    else:
        return "Invalid URL"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)