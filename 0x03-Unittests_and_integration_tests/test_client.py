#!/usr/bin/env python3
"""
Unit and integration tests for GithubOrgClient.

This file contains:
1. Unit tests for individual methods of GithubOrgClient.
2. Integration tests that simulate requests to the GitHub API,
   using fixtures and patching external requests.

We use:
- unittest for the test framework
- parameterized for parameterized testing
- unittest.mock for mocking external dependencies
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from utils import get_json
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient methods"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Test the `org` property of GithubOrgClient.

        - Patches `client.get_json` to return a fake payload.
        - Verifies that the returned org matches the payload.
        - Verifies that the correct URL was called.
        """
        mock_payload = {"login": org_name}
        mock_get_json.return_value = mock_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, mock_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """
        Test the `_public_repos_url` property.

        - Mocks the `org` property to return a repos_url.
        - Verifies that the property returns the correct URL.
        """
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": "http://example.com/repos"}

            client = GithubOrgClient("google")
            result = client._public_repos_url

            self.assertEqual(result, "http://example.com/repos")

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        Test the `public_repos` method.

        - Patches `_public_repos_url` to return a fake URL.
        - Patches `get_json` to return a fake repos payload.
        - Verifies that the method returns the expected list of repo names.
        """
        mock_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = mock_payload

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = "http://example.com/repos"

            client = GithubOrgClient("google")
            result = client.public_repos()

            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://example.com/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test the static method `has_license`.

        - Checks whether the method correctly identifies
          when a repo has the given license key.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


# Integration tests with parameterized_class
@parameterized_class((
    "org_payload", "repos_payload", "expected_repos", "apache2_repos"
), [
    (org_payload, repos_payload, expected_repos, apache2_repos),
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.

    These tests:
    - Mock external requests to GitHub API using fixtures.
    - Test the behavior of `public_repos` and license filtering.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the patcher for `requests.get`.

        The `side_effect` simulates responses for:
        - orgs URL -> returns org_payload
        - repos URL -> returns repos_payload
        """
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            if "orgs" in url:
                return Mock(json=lambda: cls.org_payload)
            elif "repos" in url:
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: {})

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Stop the requests.get patcher after tests.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test that `public_repos` returns the expected repositories list.

        Uses the `expected_repos` fixture for verification.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test that `public_repos` filters repositories by license.

        Uses the `apache2_repos` fixture for verification when filtering
        by license="apache-2.0".
        """
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
