"""Module for automating doc generation process."""
import os
import click
from click import echo
import subprocess

from lia.conversation.sphinx import say_sphinx_success_message, say_sphinx_error_message
from lia.utils.error import handle_out


@click.command()
@click.option(
    "-d", default="app", help="Specify where the source directory of the code lives"
)
def mkdocs(d: str) -> None:
    """Function to generate documentation during the tests. Your current
    directory must be the root directory of the project.

    :author: Julian M. Kleber
    """

    source_dir = "../" + d

    out = subprocess.run(
        [f"cd docs && sphinx-apidoc -o source/ {source_dir} && make html"],
        capture_output=True,
        shell=True,
        check=True,
    )
    handle_out(
        str(out),
        "Generated docs using apidoc and built html",
        say_sphinx_error_message(),
    )
    echo(say_sphinx_success_message())
