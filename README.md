# Burnout Passerelle Entr Ouvert Git Analysis

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

This Python script analyzes Git commits to identify **off-hours contributions**, aiming to detect potential risks of overload or burnout among developers.

---

## Features

- Automatically clones the Passerelle repository if not already present locally.
- Retrieves commits from a given start date (optional).
- Computes for each author:
  - **Off-hours commit rate** (weekends or before 8am / after 8pm)
  - **Total number of commits**
  - **Relative index** compared to the average number of Off-hours commits
- Outputs authors **sorted by descending index** (highest off-hours contributors first).

---

## Installation

1. Clone this repository or download `burnout.py`.
2. (Optional) Install GitPython:

```bash
pip install GitPython
```

👉 The script works without GitPython by using Git commands through subprocess.

## Usage

```bash
python burnout.py [--since YYYY-MM-DD]
```

## Options

- `--since YYYY-MM-DD`  
  Start date to filter commits.  
  If not provided, all commits from the repository history are retrieved.

```bash
python burnout.py --since 2025-08-01
```

## Output

The script prints a table like this:

| Author   | Rate  | Total | Index |
|----------|-------|-------|-------|
| Alice    | 0.25  | 40    | 1.2   |
| Charlie  | 0.30  | 30    | 1.1   |
| Bob      | 0.10  | 50    | 0.6   |

**Columns explanation:**
- **Rate** → fraction of off-hours commits (0–1)  
- **Total** → total number of commits
- **Index** → relative off-hours commits compared to the average (1 = average, >1 = above average)  

👉 The table is always **sorted in descending order of Index**, so the authors with the highest relative off-hours activity appear first.


## Author

Laurent Bouri
