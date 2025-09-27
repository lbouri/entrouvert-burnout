import argparse
import os
import subprocess
from collections import defaultdict
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
    """
    Clones a repository either using GitPython or subprocess.
    """
    if not os.path.exists(LOCAL_PATH):
        print("Cloning repository...")
        if USE_GITPYTHON:
            Repo.clone_from(REPO_URL, LOCAL_PATH)
        else:
            subprocess.run(["git", "clone", REPO_URL, LOCAL_PATH], check=True)


def get_commits(since=None):
    """
    Retrieves commits from a Git repository either using GitPython library or subprocess with Git command.

    :param since: Filter the commits based on a specific date.
    """
    if USE_GITPYTHON:
        repo = Repo(LOCAL_PATH)
        branch = repo.active_branch.name

        # add filter
        kwargs = {}
        if since:
            kwargs["since"] = since
        commits = repo.iter_commits(branch, **kwargs)
        # retrieve commits
        for commit in commits:
            yield (
                commit.author.name,
                datetime.fromtimestamp(commit.committed_date),
            )
    else:
        cmd = ["git", "-C", LOCAL_PATH, "log"]

        # add filter
        if since:
            cmd.append(f"--since={since}")
        cmd.append("--pretty=format:%an|%ct")
        output = subprocess.check_output(cmd, text=True)
        # retrieve commits
        for line in output.splitlines():
            author, timestamp = line.split("|", 1)
            yield author, datetime.fromtimestamp(int(timestamp)),


def is_off_hours(commit_date):
    """
    Determines if a given commit date is during non-working hours.

    :param commit_date: Datetime of the commit

    :return: The function `is_off_hours(commit_date)` returns `True` if the commit date is on a weekend
    (Saturday or Sunday) or if the commit time is before 8 AM or after 8 PM. Otherwise, it returns
    `False`.
    """
    if commit_date.weekday() >= 5:
        return True
    if commit_date.hour < 8 or commit_date.hour > 20:
        return True
    return False


def compute_off_hours_rate(commits):
    """
    Calculates the off-hours commit rate for each author based on their total commits and off-hours commits.

    :param commits: Commit object, contains Author and Datetime
    :return: Returns two dictionaries: `total_commits` and `rate`.
    """
    total_commits = defaultdict(int)
    off_hours_commits = defaultdict(int)

    for author, commit_date in commits:
        if is_off_hours(commit_date):
            off_hours_commits[author] += 1
        total_commits[author] += 1

    rate = {}
    for author in total_commits:
        rate[author] = round(off_hours_commits[author] / total_commits[author], 2)
    return total_commits, off_hours_commits, rate


def compute_score_index(off_hours_commits):
    """
    Calculates a score index for each author based on their commit scores relative to the mean score.

    :param off_hours_commits: A dictionary where the keys are authors and the values are off-hours commits.
    :return: A dictionary where each author from the input `score_commits` is mapped
    to their score divided by the mean score of all authors' scores.
    """
    score_index_commits = defaultdict(int)
    off_hours_number = list(off_hours_commits.values())
    mean_score = sum(off_hours_number) / len(off_hours_number) if off_hours_number else 0

    for author, off_hours_number in off_hours_commits.items():
        score_index_commits[author] = round(off_hours_number / mean_score, 2) if mean_score else 0

    return score_index_commits


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyses of git commits")
    parser.add_argument(
        "--since",
        type=str,
        help="Start date since when commits should be retrieved (YYYY-MM-DD)",
    )
    args = parser.parse_args()
    clone_repo()
    total_commits, off_hours_commits, rate_commits = compute_off_hours_rate(get_commits(since=args.since))
    score_index_commits = compute_score_index(off_hours_commits)
    sorted_score_index_commits = sorted(
        score_index_commits.items(), key=lambda x: x[1], reverse=True
    )

    print("Author", "Rate", "Total", "Index")
    for author, score_index in sorted_score_index_commits:
        print(
            author,
            rate_commits[author],
            total_commits[author],
            score_index,
        )
