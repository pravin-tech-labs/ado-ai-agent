import pytest
from git import Repo


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