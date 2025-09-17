#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from utils import get_json
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, expected, mock_get_json):
        """Test GithubOrgClient.org returns expected payload"""
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url"""
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": "http://fake.url/repos"}
            client = GithubOrgClient("google")
            self.assertEqual(
                client._public_repos_url,
                "http://fake.url/repos"
            )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos"""
        test_payload = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = test_payload

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = "http://fake.url/repos"
            client = GithubOrgClient("google")
            self.assertEqual(
                client.public_repos(),
                ["repo1", "repo2"]
            )
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("http://fake.url/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license"""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url):
            if "orgs" in url:
                return unittest.mock.Mock(json=lambda: cls.org_payload)
            elif "repos" in url:
                return unittest.mock.Mock(json=lambda: cls.repos_payload)
            return unittest.mock.Mock(json=lambda: {})

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test integration of public_repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test integration of public_repos with license filtering"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
