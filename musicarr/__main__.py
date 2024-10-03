"""Application entrypoint"""

import os
import sys
import logging
from .stringutils import is_string_none_or_empty
from . import app  # pylint: disable=unused-import


logging.basicConfig(level=logging.INFO)

# Reads Env values
qobuz_username = os.environ.get("QOBUZ_USERNAME", None)
qobuz_password = os.environ.get("QOBUZ_PASSWORD", None)

# Given that for now only Qobuz is implemented, I can say that if no credentials have been provided
# there's nothing to do and the application shouldn't even run
if is_string_none_or_empty(qobuz_username) or is_string_none_or_empty(qobuz_password):
    logging.error("Musicarr: Must specify username and password")
    sys.exit(1)
else:
    # This will also initialize the routes, but only if Qobuz is enabled
    from . import qobuzarr
    qobuzarr.initialize_quobuz(qobuz_username, qobuz_password)
