"""Module for handling suprocess errors.

:author: Julian M. Kleber
"""
from click import echo


def handle_out(out: str, success_message: str, error_message: str) -> None:
    if "returncode=0" in out:
        echo(success_message)
    else:
        echo(error_message)
        exit()
