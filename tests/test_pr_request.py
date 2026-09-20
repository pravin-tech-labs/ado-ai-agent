from models.pr_request import PullRequestRequest


def test_pull_request_request_defaults_description():
    request = PullRequestRequest(
        source_branch="feature/login-tests",
        target_branch="main",
        title="Add login tests",
    )

    assert request.source_branch == "feature/login-tests"
    assert request.target_branch == "main"
    assert request.title == "Add login tests"
    assert request.description == ""