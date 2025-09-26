#!/usr/bin/env python3
"""
Custom middlewares for the chats app:
1. RequestLoggingMiddleware → Logs every user request
2. RestrictAccessByTimeMiddleware → Restricts access outside 6AM–9PM
3. OffensiveLanguageMiddleware → Limits messages per IP (rate limiting)
"""

import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, JsonResponse

# ---------------------------
# Setup logger
# ---------------------------
logger = logging.getLogger(__name__)
handler = logging.FileHandler("requests.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware:
    """Logs each request with timestamp, user, and path."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_entry)
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    """Restricts access outside 6AM–9PM."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour >= 21:
            return HttpResponseForbidden(
                "Access restricted. Try again between 6AM and 9PM."
            )
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware to limit number of chat messages from a single IP.
    Allows max 5 messages per 1-minute window per IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to track message count per IP: { ip: [timestamps] }
        self.message_log = {}

    def __call__(self, request):
        # Apply only to POST requests to messages endpoint
        if request.method == "POST" and "messages" in request.path.lower():
            ip = self.get_client_ip(request)
            now = datetime.now()

            # Initialize list if IP not tracked
            if ip not in self.message_log:
                self.message_log[ip] = []

            # Filter timestamps to only keep those within the last 60s
            one_minute_ago = now - timedelta(minutes=1)
            self.message_log[ip] = [
                ts for ts in self.message_log[ip] if ts > one_minute_ago
            ]

            # Enforce rate limit
            if len(self.message_log[ip]) >= 5:
                return JsonResponse(
                    {
                        "error": "Rate limit exceeded. "
                        "You can only send 5 messages per minute."
                    },
                    status=429,
                )

            # Log the new message timestamp
            self.message_log[ip].append(now)

        return self.get_response(request)

    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request headers or META."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR", "unknown")
