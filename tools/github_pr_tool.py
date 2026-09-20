from models.pr_request import PullRequestRequest
from config.settings import settings
from tools.pr_tool import PRTool
from tools.github_api_client import GitHubAPIClient


class GitHubPRTool(PRTool):
    """
    GitHub implementation of the pull request tool.
    """

    def __init__(self, repository: str | None = None):
        repository = (
            repository
            if repository is not None
            else settings.github_repository
        )

        if not isinstance(repository, str):
            raise ValueError("Repository must be a string.")

        repository = repository.strip()

        if not repository:
            raise ValueError(
                "GitHub repository is not configured."
            )

        self.repository = repository

        if not settings.github_token:
            raise ValueError(
                "GitHub token is not configured."
            )

        self.token = settings.github_token
        self.client = GitHubAPIClient(self.token)

    def create_pull_request(
    self,
    request: PullRequestRequest,
    ) -> str:
        """
        Create a pull request on GitHub.
        """
        if not isinstance(request, PullRequestRequest):
            raise ValueError(
                "Request must be a PullRequestRequest."
            )

        payload = {
            "title": request.title,
            "head": request.source_branch,
            "base": request.target_branch,
            "body": request.description,
        }

        response = self.client.post(
            f"/repos/{self.repository}/pulls",
            payload,
        )

        return response["html_url"]