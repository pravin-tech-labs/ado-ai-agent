from tools.git_tool import GitTool

git_tool = GitTool()

pushed_branch = git_tool.push_changes()
print(f"Pushed branch: {pushed_branch}")