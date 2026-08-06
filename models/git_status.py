from dataclasses import dataclass

@dataclass
class GitStatus:

    branch: str
    modified_files: list[str]
    staged_files: list[str]
    untracked_files: list[str]

    @property
    def has_changes(self) -> bool:
        return bool(self.modified_files or self.staged_files or self.untracked_files)