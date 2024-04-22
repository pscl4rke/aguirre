#!/usr/bin/python3


from typing import List

import argparse
import subprocess
import sys
import time


SHELL_COMMANDS = [  # FIXME
    "pwd",
    "cp -air ./src/* .",
    "ls",
    "pip --no-cache-dir install .[testing]",
    "mypy --cache-dir /dev/null aguirre",
    "python -m unittest discover tests/",
    "(pyroma . || true)",
]


class DockerBackend:

    def __init__(self, ctrname: str) -> None:
        self.ctrname = ctrname

    def set_up(self, image: str) -> None:
        args = [
            "docker", "run",
            "--rm",
            "--detach",
            "--name", self.ctrname,
            "--entrypoint", "/bin/sh",  # FIXME
            "--workdir", "/root",  # FIXME
            "--volume", ".:/root/src:ro",  # FIXME
            image,
            "-c", "sleep 999999",  # FIXME
        ]
        subprocess.run(args, check=True)

    def run_command(self, command: str) -> None:
        args = [
            "docker", "exec", self.ctrname, "/bin/sh", "-c", command,
        ]
        subprocess.run(args, check=True)

    def tear_down(self) -> None:
        args = [
            "docker", "container", "kill", self.ctrname,
        ]
        subprocess.run(args, check=True)
        time.sleep(5)


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True)
    return parser.parse_args(args)


def main() -> None:
    ctrname = "ephemerun-poc"  # FIXME
    options = parse_args(sys.argv[1:])
    backend = DockerBackend(ctrname)
    try:
        backend.set_up(options.image)
        for command in SHELL_COMMANDS:
            backend.run_command(command)
    finally:
        backend.tear_down()


if __name__ == "__main__":
    main()
