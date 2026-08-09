from tools.git_tool import GitTool

git_tool = GitTool()
new_branch = git_tool.create_branch("feature/ado")
print(f"Created branch: {new_branch}")
print(f"Current branch: {git_tool.get_current_branch()}")