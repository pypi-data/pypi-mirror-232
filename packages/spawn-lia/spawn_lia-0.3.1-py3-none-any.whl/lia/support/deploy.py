"""Module for deployment functionality.

:author: Julian M. Kleber
"""
import subprocess
import os

import click
from click import echo

from lia.conversation.end_message import say_end_message
from lia.conversation.start_message import say_start_message
from lia.git_operations.verify_branch import verify_branch


@click.command()
@click.option("-t", default="y", help="If test should be run")
def deploy(t: str) -> None:
    """Deployment routine.

    :author: Julian M. Kleber
    """
    say_start_message()
    verify_branch()
    if t == "y":
        out = subprocess.run(
            ["python -m pytest tests/"], shell=True, check=True, capture_output=True
        )
        try:
            assert "FAILED" not in str(out)
        except:
            echo(out)
        finally:
            echo("Done testing.")
    if os.path.isdir("dist") is True:
        subprocess.run(["rm -r dist "], shell=True, check=True)
    if os.path.isdir("build") is True:
        subprocess.run(["rm -r build"], shell=True, check=True)
    subprocess.run(["python3 -m build"], shell=True, check=True)
    subprocess.run(["twine check dist/*"], shell=True, check=True)
    subprocess.run(["python3 -m twine upload dist/*"], shell=True, check=True)
    say_end_message()
