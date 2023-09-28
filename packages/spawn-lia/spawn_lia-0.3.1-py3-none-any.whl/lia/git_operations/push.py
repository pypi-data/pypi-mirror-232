"""Module for refactoring a git push after some coding has been done."""
import subprocess
import click

from lia.conversation.get_input import get_input
from lia.conversation.emojis import face_with_hearts


@click.command(help="push to remote specified")
@click.argument("remote", required=True)
def push(remote: str) -> None:  # pragma: no cover
    """The push function is used to push the changes made in the local
    repository to a remote repository.

    :param remote: str: Used to specify the remote repository we want to
        push to.
    :return: None.  :doc-author: Julian M. Kleber
    """

    subprocess.run(["git add ."], check=True, shell=True)
    subprocess.run([f"git push {remote}"], check=True, shell=True)


def do_commit() -> None:
    """The do_commit function is used to commit the changes made in the current
    working directory. The function takes no arguments and returns None.

    :return: None.  :doc-author: Julian M. Kleber
    """

    commit_message = get_commit_message()

    subprocess.run([f'git commit -m{"commit_message"}'], check=True, shell=True)


def get_commit_message() -> str:
    """The get_commit_message function prompts the user for a commit message
    and returns it as a string.

    :return: The commit message.  :doc-author: Julian M. Kleber
    """

    input_prompt = (
        f"Let's document in the commit message what we have done {face_with_hearts}: "
    )
    commit_message = get_input(input_prompt)
    return commit_message.decode("utf-8")
