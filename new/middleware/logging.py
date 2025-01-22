# myproject/middleware/logging.py
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Dictionary to keep track of request counts
url_request_count = defaultdict(int)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"request made to :{request.path}")
        start_time = time.time()
        url_request_count[request.path] += 1

        response = self.get_response(request)

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Request URL: {request.path}, Method: {request.method}, "
                    f"Response time: {duration:.2f}s, Count: {url_request_count[request.path]}")

        return response
