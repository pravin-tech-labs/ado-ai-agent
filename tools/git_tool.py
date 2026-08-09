from typing import List, Optional
from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from utils.logger import logger
from models.git_status import GitStatus


class GitTool:
    """
    Wrapper around Git operations.

    The AI Agent should always interact with Git through this class
    instead of calling GitPython directly.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.repo = None
        
        try:
            self.repo = Repo(repo_path)
            logger.info(f"Git repository initialized: {repo_path}")

        except InvalidGitRepositoryError:
            logger.error(f"Invalid Git repository: {repo_path}")
            raise

        except NoSuchPathError:
            logger.error(f"Repository path does not exist: {repo_path}")
            raise

    # ==========================================================
    # Repository
    # ==========================================================

    def is_git_repository(self) -> bool:
        try:
            return self.repo is not None
        except (InvalidGitRepositoryError, NoSuchPathError):
            return False

    def get_repository_root(self) -> str:
        pass

    def get_status(self) -> str:
        try:
            status = self.repo.git.status()
            logger.info(f"Repository status:\n{status}")
            return status
        except Exception as error:
            logger.error(f"Error occurred while fetching repository status: {error}")
            raise

    def get_current_branch(self) -> str:
        try:
            branch_name = self.repo.active_branch.name
            logger.info(f"Current branch: {branch_name}")
            return branch_name
        
        except Exception as error:
            logger.error(f"Error occurred while fetching current branch: {error}")
            raise 

    def get_repository_status(self) -> GitStatus:
        try:
            branch = self.get_current_branch()
            modified_files = self.get_modified_files()
            staged_files = self.get_staged_files()
            untracked_files = self.get_untracked_files()

            git_status = GitStatus(
                branch=branch,
                modified_files=modified_files,
                staged_files=staged_files,
                untracked_files=untracked_files,
            )

            logger.info(f"Repository status: {git_status}")
            return git_status

        except Exception as error:
            logger.error(f"Error occurred while fetching repository status: {error}")
            raise

    def get_all_changed_files(self) -> List[str]:
        try:
            all_files = set(self.get_modified_files() + self.get_staged_files() + self.get_untracked_files())
            changed_files = list(all_files)
            logger.info(f"All changed files: {changed_files}")
            return changed_files

        except Exception as error:
            logger.error(f"Failed to get all changed files: {error}")
            raise

    # ==========================================================
    # Changes
    # ==========================================================

    def has_uncommitted_changes(self) -> bool:
        try:
            has_changes = self.repo.is_dirty(untracked_files=True)
            logger.info(f"Repository has uncommitted changes: {has_changes}")
            return has_changes

        except Exception as error:
            logger.error(f"Failed to check repository changes: {error}")
            raise

    def get_modified_files(self) -> List[str]:
        try:
            modified_files = [item.a_path for item in self.repo.index.diff(None)]
            logger.info(f"Modified files: {modified_files}")
            return modified_files
        
        except Exception as error:
            logger.error(f"Failed to get modified files: {error}")
            raise

    def get_staged_files(self) -> List[str]:
        try:
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            logger.info(f"Staged files: {staged_files}")
            return staged_files

        except Exception as error:
            logger.error(f"Failed to get staged files: {error}")
            raise

    def get_untracked_files(self) -> List[str]:
        try:
            untracked_files = self.repo.untracked_files
            logger.info(f"Untracked files: {untracked_files}")
            return untracked_files

        except Exception as error:
            logger.error(f"Failed to get untracked files: {error}")
            raise

    def get_diff(self) -> str:
        pass

    def get_staged_diff(self) -> str:
        pass

    # ==========================================================
    # Staging
    # ==========================================================

    def stage_file(self, file_path: str):
        pass

    def stage_files(self, files: List[str]):
        pass

    def stage_all_changes(self):
        pass

    def unstage_file(self, file_path: str):
        pass

    # ==========================================================
    # Commit
    # ==========================================================

    def commit(self, message: str):
        pass

    def amend_last_commit(self):
        pass

    def get_latest_commit(self) -> str:
        pass

    def get_commit_history(self, limit: int = 10):
        pass

    # ==========================================================
    # Branch
    # ==========================================================

    def create_branch(self, branch_name: str) -> str:
        try:
            # Validate the branch name before creating it
            self.validate_branch_name(branch_name)

            # Check if the branch already exists
            if self.is_branch_exists(branch_name):
                raise ValueError(f"Branch '{branch_name}' already exists.")

            # Create the new branch
            new_branch = self.repo.create_head(branch_name)

            # Checkout the new branch
            new_branch.checkout()

            logger.info(f"Branch '{branch_name}' created successfully.")
            return new_branch.name

        except Exception as error:
            logger.error(f"Failed to create branch '{branch_name}': {error}")
            raise

    def checkout_branch(self, branch_name: str):
        try:
            # Validate the branch name before checking it out
            self.validate_branch_name(branch_name)

            # Check if the branch exists
            if not self.is_branch_exists(branch_name):
                raise ValueError(f"Branch '{branch_name}' does not exist.")

            # Checkout the branch
            branch = self.repo.branches[branch_name]
            branch.checkout()
            logger.info(f"Checked out to branch '{branch_name}' successfully.")

        except Exception as error:
            logger.error(f"Failed to checkout branch '{branch_name}': {error}")
            raise

    def delete_branch(self, branch_name: str):
        pass

    def get_all_branches(self) -> List[str]:
        pass

    def is_branch_exists(self, branch_name: str) -> bool:
        try:
            exists = branch_name in [branch.name for branch in self.repo.branches]
            logger.info(f"Branch '{branch_name}' exists: {exists}")
            return exists
        
        except Exception as error:
            logger.error(f"Failed to check if branch exists: {error}")
            raise

    def validate_branch_name(self, branch_name: str) -> bool:
        if not branch_name or not branch_name.strip():
            raise ValueError(
                "Branch name cannot be empty."
            )

        if branch_name.startswith("/") or branch_name.endswith("/"):
            raise ValueError(
                "Branch name cannot start or end with '/'."
            )

        if "//" in branch_name:
            raise ValueError(
                "Branch name cannot contain consecutive '/'."
            )

        if " " in branch_name:
            raise ValueError(
                "Branch name cannot contain spaces."
            )

        if "\\" in branch_name:
            raise ValueError(
                "Branch name cannot contain '\\'."
            )
        
        logger.info(
            f"Branch name '{branch_name}' is valid."
        )
        return True

    # ==========================================================
    # Remote
    # ==========================================================

    def fetch(self):
        pass

    def pull(
        self,
        remote: str = "origin",
        branch_name: Optional[str] = None,
    ):
        pass

    def push(
        self,
        remote: str = "origin",
        branch_name: Optional[str] = None,
    ):
        pass

    # ==========================================================
    # Merge
    # ==========================================================

    def merge_branch(self, source_branch: str):
        pass

    def has_merge_conflicts(self) -> bool:
        pass

    # ==========================================================
    # Stash
    # ==========================================================

    def stash(self):
        pass

    def stash_list(self):
        pass

    def stash_apply(self, stash_index: int = 0):
        pass

    def stash_pop(self):
        pass

    def stash_drop(self, stash_index: int = 0):
        pass

    # ==========================================================
    # Reset
    # ==========================================================

    def soft_reset(self, commit_hash: str):
        pass

    def hard_reset(self, commit_hash: str):
        pass