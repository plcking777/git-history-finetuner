import subprocess
import sys
from utils import *
from diff_parser import DiffParser

from compressor.main_comp import MainComp



N = 1000


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
        "--no-merges",
        '--pretty=format:"%h"',
    ]
)


git_log = git_log.decode("utf-8").replace('"', "").split("\n")


print("logs:",len(git_log))


git_log = git_log[0:N]

#target_commit = 2
target_commit = 4

diff = get_diff(repo, git_log[target_commit])


diffParser = DiffParser(repo, diff)

parsed_diff = diffParser.parse()


print("hash:", git_log[target_commit])
for file in parsed_diff.keys():
    print(f" --------  {file}  ---------- ")

    file_content = get_file_on_hash(repo, git_log[target_commit], file)

    print(MainComp.compress(file, file_content, parsed_diff))
    print(" -------------------- ")
