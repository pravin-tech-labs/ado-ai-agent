from dataclasses import dataclass, field


@dataclass
class AgentState:
    """
    Represents the current state of the AI Agent workflow.
    """

    current_branch: str = ""
    base_branch: str = ""
    changed_files: list[str] = field(default_factory=list)

    target_branch: str = ""

    commit_message: str = ""

    committed: bool = False
    pushed: bool = False
    pr_created: bool = False
    pull_request_url: str = ""
    error: str | None = None