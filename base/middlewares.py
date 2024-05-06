import logging
import time
import uuid
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from request_id import local, release_local
from request_id.middleware import RequestIdMiddleware
from rest_framework.views import exception_handler

logger = logging.getLogger("django.request")


def generate_request_id_hex():
    return uuid.uuid4().hex


def get_request_id(request):
    if hasattr(request, "request_id"):
        if not request.request_id:
            return generate_request_id_hex()
        return request.request_id
    else:
        return generate_request_id_hex()


class RequestIdTraceMiddleware(RequestIdMiddleware):
    def __call__(self, request):
        request_id = get_request_id(request)
        request.request_id = request_id
        local.request_id = request_id

        response = self.get_response(request)

        release_local(local)

        return response


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        self.log_request(request)

        response = self.get_response(request)
        end_time = time.time()

        self.log_response(request, response, (end_time - start_time) * 1000)

        return response

    def log_request(self, request):
        logger.info(f"Request Path {request.path} - Method {request.method}")
        if request.body:
            logger.debug(f"Request body: {request.body}")

    def log_response(self, request, response, request_delta):
        if response.streaming:
            content = "<streaming content>"
        else:
            content = response.content
        logger.debug(f"Response body: {content }")
        logger.info(f"Request delta: {request_delta} ms")

    def process_exception(self, request, exception):
        logger.exception(f"Exception occurred: {exception}")
        if isinstance(exception, Exception):
            response_data = {
                "error": "Internal server error",
                "detail": str(exception)
                if settings.DEBUG
                else "Something went wrong. Our support team has been notified.",
                "time": str(datetime.now()),
            }
            if settings.DEBUG:
                import sys
                import traceback

                response_data["traceback"] = "".join(traceback.format_exception(*sys.exc_info()))
            return JsonResponse(response_data, status=500)
        return None
