from abc import ABC, abstractmethod

from models.pr_request import PullRequestRequest


class PRTool(ABC):
    """
    Abstract interface for pull request operations.
    """

    @abstractmethod
    def create_pull_request(
        self,
        request: PullRequestRequest,
    ) -> str:
        """
        Create a pull request and return its identifier or URL.
        """
        raise NotImplementedError