import argparse
import os
import re
import subprocess
import unicodedata
from collections import defaultdict
from datetime import datetime

REPO_URL = "https://git.entrouvert.org/entrouvert/passerelle.git"
LOCAL_PATH = "./passerelle_repo"

try:
    from git import Repo

    USE_GITPYTHON = True
except ImportError:
    USE_GITPYTHON = False


def validate_since(since_str):
    """Validate the since date format YYYY-MM-DD"""
    if since_str is None:
        return None
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, since_str):
        raise ValueError(
            f"Invalid date format for --since: {since_str}. Expected YYYY-MM-DD."
        )
    return since_str


def normalize_author(author):
    """Lowercase and remove accents to unify author names"""
    if not author:
        return ""
    author = author.lower()
    author = unicodedata.normalize("NFKD", author)
    author = "".join(c for c in author if not unicodedata.combining(c))
    return author


def clone_repo():
    if not os.path.exists(LOCAL_PATH):
        print("Cloning repository...")
        if USE_GITPYTHON:
            Repo.clone_from(REPO_URL, LOCAL_PATH)
        else:
            subprocess.run(["git", "clone", REPO_URL, LOCAL_PATH], check=True)


def get_commits(since=None):
    if USE_GITPYTHON:
        repo = Repo(LOCAL_PATH)
        branch = repo.active_branch.name
        kwargs = {}
        if since:
            kwargs["since"] = since
        commits = repo.iter_commits(branch, **kwargs)
        for commit in commits:
            yield (
                normalize_author(commit.author.name),
                datetime.fromtimestamp(commit.committed_date),
            )
    else:
        cmd = ["git", "-C", LOCAL_PATH, "log"]
        if since:
            cmd.append(f"--since={since}")
        cmd.append("--pretty=format:%an|%ct")
        output = subprocess.check_output(cmd, text=True)
        for line in output.splitlines():
            author, timestamp = line.split("|", 1)
            yield normalize_author(author), datetime.fromtimestamp(int(timestamp))


def is_off_hours(commit_date):
    if commit_date.weekday() >= 5:
        return True
    if commit_date.hour < 8 or commit_date.hour > 20:
        return True
    return False


def compute_off_hours_rate(commits):
    total_commits = defaultdict(int)
    off_hours_commits = defaultdict(int)

    for author, commit_date in commits:
        if is_off_hours(commit_date):
            off_hours_commits[author] += 1
        total_commits[author] += 1

    rate = {
        author: round(off_hours_commits[author] / total_commits[author], 2)
        for author in total_commits
    }

    return total_commits, off_hours_commits, rate


def compute_score_index(off_hours_commits):
    score_index_commits = defaultdict(int)
    values = list(off_hours_commits.values())
    mean_score = sum(values) / len(values) if values else 0

    for author, value in off_hours_commits.items():
        score_index_commits[author] = round(value / mean_score, 2) if mean_score else 0

    return score_index_commits


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyse git commits")
    parser.add_argument(
        "--since",
        type=validate_since,
        help="Start date since when commits should be retrieved (YYYY-MM-DD)",
    )
    args = parser.parse_args()

    clone_repo()
    commits = get_commits(since=args.since)
    total_commits, off_hours_commits, rate_commits = compute_off_hours_rate(commits)
    score_index_commits = compute_score_index(off_hours_commits)
    sorted_score_index_commits = sorted(
        score_index_commits.items(), key=lambda x: x[1], reverse=True
    )

    print("Author", "Rate", "Total", "Index")
    for author, score_index in sorted_score_index_commits:
        print(author, rate_commits[author], total_commits[author], score_index)
