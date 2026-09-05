import pytest
from git import Repo

from tools.git_tool import GitTool


@pytest.fixture
def temp_repo(tmp_path):
    repo = Repo.init(tmp_path)

    # Configure Git identity for the temporary test repository
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")

    test_file = tmp_path / "test.txt"
    test_file.write_text("initial content")

    repo.index.add(["test.txt"])
    repo.index.commit("Initial commit")

    return tmp_path

@pytest.fixture
def temp_remote(tmp_path):
    remote_path = tmp_path / "remote.git"
    Repo.init(remote_path, bare=True)

    return remote_path

def test_git_repository_initialization():
    git_tool = GitTool(".")

    assert git_tool.is_git_repository() is True


def test_get_current_branch():
    git_tool = GitTool(".")

    branch = git_tool.get_current_branch()

    assert isinstance(branch, str)
    assert branch != ""


def test_get_repository_status():
    git_tool = GitTool(".")

    status = git_tool.get_repository_status()

    assert status.branch != ""
    assert isinstance(status.modified_files, list)
    assert isinstance(status.staged_files, list)
    assert isinstance(status.untracked_files, list)


def test_get_all_changed_files():
    git_tool = GitTool(".")

    changed_files = git_tool.get_all_changed_files()

    assert isinstance(changed_files, list)
    assert changed_files == sorted(changed_files)
    assert len(changed_files) == len(set(changed_files))

