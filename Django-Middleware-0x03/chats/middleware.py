#!/usr/bin/env python3
"""
Custom middleware for the chats app:
1. RequestLoggingMiddleware → Logs every user request to requests.log
2. RestrictAccessByTimeMiddleware → Restricts access outside 6AM–9PM
"""

import logging
from datetime import datetime
from django.http import HttpResponseForbidden

# Setup a simple logger for request logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("requests.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """
    Middleware to log each request with timestamp, user, and request path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_entry)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the chats app
    outside of working hours (6AM – 9PM).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour

        # Allowed: 6AM <= hour < 9PM
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden(
                "Access to the messaging app is restricted at this time. "
                "Please try again between 6AM and 9PM."
            )

        response = self.get_response(request)
        return response
