from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from utils.logger import logger
from models.git_status import GitStatus
from pathlib import Path


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
        return self.repo is not None

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

    def get_all_changed_files(self) -> list[str]:
        try:
            all_files = set(self.get_modified_files() + self.get_staged_files() + self.get_untracked_files())
            changed_files = sorted(all_files)
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

    def get_modified_files(self) -> list[str]:
        try:
            modified_files = [item.a_path for item in self.repo.index.diff(None)]
            logger.info(f"Modified files: {modified_files}")
            return modified_files
        
        except Exception as error:
            logger.error(f"Failed to get modified files: {error}")
            raise

    def get_staged_files(self) -> list[str]:
        try:
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            logger.info(f"Staged files: {staged_files}")
            return staged_files

        except Exception as error:
            logger.error(f"Failed to get staged files: {error}")
            raise

    def get_untracked_files(self) -> list[str]:
        try:
            untracked_files = self.repo.untracked_files
            logger.info(f"Untracked files: {untracked_files}")
            return untracked_files

        except Exception as error:
            logger.error(f"Failed to get untracked files: {error}")
            raise

    # ==========================================================
    # Commit
    # ==========================================================

    def commit_changes(self, message: str) -> str:
        try:
            if not isinstance(message, str):
                raise ValueError(
                    "Commit message must be a string."
                )

            if not message.strip():
                raise ValueError(
                    "Commit message cannot be empty."
                )

            message = message.strip()

            staged_changes = self.repo.git.diff(
                "--cached",
                "--name-only"
            ).splitlines()

            if not staged_changes:
                raise RuntimeError(
                    "No staged changes to commit."
                )

            commit = self.repo.index.commit(message)

            logger.info(
                f"Commit created successfully: "
                f"{commit.hexsha[:8]} - {message}"
            )

            return commit.hexsha

        except Exception as error:
            logger.error(
                f"Failed to commit changes: {error}"
            )
            raise

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

    def checkout_branch(self, branch_name: str) -> str:
        try:
            # Validate the branch name before checking it out
            self.validate_branch_name(branch_name)

            # Check if the branch exists
            if not self.is_branch_exists(branch_name):
                raise ValueError(f"Branch '{branch_name}' does not exist.")

            # Check Uncommitted changes before switching branches
            if self.has_uncommitted_changes():
                raise RuntimeError(
                    "Cannot checkout branch because the repository "
                    "contains uncommitted changes."
                )

            # Checkout the branch
            branch = self.repo.branches[branch_name]
            branch.checkout()
            logger.info(f"Checked out to branch '{branch_name}' successfully.")

            return branch_name

        except Exception as error:
            logger.error(f"Failed to checkout branch '{branch_name}': {error}")
            raise

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

    def pull_changes(
        self,
        remote: str = "origin",
        branch_name: str | None = None,
) -> str:
        try:
            # Validate remote
            if not remote or not remote.strip():
                raise ValueError(
                    "Remote name cannot be empty."
                )

            remote = remote.strip()

            # Check if remote exists
            if remote not in self.repo.remotes:
                raise ValueError(
                    f"Remote '{remote}' does not exist."
                )

            # Use current branch when branch is not provided
            if branch_name is None:
                branch_name = self.get_current_branch()
            else:
                branch_name = branch_name.strip()

                # Validate branch name
                self.validate_branch_name(branch_name)

            # Check if branch exists
            if not self.is_branch_exists(branch_name):
                raise ValueError(
                    f"Branch '{branch_name}' does not exist."
                )

            # Ensure requested branch is currently checked out
            current_branch = self.get_current_branch()

            if current_branch != branch_name:
                raise ValueError(
                    f"Branch '{branch_name}' is not the "
                    f"current branch. Current branch: "
                    f"'{current_branch}'."
                )

            # Pull changes
            remote_repo = self.repo.remote(remote)
            remote_repo.pull()

            logger.info(
                f"Successfully pulled changes for "
                f"branch '{branch_name}' from '{remote}'."
            )

            return branch_name

        except Exception as error:
            logger.error(
                f"Failed to pull branch "
                f"'{branch_name}' from '{remote}': {error}"
            )
            raise
        
    def push_changes(
        self,
        remote: str = "origin",
        branch_name: str | None = None,
) -> str:
        try:
            # Validate remote
            if not remote or not remote.strip():
                raise ValueError(
                    "Remote name cannot be empty."
                )

            remote = remote.strip()

            # Check if remote exists
            if remote not in self.repo.remotes:
                raise ValueError(
                    f"Remote '{remote}' does not exist."
                )

            # Use current branch when branch is not provided
            if branch_name is None:
                branch_name = self.get_current_branch()
            else:
                branch_name = branch_name.strip()
                # Validate branch name
                self.validate_branch_name(branch_name)

            # Check if branch exists
            if not self.is_branch_exists(branch_name):
                raise ValueError(
                    f"Branch '{branch_name}' does not exist."
                )

            # Push changes
            remote_repo = self.repo.remote(remote)

            push_results = remote_repo.push(
                branch_name,
                set_upstream=True
            )

            # Verify push result
            for push_result in push_results:
                if push_result.flags & push_result.ERROR:
                    raise RuntimeError(
                        f"Push failed: {push_result.summary}"
                    )

            logger.info(
                f"Successfully pushed branch "
                f"'{branch_name}' to remote '{remote}'."
            )

            return branch_name

        except Exception as error:
            logger.error(
                f"Failed to push branch "
                f"'{branch_name}' to '{remote}': {error}"
            )
            raise


    # ==========================================================
    # Merge
    # ==========================================================

    def merge_branch(
        self,
        source_branch: str,
        target_branch: str
) -> str:
        try:
            self.validate_branch_name(source_branch)
            self.validate_branch_name(target_branch)

            if source_branch == target_branch:
                raise ValueError(
                    "Source and target branches cannot be the same."
                )

            if not self.is_branch_exists(source_branch):
                raise ValueError(
                    f"Source branch '{source_branch}' does not exist."
                )

            if not self.is_branch_exists(target_branch):
                raise ValueError(
                    f"Target branch '{target_branch}' does not exist."
                )

            # Prevent merge when repository has uncommitted changes
            if self.has_uncommitted_changes():
                raise RuntimeError(
                    "Cannot merge branches because the repository "
                    "contains uncommitted changes."
                )

            current_branch = self.get_current_branch()

            if current_branch != target_branch:
                self.checkout_branch(target_branch)

            try:
                self.repo.git.merge(source_branch)

            except Exception as error:
                conflicts = self.merge_conflicts()

                if conflicts:
                    logger.error(
                        f"Merge conflicts detected: {conflicts}"
                    )
                    raise RuntimeError(
                        f"Merge failed due to conflicts: {conflicts}"
                    ) from error

                raise

            logger.info(
                f"Successfully merged '{source_branch}' "
                f"into '{target_branch}'."
            )

            return target_branch

        except Exception as error:
            logger.error(
                f"Failed to merge '{source_branch}' "
                f"into '{target_branch}': {error}"
            )
            raise

    def merge_conflicts(self) -> list[str]:
        try:
            conflicts = list(
                self.repo.index.unmerged_blobs().keys()
            )

            if conflicts:
                logger.warning(
                    f"Merge conflicts detected: {conflicts}"
                )
            else:
                logger.info(
                    "No merge conflicts detected."
                )

            return conflicts

        except Exception as error:
            logger.error(
                f"Failed to detect merge conflicts: {error}"
            )
            raise

    # ==========================================================
    # Stash
    # ==========================================================

    def validate_stash_index(self, stash_index: int) -> bool:
        try:
            if not isinstance(stash_index, int):
                raise ValueError(
                    "Stash index must be an integer."
                )

            if stash_index < 0:
                raise ValueError(
                    "Stash index cannot be negative."
                )

            stashes = self.do_stash_list()

            if stash_index >= len(stashes):
                raise ValueError(
                    f"Stash index '{stash_index}' does not exist."
                )

            logger.info(
                f"Stash index '{stash_index}' is valid."
            )

            return True

        except ValueError:
            raise

        except Exception as error:
            logger.error(
                f"Failed to validate stash index "
                f"'{stash_index}': {error}"
            )
            raise

    def do_stash_changes(self) -> str:
        try:
            if not self.has_uncommitted_changes():
                logger.info(
                    "No uncommitted changes available to stash."
                )
                raise RuntimeError(
                    "No uncommitted changes available to stash."
                )

            result = self.repo.git.stash("push")

            logger.info(
                "Changes successfully stashed."
            )

            return result

        except Exception as error:
            logger.error(
                f"Failed to stash changes: {error}"
            )
            raise

    def do_stash_list(self) -> list[str]:
        try:
            stashes = list(
                self.repo.git.stash(
                    "list"
                ).splitlines()
            )

            logger.info(
                f"Available stashes: {len(stashes)}"
            )

            return stashes

        except Exception as error:
            logger.error(
                f"Failed to retrieve stash list: {error}"
            )
            raise

    def do_stash_apply(
        self,
        stash_index: int = 0
    ) -> str:
        try:
            self.validate_stash_index(stash_index)
            stash_reference = f"stash@{{{stash_index}}}"

            self.repo.git.stash(
                "apply",
                stash_reference
            )

            logger.info(
                f"Applied stash '{stash_reference}'."
            )

            return stash_reference

        except Exception as error:
            logger.error(
                f"Failed to apply stash: {error}"
            )
            raise

    def do_stash_pop(self) -> str:
        try:
            stashes = self.do_stash_list()

            if not stashes:
                raise RuntimeError(
                    "No stashes available to pop."
                )

            result = self.repo.git.stash("pop")

            logger.info(
                "Latest stash successfully popped."
            )

            return result

        except Exception as error:
            logger.error(
                f"Failed to pop stash: {error}"
            )
            raise

    def do_stash_drop(self, stash_index: int = 0) -> str:
        try:
            self.validate_stash_index(stash_index)

            stash_reference = f"stash@{{{stash_index}}}"

            self.repo.git.stash("drop", stash_reference)

            logger.info(
                f"Dropped stash '{stash_reference}'."
            )

            return stash_reference

        except Exception as error:
            logger.error(
                f"Failed to drop stash '{stash_index}': {error}"
            )
            raise

    # ==========================================================
    # Reset
    # ==========================================================

    def validate_commit_reference(self, commit_reference: str) -> bool:
        try:
            if not commit_reference or not commit_reference.strip():
                raise ValueError(
                    "Commit reference cannot be empty."
                )

            commit_reference = commit_reference.strip()

            # Verify that the reference resolves to a valid commit
            self.repo.commit(commit_reference)
            logger.info(
                f"Commit reference '{commit_reference}' is valid."
            )
            return True

        except ValueError:
            raise

        except Exception as error:
            logger.error(
                f"Invalid commit reference '{commit_reference}': {error}"
            )
            raise ValueError(
                f"Invalid commit reference: '{commit_reference}'."
            ) from error

    def validate_reset_target(self, commit_reference: str) -> bool:
        self.validate_commit_reference(commit_reference)

        target_commit = self.repo.commit(
            commit_reference
        )

        current_commit = self.repo.head.commit

        if target_commit.hexsha == current_commit.hexsha:
            raise ValueError(
                "Reset target is already the current HEAD."
            )

        logger.info(
            f"Reset target '{commit_reference}' is valid."
        )

        return True

    def do_soft_reset(self, commit_reference: str) -> str:
        try:
            self.validate_reset_target(commit_reference)
            commit_reference = commit_reference.strip()

            self.repo.git.reset(
                "--soft",
                commit_reference
            )

            logger.info(
                f"Soft reset performed to commit "
                f"'{commit_reference}'."
            )

            return commit_reference

        except Exception as error:
            logger.error(
                f"Failed to perform soft reset: {error}"
            )
            raise

    def do_hard_reset(self, commit_reference: str) -> str:
        try:
            self.validate_reset_target(commit_reference)
            commit_reference = commit_reference.strip()

            self.repo.git.reset(
                "--hard",
                commit_reference
            )

            logger.warning(
                f"Hard reset performed to commit "
                f"'{commit_reference}'."
            )

            return commit_reference

        except Exception as error:
            logger.error(
                f"Failed to perform hard reset: {error}"
            )
            raise

    # ==========================================================
    # Staging Operations
    # ==========================================================

    def add_all_changes(self) -> list[str]:
        try:
            changed_files = self.get_all_changed_files()

            if not changed_files:
                logger.info("No changes to stage.")
                return []

            self.repo.git.add(A=True)
            logger.info(f"Staged all changes: {changed_files}")

            return changed_files

        except Exception as error:
            logger.error(f"Failed to stage all changes: {error}")
            raise

    def add_file(self, files: list[str]) -> list[str]:
        try:
            if not isinstance(files, list) or not files:
                raise ValueError(
                    "Files must be provided as a non-empty list."
                )

            if not all(isinstance(file, str) for file in files):
                raise ValueError(
                    "All file names must be strings."
                )

            files = [file.strip() for file in files]

            if any(not file for file in files):
                raise ValueError(
                    "File names cannot be empty."
                )

            files = list(dict.fromkeys(files))

            changed_files = self.get_all_changed_files()

            invalid_files = [
                file
                for file in files
                if file not in changed_files
            ]

            if invalid_files:
                raise ValueError(
                    f"The following files have no changes to stage: "
                    f"{invalid_files}"
                )

            self.repo.index.add(files)

            logger.info(
                f"Successfully staged files: {files}"
            )

            return files

        except Exception as error:
            logger.error(
                f"Failed to stage files {files}: {error}"
            )
            raise