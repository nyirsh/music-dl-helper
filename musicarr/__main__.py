"""Application entrypoint"""

from . import app, session


@app.route('/health')
def health_check():
    """
    A simple route that checks everything is in working condition
    """

    if session.musicarr_initialized:
        return "Healthy", 200  # Respond with a 200 OK status if healthy

    return "Unhealthy", 503  # Respond with a 503 Service Unavailable if not healthy
