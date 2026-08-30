from tools.git_tool import GitTool

git_tool = GitTool()

print(f"Checking Test Push")
print(f"Staged changes: {git_tool.add_all_changes()}")
print(f"Committed changes: {git_tool.commit_changes('Implemented commit operation')}")