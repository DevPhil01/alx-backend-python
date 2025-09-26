#!/usr/bin/env python3
"""
Custom authentication module for the chats app.

This integrates with JWT authentication provided by
`djangorestframework-simplejwt`. You may also extend this file
with additional authentication schemes if required.

Author: Your Name
Date: 2025-09-24
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication.

    Extends the default JWTAuthentication to allow additional checks
    or custom error messages.
    """

    def authenticate(self, request):
        """
        Override the default authenticate method to include
        additional validation if needed.
        """
        try:
            return super().authenticate(request)
        except Exception as e:
            raise AuthenticationFailed(f"JWT authentication failed: {str(e)}")


class CustomSessionAuthentication(SessionAuthentication):
    """
    Custom Session Authentication.

    Extends DRF’s SessionAuthentication to override CSRF checks
    if needed for APIs.
    """

    def enforce_csrf(self, request):
        """
        Optionally disable CSRF enforcement for API endpoints.
        Uncomment the `return` line below if you want to skip CSRF checks.
        """
        return super().enforce_csrf(request)
        # return  # Uncomment to disable CSRF checks entirely
