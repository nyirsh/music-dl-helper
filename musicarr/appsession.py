"""Handles the application session"""

import os
from .stringutils import is_string_none_or_empty


class AppSession:
    """Session class for the application."""

    def __init__(self):
        self.musicarr_initialized = False

        # Qobuz handlers
        self.qobuz_username = os.environ.get("QOBUZ_USERNAME", None)
        self.qobuz_password = os.environ.get("QOBUZ_PASSWORD", None)
        self.qobuz_enabled = self.is_qobuz_enabled()
        self.qobuz_error = False
        self.qobuz_app = None

        # When multiple services will be added they should be included here too
        self.musicarr_enabled = self.qobuz_enabled

    def is_qobuz_enabled(self):
        """Check if Qobuz is enabled based on credentials."""
        return not (is_string_none_or_empty(self.qobuz_username)
                    or is_string_none_or_empty(self.qobuz_password))

    def is_qobuz_initialized(self):
        """Check if Qobuz is properly initialized"""
        if self.qobuz_enabled:
            return not self.qobuz_app is None
        return False

    def initialize(self):
        """Initialize Qobuz if enabled."""
        everything_initialized = True

        if self.qobuz_enabled:
            # I only want to activate all qobuz-related routes and so on only if qobuz is enabled
            from . import qobuzarr  # pylint: disable=import-outside-toplevel
            self.qobuz_app = qobuzarr.initialize_quobuz()
            self.qobuz_error = self.qobuz_app is None
            if everything_initialized and self.qobuz_error:
                everything_initialized = False

        # Should be true if all of the services have been initialized without issues
        # and if there is at least one enabled service
        self.musicarr_initialized = self.musicarr_enabled and everything_initialized
        return self.musicarr_initialized
