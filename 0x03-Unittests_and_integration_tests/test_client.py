#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient
"""

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
        expected_payload = {"login": org_name}
        expected_url = f"https://api.github.com/orgs/{org_name}"

        # Mock return value
        mock_get_json.return_value = expected_payload

        # Instantiate client
        client = GithubOrgClient(org_name)

        # Since org is memoized property, access without ()
        result = client.org

        # Assert get_json was called with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

        # Assert result matches mocked payload
        self.assertEqual(result, expected_payload)


if __name__ == "__main__":
    unittest.main()
