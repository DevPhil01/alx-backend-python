#!/usr/bin/env python3
"""
Custom middleware for logging user requests.

This middleware logs every incoming request with the timestamp,
user (if authenticated), and the request path.
"""

import logging
from datetime import datetime

from django.utils.deprecation import MiddlewareMixin


class RequestLoggingMiddleware:
    """
    Middleware to log requests with timestamp, user, and request path.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Configure logger
        self.logger = logging.getLogger("request_logger")
        handler = logging.FileHandler("requests.log")
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        # Get user or mark as Anonymous
        user = request.user if request.user.is_authenticated else "Anonymous"

        # Log request details
        self.logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")

        # Continue processing
        response = self.get_response(request)
        return response
