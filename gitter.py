import git
import os

def list_files_recursive(directory):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.relpath(os.path.join(root, file), start=directory))
    return file_list


repo_path = '.'
repo = git.Repo(repo_path)

# Get the set of files currently in the working directory and its subdirectories
# current_files = set(list_files_recursive(repo.working_tree_dir))
with open('current_files.txt', 'r') as f:
    current_files = [x.strip() for x in f.readlines()]

since_commit = 'f1f8056'
commits = repo.iter_commits(f"{since_commit}..exact_copy")

relevant_commits: list[git.Commit] = []
for commit in commits:
    commit_files = commit.stats.files.keys()
    if any(file in current_files for file in commit_files):
        relevant_commits.append(commit)

for commit in relevant_commits:
    print(f"  Commit: {commit.hexsha[0:7]} - {commit.committed_datetime}: {commit.message}")
