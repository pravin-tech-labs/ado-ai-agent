from tools.git_tool import GitTool

git_tool = GitTool()

merged_branch = git_tool.merge_branch("test-branch", "main")
print(f"Merged branch: {merged_branch}")