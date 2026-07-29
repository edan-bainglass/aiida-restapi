"""Configuration of API"""

from aiida_restapi import __version__

API_CONFIG = {
    'PREFIX': '/v0',
    'VERSION': __version__,
}

CORS_ORIGIN_URLS: list[str] = []
CORS_ALLOW_ORIGIN_REGEX = r'https?://(localhost|127\.0\.0\.1)(:\d+)?'

# Regarding CORS:
# - We support requests from localhost out of the box via the regex pattern above.
# - If you want to allow requests from other origins, you can:
#   - Add them to the CORS_ORIGIN_URLS list above, and/or
#   - Change the regex above to allow other origins
# For more details, see https://fastapi.tiangolo.com/tutorial/cors/#configure-cors
