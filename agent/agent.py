import re

from models.agent_state import AgentState
from tools.git_tool import GitTool
from agent.actions import AgentAction


class Agent:
    """
    Core AI Agent responsible for orchestrating repository operations.
    """

    def __init__(self, repo_path: str = "."):
        self.git_tool = GitTool(repo_path)
        self.state = AgentState()

    def inspect_repository(self) -> AgentState:
        """
        Inspect the repository and populate the agent state.
        """
        status = self.git_tool.get_repository_status()

        self.state.current_branch = status.branch

        if not self.state.base_branch:
            self.state.base_branch = status.branch

        self.state.changed_files = self.git_tool.get_all_changed_files()

        return self.state

    def determine_next_action(self) -> AgentAction:
        """
        Determine the next action based on the current agent state.
        """
        if not self.state.changed_files:
            return AgentAction.NO_ACTION

        if self.state.current_branch == self.state.base_branch:
            return AgentAction.CREATE_BRANCH

        return AgentAction.STAGE_CHANGES

    def generate_branch_name(self, task_description: str) -> str:
        """
        Generate a feature branch name from a task description.
        """
        if not isinstance(task_description, str):
            raise ValueError("Task description must be a string.")

        task_description = task_description.strip().lower()

        if not task_description:
            raise ValueError("Task description cannot be empty.")

        branch_suffix = re.sub(
            r"[^a-z0-9]+",
            "-",
            task_description
        ).strip("-")

        if not branch_suffix:
            raise ValueError(
                "Task description must contain letters or numbers."
            )

        branch_name = f"feature/{branch_suffix}"

        self.git_tool.validate_branch_name(branch_name)

        return branch_name

    def create_feature_branch(self, task_description: str) -> str:
        """Create a feature branch and save it in agent state."""
        if self.determine_next_action() != AgentAction.CREATE_BRANCH:
            raise RuntimeError(
                "Agent is not ready to create a feature branch."
            )

        branch_name = self.generate_branch_name(task_description)

        self.git_tool.create_branch(branch_name)

        self.state.target_branch = branch_name
        self.state.current_branch = branch_name

        return branch_name

    def stage_changes(self) -> list[str]:
        """Stage all detected changed files."""
        if not self.state.changed_files:
            raise RuntimeError("No changed files available to stage.")

        staged_files = self.git_tool.add_file(
            self.state.changed_files
        )

        return staged_files

    def commit_changes(self, commit_message: str) -> str:
        """Commit the staged changes."""
        if not commit_message or not commit_message.strip():
            raise ValueError("Commit message cannot be empty.")

        if not self.git_tool.get_staged_files():
            raise RuntimeError("No staged files available to commit.")

        self.git_tool.commit_changes(commit_message.strip())

        self.state.commit_message = commit_message.strip()
        self.state.committed = True

        return self.state.commit_message

    def push_changes(self) -> str:
        """Push the committed feature branch."""
        if not self.state.committed:
            raise RuntimeError(
                "Changes must be committed before pushing."
            )

        if not self.state.target_branch:
            raise RuntimeError(
                "Target branch is not available."
            )

        self.git_tool.push_changes(self.state.target_branch)

        self.state.pushed = True

        return self.state.target_branch

    def prepare_pull_request(self) -> dict[str, str]:
        """Prepare the information required to create a pull request."""
        if not self.state.pushed:
            raise RuntimeError(
                "Changes must be pushed before creating a pull request."
            )

        if not self.state.target_branch:
            raise RuntimeError(
                "Target branch is not available."
            )

        if not self.state.base_branch:
            raise RuntimeError(
                "Base branch is not available."
            )

        if not self.state.commit_message:
            raise RuntimeError(
                "Commit message is not available."
            )

        return {
            "source_branch": self.state.target_branch,
            "target_branch": self.state.base_branch,
            "title": self.state.commit_message,
        }