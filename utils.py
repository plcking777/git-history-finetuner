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