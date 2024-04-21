#!/usr/bin/python3


import subprocess
import sys
import time


SHELL_COMMANDS = [
    "pwd",
    "pip --no-cache-dir install .[testing]",
    "mypy --cache-dir /dev/null aguirre",
    "python -m unittest discover tests/",
    "(pyroma . || true)",
]


def setUp(ctrname: str, image: str) -> None:
    args = [
        "docker", "run",
        "--rm",
        "--detach",
        "--name", ctrname,
        "--entrypoint", "/bin/sh",
        "--workdir", "/root",
        "--volume", ".:/root:ro",
        image,
        "-c", "sleep 999999",
    ]
    subprocess.run(args, check=True)


def runCommand(ctrname: str, command: str) -> None:
    args = [
        "docker", "exec", ctrname, "/bin/sh", "-c", command,
    ]
    subprocess.run(args, check=True)


def tearDown(ctrname: str) -> None:
    args = [
        "docker", "container", "kill", ctrname,
    ]
    subprocess.run(args, check=True)
    time.sleep(5)


def main() -> None:
    ctrname = "ephemerun-poc"
    imageversion = sys.argv[1]
    image = f"python:{imageversion}"
    try:
        setUp(ctrname, image)
        for command in SHELL_COMMANDS:
            runCommand(ctrname, command)
    finally:
        tearDown(ctrname)


if __name__ == "__main__":
    main()
