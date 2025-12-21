import subprocess
import sys
from utils import *


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


print(get_diff(repo, git_log[0], git_log[1]))
