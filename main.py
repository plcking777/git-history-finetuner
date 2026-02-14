import subprocess
import sys
from utils import *
from diff_parser import DiffParser
import json

from compressor.main_comp import MainComp



N = 5000


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


def open_and_append(file_path: str, content: str):
    file = open(file_path, 'a')
    file.write(content)
    file.flush()

def template_file_and_content(file_path: str, content: str):
    return f"In `{file_path}`\n```\n{content}\n```\n\n"


BATCH_SIZE = 3


open_and_append("out.json", "[\n")


indent = 4

"""
list of dicts with "input" and "output" keys
"""
batch_content = []

for i in range(N):
    commit_hash = git_log[i]
    print("processing: ", commit_hash)

    message = get_commit_message(repo, commit_hash)
    print("message: ", message)


    diff = get_diff(repo, commit_hash)
    diffParser = DiffParser(repo, diff)
    parsed_diff = diffParser.parse()


    output = ""
    for file in parsed_diff.keys():
        file_content = get_file_on_hash(repo, commit_hash, file)
        comp_content = MainComp.compress(file, file_content, parsed_diff)
        output += template_file_and_content(file, comp_content)


    batch_content.append({
        "input": message,
        "output": output
    })

    is_last = i == N - 1

    if i % BATCH_SIZE == 0 or is_last:
        json_batch = json.dumps(batch_content, indent=indent)
        batch_content.clear()

        # remove first and last char ("[", "]")
        json_batch = json_batch[1:]
        json_batch = json_batch[:len(json_batch) - 2] # remove 2 values to also remove the trailing "\n"



        if not is_last:
            json_batch += ","

        open_and_append("out.json", json_batch)



open_and_append("out.json", "\n]")
