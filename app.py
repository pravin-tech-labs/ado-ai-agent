from tools.git_tool import GitTool

git_tool = GitTool()

status = git_tool.get_repository_status()

print(git_tool.get_all_changed_files())