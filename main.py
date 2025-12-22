import subprocess
import sys
from utils import *
from diff_parser import DiffParser

N = 5


if len(sys.argv) != 2:
    raise ValueError("Expected a `repository path` argument")
repo = sys.argv[1]


# get N git commits
git_log = subprocess.check_output(
    [
        "git",
        "-C",
        repo,
        "log",
        "--oneline",
        "--all",
        "--no-merges",
        '--pretty=format:"%h"',
    ]
)


git_log = git_log.decode("utf-8").replace('"', "").split("\n")


git_log = git_log[0:N]
print(git_log)


target_commit = 0

diff = get_diff(repo, git_log[target_commit + 1], git_log[target_commit])
print(diff)

print("\n ----------------- ")

diffParser = DiffParser(repo, git_log[target_commit + 1], diff)


print(diffParser.files)

print(diffParser.parse())
