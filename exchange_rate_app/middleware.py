import logging
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request path and headers for debugging
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request headers: {request.headers}")

        # Bypass API key check for admin, static files, and favicon
        path = request.path.lower()
        if path.startswith(('/admin/', '/static/', '/favicon.ico')):
            return self.get_response(request)

        # Check for the API key in the headers
        api_key = request.headers.get('x-api-key')

        if api_key == "#m)mq6b^f&1e0s8i=5)5_!loq#)_xbp1ac1j7r0wdu*1#rbm":
            logger.info("API key validated successfully")

        if api_key != "#m)mq6b^f&1e0s8i=5)5_!loq#)_xbp1ac1j7r0wdu*1#rbm":
            logger.warning("Unauthorized access attempt: Missing or invalid API key")
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        return self.get_response(request)
