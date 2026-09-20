import requests


class GitHubAPIClient:
    """
    Handles HTTP communication with the GitHub REST API.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        if not isinstance(token, str):
            raise ValueError("GitHub token must be a string.")

        token = token.strip()

        if not token:
            raise ValueError("GitHub token cannot be empty.")

        self.token = token

    def _get_headers(self) -> dict[str, str]:
        """
        Return common headers for GitHub API requests.
        """
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_repository(self, repository: str) -> dict:
        """
        Get repository information from GitHub.
        """
        if not isinstance(repository, str):
            raise ValueError("Repository must be a string.")

        repository = repository.strip()

        if not repository:
            raise ValueError("Repository cannot be empty.")

        url = f"{self.BASE_URL}/repos/{repository}"

        response = requests.get(
            url,
            headers=self._get_headers(),
            timeout=30,
        )

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> dict:
        """
        Validate a GitHub API response and return its JSON data.
        """
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"GitHub API request failed "
                f"(status={response.status_code}): {response.text}"
            ) from exc

        return response.json()

    def post(self, endpoint: str, payload: dict) -> dict:
        """
        Send a POST request to the GitHub API.
        """
        if not isinstance(endpoint, str):
            raise ValueError("Endpoint must be a string.")

        endpoint = endpoint.strip()

        if not endpoint:
            raise ValueError("Endpoint cannot be empty.")

        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary.")

        url = f"{self.BASE_URL}{endpoint}"

        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=30,
        )

        return self._handle_response(response)