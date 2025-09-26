#!/usr/bin/env python3
"""
Middleware to restrict access to the messaging app
based on server time.

Only allows access between 06:00 and 21:00 (6 AM - 9 PM).
Outside these hours, requests return HTTP 403 Forbidden.
"""

from datetime import datetime
from django.http import HttpResponseForbidden


class RestrictAccessByTimeMiddleware:
    """
    Middleware that restricts access to the chats app
    outside of working hours (6AM - 9PM).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current server time (24-hour format)
        current_hour = datetime.now().hour

        # Allowed window: 6 <= hour < 21
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden(
                "Access to the messaging app is restricted at this time. "
                "Please try again between 6AM and 9PM."
            )

        # Continue normal request processing
        response = self.get_response(request)
        return response
