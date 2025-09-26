import os
import subprocess
from datetime import datetime

REPO_URL = "https://git.entrouvert.org/entrouvert/passerelle.git"
LOCAL_PATH = "./passerelle_repo"

# Trying to import GitPython
try:
    from git import Repo
    USE_GITPYTHON = True
except ImportError:
    USE_GITPYTHON = False


def clone_repo():
    """Cloning repository"""
    if not os.path.exists(LOCAL_PATH):
        print("Cloning repository...")
        if USE_GITPYTHON:
            Repo.clone_from(REPO_URL, LOCAL_PATH)
        else:
            subprocess.run(["git", "clone", REPO_URL, LOCAL_PATH], check=True)


def get_commits(max_count=10):
    """Retrieve commits"""
    if USE_GITPYTHON:
        repo = Repo(LOCAL_PATH)
        commits = repo.iter_commits("master", max_count=max_count)
        for commit in commits:
            yield commit.author.name, datetime.fromtimestamp(commit.committed_date), commit.message.strip()
    else:
        cmd = ["git", "-C", LOCAL_PATH, "log", f"-{max_count}", "--pretty=format:%an|%ct|%s"]
        output = subprocess.check_output(cmd, text=True)
        for line in output.splitlines():
            author, timestamp, message = line.split("|", 2)
            yield author, datetime.fromtimestamp(int(timestamp)), message


if __name__ == "__main__":
    clone_repo()
    for author, date, msg in get_commits(5):
        print(f"{author} - {date} - {msg}")