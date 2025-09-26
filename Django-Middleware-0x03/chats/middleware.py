#!/usr/bin/env python3
"""
Middleware for logging, restricting access by time, rate limiting,
and role-based permissions in the chats app.
"""

import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden

# Setup logger for request logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("requests.log")
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """Logs each request with timestamp, user, and path."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        logger.info(f"User: {user} - Path: {request.path}")
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """Restricts access outside 6AM - 9PM server time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden("Access restricted during this time.")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware to rate-limit messages based on IP address.
    Allows max 5 messages/minute per IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_request_log = {}

    def __call__(self, request):
        if request.method == "POST" and "/messages" in request.path:
            ip = self.get_client_ip(request)
            now = datetime.now()
            request_times = self.ip_request_log.get(ip, [])

            # Filter only requests within the last minute
            request_times = [
                t for t in request_times if now - t < timedelta(minutes=1)
            ]

            if len(request_times) >= 5:
                return HttpResponseForbidden(
                    "Rate limit exceeded: Max 5 messages per minute."
                )

            request_times.append(now)
            self.ip_request_log[ip] = request_times

        return self.get_response(request)

    def get_client_ip(self, request):
        """Extract client IP address."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class RolepermissionMiddleware:
    """
    Middleware to check user role before granting access.
    Only 'admin' or 'moderator' roles are allowed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check role from user model (assuming 'role' field exists)
            user_role = getattr(request.user, "role", None)

            if user_role not in ["admin", "moderator"]:
                return HttpResponseForbidden(
                    "You do not have permission to access this resource."
                )

        return self.get_response(request)
