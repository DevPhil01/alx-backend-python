#!/usr/bin/env python3
"""
Unit and integration tests for GithubOrgClient.
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
import fixtures
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google", {"org": "google"}),
        ("abc", {"org": "abc"}),
    ])
    @patch("client.get_json", return_value={"org": "test"})
    def test_org(self, org_name, expected_payload, mock_get_json):
        """Test GithubOrgClient.org returns the expected payload."""
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, {"org": "test"})

    def test_public_repos_url(self):
        """Test _public_repos_url reads repos_url from org payload."""
        fake_payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
        client = GithubOrgClient("test_org")
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = fake_payload
            result = client._public_repos_url
            self.assertEqual(result, fake_payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos uses _public_repos_url and get_json."""
        client = GithubOrgClient("test_org")
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/test_org/repos"
            mock_get_json.return_value = [
                {"name": "repo1"},
                {"name": "repo2"},
            ]
            result = client.public_repos()
            expected = ["repo1", "repo2"]
            self.assertEqual(result, expected)
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/test_org/repos"
            )
            self.assertTrue(mock_url.called)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns True when license_key matches."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class((
    "org_payload", "repos_payload", "expected_repos", "apache2_repos"
), [
    (
        fixtures.org_payload,
        fixtures.repos_payload,
        fixtures.expected_repos,
        fixtures.apache2_repos,
    ),
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Start patcher for utils.requests.get and configure side_effect."""
        cls.get_patcher = patch("utils.requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Return Mock with .json() for known URLs."""
            m = Mock()
            org_url = GithubOrgClient.ORG_URL.format(org="google")
            repos_url = cls.org_payload.get("repos_url")
            if url == org_url:
                m.json.return_value = cls.org_payload
            elif repos_url and url == repos_url:
                m.json.return_value = cls.repos_payload
            else:
                m.json.return_value = None
            return m

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration: public_repos returns expected repos list."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration: public_repos filters repos by license."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
