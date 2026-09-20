from dataclasses import dataclass


@dataclass
class PullRequestRequest:
    """
    Represents the information required to create a pull request.
    """

    source_branch: str
    target_branch: str
    title: str
    description: str = ""