def test_add_file(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("updated content")

    staged_files = git_tool.add_file(["test.txt"])

    assert staged_files == ["test.txt"]
    assert git_tool.get_staged_files() == ["test.txt"]

def test_add_all_changes(temp_repo):
    git_tool = GitTool(temp_repo)

    modified_file = temp_repo / "test.txt"
    modified_file.write_text("updated content")

    new_file = temp_repo / "new_file.txt"
    new_file.write_text("new content")

    changed_files = git_tool.add_all_changes()

    assert "test.txt" in changed_files
    assert "new_file.txt" in changed_files

    staged_files = git_tool.get_staged_files()

    assert "test.txt" in staged_files
    assert "new_file.txt" in staged_files

def test_commit_changes(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("updated content")

    git_tool.add_file(["test.txt"])

    commit_sha = git_tool.commit_changes("Update test file")

    assert isinstance(commit_sha, str)
    assert len(commit_sha) == 40

    latest_commit = git_tool.repo.head.commit

    assert latest_commit.hexsha == commit_sha
    assert latest_commit.message.strip() == "Update test file"

def test_create_branch(temp_repo):
    git_tool = GitTool(temp_repo)

    branch_name = git_tool.create_branch("feature/test-branch")

    assert branch_name == "feature/test-branch"
    assert git_tool.get_current_branch() == "feature/test-branch"
    assert git_tool.is_branch_exists("feature/test-branch") is True

def test_checkout_branch(temp_repo):
    git_tool = GitTool(temp_repo)

    git_tool.create_branch("feature/test-branch")
    git_tool.checkout_branch("master")

    assert git_tool.get_current_branch() == "master"

def test_checkout_branch_with_uncommitted_changes(temp_repo):
    git_tool = GitTool(temp_repo)

    git_tool.create_branch("feature/test-branch")

    test_file = temp_repo / "test.txt"
    test_file.write_text("uncommitted change")

    with pytest.raises(RuntimeError, match="uncommitted changes"):
        git_tool.checkout_branch("master")

def test_do_stash_changes(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("temporary change")

    stash_result = git_tool.do_stash_changes()

    assert isinstance(stash_result, str)
    assert git_tool.has_uncommitted_changes() is False
    assert len(git_tool.do_stash_list()) == 1

def test_stash_apply_and_drop(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("temporary change")

    git_tool.do_stash_changes()

    assert len(git_tool.do_stash_list()) == 1

    stash_reference = git_tool.do_stash_apply(0)

    assert stash_reference == "stash@{0}"
    assert test_file.read_text() == "temporary change"

    git_tool.do_stash_drop(0)

    assert git_tool.do_stash_list() == []

def test_do_stash_pop(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("temporary change")

    git_tool.do_stash_changes()

    assert git_tool.do_stash_list() != []

    git_tool.do_stash_pop()

    assert test_file.read_text() == "temporary change"
    assert git_tool.do_stash_list() == []

def test_do_soft_reset(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"

    # Create second commit
    test_file.write_text("second commit")
    git_tool.add_file(["test.txt"])
    second_commit = git_tool.commit_changes("Second commit")

    # Get the initial commit
    initial_commit = git_tool.repo.git.rev_parse("HEAD~1")

    # Perform soft reset
    reset_target = git_tool.do_soft_reset(initial_commit)

    assert reset_target == initial_commit
    assert git_tool.repo.head.commit.hexsha == initial_commit

    # Soft reset keeps the changes staged
    assert "test.txt" in git_tool.get_staged_files()

def test_do_hard_reset(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"

    # Create second commit
    test_file.write_text("second commit")
    git_tool.add_file(["test.txt"])
    git_tool.commit_changes("Second commit")

    initial_commit = git_tool.repo.git.rev_parse("HEAD~1")

    # Perform hard reset
    reset_target = git_tool.do_hard_reset(initial_commit)

    assert reset_target == initial_commit
    assert git_tool.repo.head.commit.hexsha == initial_commit

    # Verify second commit's content is removed
    assert test_file.read_text() == "initial content"

    # Repository should be clean
    assert git_tool.has_uncommitted_changes() is False

def test_merge_branch(temp_repo):
    git_tool = GitTool(temp_repo)

    current_branch = git_tool.get_current_branch()

    # Create feature branch
    git_tool.create_branch("feature/merge-test")

    # Make a change on feature branch
    test_file = temp_repo / "test.txt"
    test_file.write_text("feature change")

    git_tool.add_file(["test.txt"])
    git_tool.commit_changes("Feature change")

    # Switch back to original branch
    git_tool.checkout_branch(current_branch)

    # Merge feature branch
    merged_branch = git_tool.merge_branch(
        "feature/merge-test",
        current_branch
    )

    assert merged_branch == current_branch
    assert git_tool.get_current_branch() == current_branch
    assert test_file.read_text() == "feature change"
    assert git_tool.merge_conflicts() == []

def test_merge_branch_with_conflict(temp_repo):
    git_tool = GitTool(temp_repo)

    current_branch = git_tool.get_current_branch()

    # Create feature branch
    git_tool.create_branch("feature/conflict-test")

    test_file = temp_repo / "test.txt"
    test_file.write_text("feature change")

    git_tool.add_file(["test.txt"])
    git_tool.commit_changes("Feature change")

    # Switch back to main
    git_tool.checkout_branch(current_branch)

    # Make a conflicting change on main
    test_file.write_text("main change")

    git_tool.add_file(["test.txt"])
    git_tool.commit_changes("Main change")

    # Merge should fail because both branches changed the same line
    with pytest.raises(RuntimeError, match="conflicts"):
        git_tool.merge_branch(
            "feature/conflict-test",
            current_branch
        )

    conflicts = git_tool.merge_conflicts()

    assert "test.txt" in conflicts

def test_commit_changes_with_empty_message(temp_repo):
    git_tool = GitTool(temp_repo)

    with pytest.raises(ValueError, match="Commit message cannot be empty"):
        git_tool.commit_changes("   ")


def test_commit_changes_without_staged_changes(temp_repo):
    git_tool = GitTool(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    with pytest.raises(RuntimeError, match="No staged changes to commit"):
        git_tool.commit_changes("Should fail")


def test_create_branch_with_invalid_name(temp_repo):
    git_tool = GitTool(temp_repo)

    with pytest.raises(ValueError, match="Branch name cannot contain spaces"):
        git_tool.create_branch("feature test")


def test_checkout_non_existing_branch(temp_repo):
    git_tool = GitTool(temp_repo)

    with pytest.raises(ValueError, match="does not exist"):
        git_tool.checkout_branch("feature/not-found")

def test_stash_changes_without_changes(temp_repo):
    git_tool = GitTool(temp_repo)

    with pytest.raises(RuntimeError, match="No uncommitted changes"):
        git_tool.do_stash_changes()


def test_stash_apply_with_invalid_index(temp_repo):
    git_tool = GitTool(temp_repo)

    with pytest.raises(ValueError, match="does not exist"):
        git_tool.do_stash_apply(0)


def test_stash_drop_with_invalid_index(temp_repo):
    git_tool = GitTool(temp_repo)

    with pytest.raises(ValueError, match="does not exist"):
        git_tool.do_stash_drop(0)


def test_reset_with_invalid_commit_reference(temp_repo):
    git_tool = GitTool(temp_repo)

    with pytest.raises(ValueError, match="Invalid commit reference"):
        git_tool.do_soft_reset("invalid-commit")

def test_push_changes(temp_repo, temp_remote):
    git_tool = GitTool(temp_repo)

    git_tool.repo.create_remote(
        "origin",
        temp_remote.as_uri()
    )

    current_branch = git_tool.get_current_branch()

    test_file = temp_repo / "test.txt"
    test_file.write_text("push test")

    git_tool.add_file(["test.txt"])
    git_tool.commit_changes("Test push")

    result = git_tool.push_changes()

    assert result == current_branch

def test_pull_changes(temp_repo, temp_remote):
    git_tool = GitTool(temp_repo)

    git_tool.repo.create_remote(
        "origin",
        temp_remote.as_uri()
    )

    current_branch = git_tool.get_current_branch()

    # Push initial repository state
    git_tool.push_changes()

    # Clone the remote into another temporary repository
    clone_path = temp_repo.parent / "clone"
    clone_repo = Repo.clone_from(
        temp_remote.as_uri(),
        clone_path,
        branch=current_branch
    )

    # Make a change in the cloned repository
    clone_file = clone_path / "test.txt"
    clone_file.write_text("remote change")

    clone_repo.index.add(["test.txt"])
    clone_repo.index.commit("Remote change")

    clone_repo.git.push(
        "origin",
        current_branch
    )

    # Pull the remote change into the original repository
    result = git_tool.pull_changes()

    assert result == current_branch
    assert (temp_repo / "test.txt").read_text() == "remote change"