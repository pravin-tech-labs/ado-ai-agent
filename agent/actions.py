from enum import Enum


class AgentAction(Enum):
    """
    Represents the possible actions the AI Agent can take.
    """

    NO_ACTION = "no_action"
    CREATE_BRANCH = "create_branch"
    STAGE_CHANGES = "stage_changes"
    COMMIT = "commit"
    PUSH = "push"
    CREATE_PR = "create_pr"