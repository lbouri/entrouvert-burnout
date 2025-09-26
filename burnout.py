import os
import subprocess
from datetime import datetime
import argparse

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


def get_commits(max_count=None, since=None):
    """Retrieve commits"""
    if USE_GITPYTHON:
        repo = Repo(LOCAL_PATH)

        # add filter
        kwargs = {}
        if since:
            kwargs["since"] = since
        commits = repo.iter_commits("master", **kwargs)
        # display commits
        for commit in commits:
            yield (
                commit.author.name,
                datetime.fromtimestamp(commit.committed_date),
                commit.message.strip(),
            )
    else:
        cmd = ["git", "-C", LOCAL_PATH, "log"]

        # add filter
        if since:
            cmd.append(f"--since={since}")
        cmd.append("--pretty=format:%an|%ct|%s")
        output = subprocess.check_output(cmd, text=True)
        # display commits
        for line in output.splitlines():
            author, timestamp, message = line.split("|", 2)
            yield author, datetime.fromtimestamp(int(timestamp)), message


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyses of git commits")
    parser.add_argument(
        "--since",
        type=str,
        help="Start date since when commits should be retrieved (YYYY-MM-DD)",
    )
    args = parser.parse_args()

    clone_repo()
    for author, date, msg in get_commits(since=args.since):
        print(f"{author} - {date} - {msg}")
