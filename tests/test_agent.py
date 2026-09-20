import pytest

from agent.agent import Agent
from agent.actions import AgentAction

def test_agent_inspect_repository(temp_repo):
    agent = Agent(temp_repo)

    state = agent.inspect_repository()

    assert state.current_branch == "master"
    assert state.changed_files == []

def test_agent_inspect_repository_with_changes(temp_repo):
    agent = Agent(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    state = agent.inspect_repository()

    assert state.current_branch
    assert "test.txt" in state.changed_files
    assert state.committed is False
    assert state.pushed is False
    assert state.pr_created is False

def test_agent_decides_no_action_for_clean_repository(temp_repo):
    agent = Agent(temp_repo)

    agent.inspect_repository()

    action = agent.determine_next_action()

    assert action == AgentAction.NO_ACTION


def test_agent_decides_create_branch_for_repository_changes(temp_repo):
    agent = Agent(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()

    action = agent.determine_next_action()

    assert action == AgentAction.CREATE_BRANCH

def test_agent_decides_create_branch_on_base_branch(temp_repo):
    agent = Agent(temp_repo)

    agent.state.base_branch = agent.state.current_branch

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()

    action = agent.determine_next_action()

    assert action == AgentAction.CREATE_BRANCH


def test_agent_decides_stage_changes_on_feature_branch(temp_repo):
    agent = Agent(temp_repo)

    agent.state.base_branch = "main"

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()

    agent.state.current_branch = "feature/login-fix"

    action = agent.determine_next_action()

    assert action == AgentAction.STAGE_CHANGES

def test_generate_branch_name(temp_repo):
    agent = Agent(temp_repo)

    branch_name = agent.generate_branch_name(
        "Fix Login Validation"
    )

    assert branch_name == "feature/fix-login-validation"


def test_generate_branch_name_with_special_characters(temp_repo):
    agent = Agent(temp_repo)

    branch_name = agent.generate_branch_name(
        "Fix login: validation & timeout!"
    )

    assert branch_name == "feature/fix-login-validation-timeout"


def test_generate_branch_name_with_empty_description(temp_repo):
    agent = Agent(temp_repo)

    with pytest.raises(
        ValueError,
        match="Task description cannot be empty"
    ):
        agent.generate_branch_name("   ")

def test_create_feature_branch_updates_agent_state(temp_repo):
    agent = Agent(temp_repo)
    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()

    branch_name = agent.create_feature_branch(
        "Add login tests"
    )

    assert branch_name == "feature/add-login-tests"
    assert agent.state.target_branch == branch_name
    assert agent.state.current_branch == branch_name
    assert agent.git_tool.get_current_branch() == branch_name

def test_create_feature_branch_preserves_changes(temp_repo):
    agent = Agent(temp_repo)
    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()
    agent.create_feature_branch("Preserve local changes")

    assert "test.txt" in agent.git_tool.get_all_changed_files()

def test_create_feature_branch_requires_changes(temp_repo):
    agent = Agent(temp_repo)
    agent.inspect_repository()
    with pytest.raises(RuntimeError):
        agent.create_feature_branch("Add login tests")

def test_create_feature_branch_rejects_empty_description(temp_repo):
    agent = Agent(temp_repo)
    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()

    with pytest.raises(ValueError):
        agent.create_feature_branch("")

    assert agent.state.target_branch == ""

def test_stage_changes_stages_detected_files(temp_repo):
    agent = Agent(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()
    agent.create_feature_branch("Stage changes")
    
    staged_files = agent.stage_changes()

    assert "test.txt" in staged_files

    status = agent.git_tool.get_repository_status()

    assert "test.txt" in status.staged_files
    assert "test.txt" not in status.modified_files

def test_stage_changes_requires_changed_files(temp_repo):
    agent = Agent(temp_repo)
    agent.inspect_repository()

    with pytest.raises(RuntimeError):
        agent.stage_changes()

def test_commit_changes_updates_agent_state(temp_repo):
    agent = Agent(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()
    agent.create_feature_branch("Commit changes")
    agent.stage_changes()

    commit_message = agent.commit_changes(
        "Add updated test content"
    )

    assert commit_message == "Add updated test content"
    assert agent.state.commit_message == "Add updated test content"
    assert agent.state.committed is True

    assert not agent.git_tool.get_staged_files()


def test_commit_changes_requires_staged_files(temp_repo):
    agent = Agent(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()
    agent.create_feature_branch("Commit without staging")

    with pytest.raises(RuntimeError):
        agent.commit_changes("Commit changes")

    assert agent.state.committed is False


def test_commit_changes_rejects_empty_message(temp_repo):
    agent = Agent(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()
    agent.create_feature_branch("Empty commit message")
    agent.stage_changes()

    with pytest.raises(ValueError):
        agent.commit_changes("")

    assert agent.state.committed is False

def test_push_changes_requires_commit(temp_repo):
    agent = Agent(temp_repo)

    test_file = temp_repo / "test.txt"
    test_file.write_text("modified content")

    agent.inspect_repository()
    agent.create_feature_branch("Push changes")

    with pytest.raises(RuntimeError):
        agent.push_changes()

    assert agent.state.pushed is False


def test_push_changes_requires_target_branch(temp_repo):
    agent = Agent(temp_repo)

    agent.state.committed = True

    with pytest.raises(RuntimeError):
        agent.push_changes()

    assert agent.state.pushed is False

def test_prepare_pull_request_returns_pr_details(temp_repo):
    agent = Agent(temp_repo)

    agent.state.base_branch = "main"
    agent.state.target_branch = "feature/add-login-tests"
    agent.state.commit_message = "Add login tests"
    agent.state.pushed = True

    pr_details = agent.prepare_pull_request()

    assert pr_details == {
        "source_branch": "feature/add-login-tests",
        "target_branch": "main",
        "title": "Add login tests",
    }


def test_prepare_pull_request_requires_push(temp_repo):
    agent = Agent(temp_repo)

    agent.state.target_branch = "feature/add-login-tests"
    agent.state.base_branch = "main"
    agent.state.commit_message = "Add login tests"

    with pytest.raises(RuntimeError):
        agent.prepare_pull_request()


def test_prepare_pull_request_requires_target_branch(temp_repo):
    agent = Agent(temp_repo)

    agent.state.base_branch = "main"
    agent.state.commit_message = "Add login tests"
    agent.state.pushed = True

    with pytest.raises(RuntimeError):
        agent.prepare_pull_request()