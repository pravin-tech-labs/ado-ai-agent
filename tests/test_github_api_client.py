import pytest

from tools.github_api_client import GitHubAPIClient
from unittest.mock import Mock
from unittest.mock import Mock, patch


def test_github_api_client_requires_token():
    with pytest.raises(ValueError):
        GitHubAPIClient("")


def test_github_api_client_rejects_non_string_token():
    with pytest.raises(ValueError):
        GitHubAPIClient(None)


def test_github_api_client_stores_token():
    client = GitHubAPIClient("test-token")

    assert client.token == "test-token"


def test_github_api_client_builds_headers():
    client = GitHubAPIClient("test-token")

    headers = client._get_headers()

    assert headers["Accept"] == "application/vnd.github+json"
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"

def test_handle_response_returns_json():
    client = GitHubAPIClient("test-token")

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "full_name": "owner/repository"
    }

    result = client._handle_response(response)

    assert result == {
        "full_name": "owner/repository"
    }


def test_handle_response_raises_runtime_error():
    client = GitHubAPIClient("test-token")

    response = Mock()
    response.status_code = 404
    response.text = "Not Found"

    import requests

    response.raise_for_status.side_effect = requests.HTTPError(
        "404 Client Error"
    )

    with pytest.raises(RuntimeError, match="status=404"):
        client._handle_response(response)

def test_post_rejects_empty_endpoint():
    client = GitHubAPIClient("test-token")

    with pytest.raises(ValueError):
        client.post("", {})


def test_post_rejects_non_string_endpoint():
    client = GitHubAPIClient("test-token")

    with pytest.raises(ValueError):
        client.post(None, {})


def test_post_rejects_non_dictionary_payload():
    client = GitHubAPIClient("test-token")

    with pytest.raises(ValueError):
        client.post("/test", None)

def test_post_sends_request():
    client = GitHubAPIClient("test-token")

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 123,
        "html_url": "https://github.com/test/repo/pull/1",
    }

    with patch(
        "tools.github_api_client.requests.post",
        return_value=mock_response,
    ) as mock_post:
        result = client.post(
            "/repos/test/repo/pulls",
            {
                "title": "Test PR",
                "head": "feature/test",
                "base": "main",
            },
        )

    mock_post.assert_called_once_with(
        "https://api.github.com/repos/test/repo/pulls",
        headers=client._get_headers(),
        json={
            "title": "Test PR",
            "head": "feature/test",
            "base": "main",
        },
        timeout=30,
    )

    assert result["id"] == 123
    assert result["html_url"] == "https://github.com/test/repo/pull/1"