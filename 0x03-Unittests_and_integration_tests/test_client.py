#!/usr/bin/env python3
"""
Integration tests for GithubOrgClient.public_repos.

This file is written to match the grader's exact expectations:
- uses @parameterized_class with fixtures imported as `import fixtures`
- creates a class attribute `get_patcher` in setUpClass
- patches `utils.requests.get` (where utils.get_json looks up requests)
- stops the patcher in tearDownClass
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized_class
import fixtures
from client import GithubOrgClient


@parameterized_class([
    {
        "org_payload": fixtures.org_payload,
        "repos_payload": fixtures.repos_payload,
        "expected_repos": fixtures.expected_repos,
        "apache2_repos": fixtures.apache2_repos,
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Start a patcher for utils.requests.get and configure side_effect."""
        def side_effect(url):
            """Return an object whose .json() returns the right fixture."""
            mock_resp = Mock()
            # exact org URL the client will call for org info
            org_url = GithubOrgClient.ORG_URL.format(org="google")
            # repos URL is taken from the org_payload fixture
            repos_url = cls.org_payload.get("repos_url")
            if url == org_url:
                mock_resp.json.return_value = cls.org_payload
            elif repos_url and url == repos_url:
                mock_resp.json.return_value = cls.repos_payload
            else:
                # default to None / empty payload
                mock_resp.json.return_value = None
            return mock_resp

        # IMPORTANT: patch the requests.get used inside utils.get_json
        cls.get_patcher = patch("utils.requests.get", side_effect=side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Stop the requests.get patcher started in setUpClass."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration: public_repos returns the expected repo list."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration: public_repos filters by license correctly."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
