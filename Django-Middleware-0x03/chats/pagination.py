#!/usr/bin/env python3
"""
Custom pagination for the chats app.

This file defines a pagination class that limits messages
to 20 per page and exposes useful metadata such as total count.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MessagePagination(PageNumberPagination):
    """
    Pagination class for messages.
    - Defaults to 20 messages per page.
    - Allows clients to override the page size with `page_size` query param,
      up to a maximum of 100.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return a custom paginated response including:
        - total count
        - next/previous links
        - current page size
        - results
        """
        return Response({
            "count": self.page.paginator.count,   # ✅ explicitly included
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "page_size": self.page_size,
            "results": data,
        })
