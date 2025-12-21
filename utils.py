import subprocess



def get_commit_message(repo, hash):
    #git log --format=%B -n 1 {hash}

    out = subprocess.check_output(
        [
            "git",
            "-C",
            repo,
            "log",
            "--format=%B",
            "-n",
            "1",
            hash,
        ]
    )

    return out.decode("utf-8")


def get_file_on_hash(repo, hash, file_path):
    #git show <hash>:<file_path>
    out = subprocess.check_output(
        [
            "git",
            "-C",
            repo,
            "show",
            f"{hash}:{file_path}",
        ]
    )

    return out.decode("utf-8")



def get_diff(repo, prev_hash, hash):
    #git diff <prev_hash>^..<hash>
    out = subprocess.check_output(
        [
            "git",
            "-C",
            repo,
            "diff",
            f"{prev_hash}^..{hash}",
        ]
    )

    return out.decode("utf-8")
