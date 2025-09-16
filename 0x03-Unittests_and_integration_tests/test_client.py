#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for the GithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"org": org_name}

        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)

        result = client.org   # ✅ no parentheses

        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_payload)
