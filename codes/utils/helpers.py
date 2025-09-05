import os

def get_default_host() -> str:
    """Get default host based on environment"""
    # Try to get from environment first
    if host_env := os.environ.get('HOST'):
        return host_env

    # Check if running in Cloud Run
    if os.environ.get('K_SERVICE'):
        # In Cloud Run but HOST not set - this is an error state
        raise ValueError("HOST environment variable must be set in Cloud Run")

    # Local development default
    return 'localhost'
