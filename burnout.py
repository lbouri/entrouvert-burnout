import argparse
import os
import re
import subprocess
import unicodedata
from collections import defaultdict
from datetime import datetime

# Remote repository to analyze
REPO_URL = "https://git.entrouvert.org/entrouvert/passerelle.git"
LOCAL_PATH = "./passerelle_repo"

# Check if GitPython is available
try:
    from git import Repo

    USE_GITPYTHON = True
except ImportError:
    USE_GITPYTHON = False


def validate_since(since_str):
    """
    Validate the format of the date provided to the --since argument.

    Args:
        since_str (str): Date string in YYYY-MM-DD format.

    Raises:
        ValueError: If the format does not match YYYY-MM-DD.

    Returns:
        str: The validated date string.
    """
    if since_str is None:
        return None
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, since_str):
        raise ValueError(
            f"Invalid date format for --since: {since_str}. Expected YYYY-MM-DD."
        )
    return since_str


def normalize_author(author):
    """
    Normalize the author's name:
      - Convert to lowercase
      - Remove accents and diacritics

    Args:
        author (str): Author's name

    Returns:
        str: Normalized name (lowercase, accent-free)
    """
    if not author:
        return ""
    author = author.lower()
    author = unicodedata.normalize("NFKD", author)
    author = "".join(c for c in author if not unicodedata.combining(c))
    return author


def clone_repo():
    """
    Clone the remote Git repository if the local directory does not already exist.
    Uses GitPython if available, otherwise subprocess.
    """
    if not os.path.exists(LOCAL_PATH):
        print("Cloning repository...")
        if USE_GITPYTHON:
            Repo.clone_from(REPO_URL, LOCAL_PATH)
        else:
            subprocess.run(["git", "clone", REPO_URL, LOCAL_PATH], check=True)


def get_commits(since=None):
    """
    Retrieve the list of commits (author + date) from the repository.

    Args:
        since (str, optional): Start date in YYYY-MM-DD format.

    Yields:
        tuple: (author, datetime)
    """
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
    """
    Determine whether a commit was made outside regular working hours.

    Args:
        commit_date (datetime): The commit date and time.

    Returns:
        bool: True if the commit was made on a weekend or before 8 AM / after 8 PM.
    """
    if commit_date.weekday() >= 5:
        return True
    if commit_date.hour < 8 or commit_date.hour > 20:
        return True
    return False


def compute_off_hours_rate(commits):
    """
    Compute the rate of commits made outside regular working hours.

    Args:
        commits (iterable): Iterable of tuples (author, datetime)

    Returns:
        tuple(dict, dict, dict):
            - total_commits: total commits per author
            - off_hours_commits: commits made outside working hours per author
            - rate: proportion of off-hours commits (0–1)
    """
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
    """
    Compute a relative score index for each author based on the average number
    of commits made outside regular working hours.

    Args:
        off_hours_commits (dict): Number of off-hours commits per author

    Returns:
        dict: Relative index per author (1.0 = average)
    """
    score_index_commits = defaultdict(int)
    values = list(off_hours_commits.values())
    mean_score = sum(values) / len(values) if values else 0

    for author, value in off_hours_commits.items():
        score_index_commits[author] = round(value / mean_score, 2) if mean_score else 0

    return score_index_commits


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Git commit activity analysis")
    parser.add_argument(
        "--since",
        type=validate_since,
        help="Start date for commit retrieval (YYYY-MM-DD)",
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
