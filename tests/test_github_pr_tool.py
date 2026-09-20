import pytest

from tools.github_pr_tool import GitHubPRTool
from models.pr_request import PullRequestRequest


def test_github_pr_tool_requires_repository(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "",
                "github_token": "test-token",
            },
        )(),
    )

    with pytest.raises(ValueError):
        GitHubPRTool("")


def test_github_pr_tool_rejects_non_string_repository(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "",
                "github_token": "test-token",
            },
        )(),
    )

    with pytest.raises(ValueError):
        GitHubPRTool(None)


def test_github_pr_tool_stores_repository(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "",
                "github_token": "test-token",
            },
        )(),
    )

    tool = GitHubPRTool("owner/repository")

    assert tool.repository == "owner/repository"


def test_github_pr_tool_uses_configured_repository(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "owner/configured-repository",
                "github_token": "test-token",
            },
        )(),
    )

    tool = GitHubPRTool()

    assert tool.repository == "owner/configured-repository"


def test_github_pr_tool_requires_token(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "owner/repository",
                "github_token": "",
            },
        )(),
    )

    with pytest.raises(ValueError):
        GitHubPRTool()


def test_github_pr_tool_stores_token(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "owner/repository",
                "github_token": "test-token",
            },
        )(),
    )

    tool = GitHubPRTool()

    assert tool.token == "test-token"

def test_github_pr_tool_creates_api_client(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "owner/repository",
                "github_token": "test-token",
            },
        )(),
    )

    tool = GitHubPRTool()

    assert tool.client is not None
    assert tool.client.token == "test-token"

def test_create_pull_request(monkeypatch):
    monkeypatch.setattr(
        "tools.github_pr_tool.settings",
        type(
            "TestSettings",
            (),
            {
                "github_repository": "owner/repository",
                "github_token": "test-token",
            },
        )(),
    )

    tool = GitHubPRTool()

    expected_payload = {
        "title": "Add login tests",
        "head": "feature/login-tests",
        "base": "main",
        "body": "Automated login test improvements.",
    }

    def fake_post(endpoint, payload):
        assert endpoint == "/repos/owner/repository/pulls"
        assert payload == expected_payload

        return {
            "html_url": (
                "https://github.com/owner/repository/pull/1"
            )
        }

    monkeypatch.setattr(
        tool.client,
        "post",
        fake_post,
    )

    request = PullRequestRequest(
        source_branch="feature/login-tests",
        target_branch="main",
        title="Add login tests",
        description="Automated login test improvements.",
    )

    result = tool.create_pull_request(request)

    assert result == (
        "https://github.com/owner/repository/pull/1"
    )