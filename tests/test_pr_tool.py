import pytest

from tools.pr_tool import PRTool


def test_pr_tool_cannot_be_instantiated():
    with pytest.raises(TypeError):
        PRTool()