#!/usr/bin/python3


from typing import List, Optional

import logging
LOG = logging.getLogger("ephemerun")

import argparse
import subprocess
import sys
import time


class Shell:

    def __init__(self, command):
        self.command = command

    def apply(self, backend):
        backend.run_command(self.command)


class Workdir:

    def __init__(self, workdir):
        self.workdir = workdir

    def apply(self, backend):
        backend.set_workdir(self.workdir)


ACTIONS = [  # FIXME
    Workdir("/root"),
    Shell("cp -air ./src/* ."),
    Shell("pip --no-cache-dir install .[testing]"),
    Shell("mypy --cache-dir /dev/null aguirre"),
    Shell("coverage run -m unittest discover tests/"),
    Shell("coverage report -m"),
    Shell("(pyroma . || true)"),
]


class DockerBackend:

    def __init__(self, ctrname: str) -> None:
        self.ctrname = ctrname

    def set_workdir(self, workdir: Optional[str]):
        LOG.info("Workdir: %s" % workdir)
        self.workdir = workdir

    def set_up(self, image: str) -> None:
        LOG.info("Starting: %s" % self.ctrname)
        args = [
            "docker", "run",
            "--rm",
            "--detach",
            "--name", self.ctrname,
            "--entrypoint", "/bin/sh",  # FIXME
            "--volume", ".:/root/src:ro",  # FIXME
            image,
            "-c", "sleep 999999",  # FIXME
        ]
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

    def run_command(self, command: str) -> None:
        LOG.info("Run: %s" % command)
        args = ["docker", "exec"]
        if self.workdir is not None:
            args.extend(["--workdir", self.workdir])
        args.extend([self.ctrname, "/bin/sh", "-c", command])
        subprocess.run(args, check=True)

    def tear_down(self) -> None:
        LOG.info("Stopping: %s" % self.ctrname)
        args = [
            "docker", "container", "kill", self.ctrname,
        ]
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL)
        time.sleep(5)


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True)
    return parser.parse_args(args)


def main() -> None:
    logging.basicConfig(level="INFO", format="[ephemerun] %(message)s")
    ctrname = "ephemerun-poc"  # FIXME
    options = parse_args(sys.argv[1:])
    backend = DockerBackend(ctrname)
    try:
        backend.set_up(options.image)
        for action in ACTIONS:
            action.apply(backend)
        LOG.info("All actions completed successfully")
    except KeyboardInterrupt:
        LOG.error("Interrupted")
    except subprocess.CalledProcessError as exc:
        LOG.error("Error: %s" % exc)
    except subprocess.TimeoutExpired as exc:
        LOG.error("Timeout: %s" % exc)
    finally:
        backend.tear_down()


if __name__ == "__main__":
    main()
