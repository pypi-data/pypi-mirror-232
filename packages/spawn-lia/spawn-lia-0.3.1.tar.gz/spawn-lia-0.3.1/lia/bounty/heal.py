"""Module for python file bug revealing functionality.

:author: Julian M. Kleber
"""
import os
import subprocess
import click

from lia.conversation.end_message import say_end_message
from lia.conversation.start_message import say_start_message

from lia.git_operations.verify_branch import verify_branch

from lia.bounty.testing import test_package


@click.command()
@click.argument("packagename")
@click.option("-t", default="y", help="If test should be run")
def heal(packagename: str, t: str) -> None:  # pragma: no cover
    """One of Lias most basic spells. It lints, and typechecks the code
    specified in the path. To test use the -t option. Lia only supports pytest.

    The heal function is a wrapper for the following commands:
        - black
        - autopep8
        - flake8 (with E9, F63, F7 and F82)
        - mypy --strict
       It also runs pylint with the parseable output format to
       make it easier to integrate into CI systems like
       Woodpecker or Codeberg CI.

    :param packagename:str: Used to specify the package name.
    :param o:str: Used to specify if the user wants to run tests or not.

    :doc-author: Julian M. Kleber
    """

    say_start_message()
    verify_branch()

    assert t in ["y", "n"], "Plase specify -t as y/n"
    assert os.path.isdir(packagename)

    if not packagename.endswith("/"):
        packagename += "/"

    bounty_routine(object_name=packagename)

    if t == "y":
        test_package()

    out = subprocess.run(
        ["pip freeze > requirements.txt"], shell=True, check=True, capture_output=True
    )

    say_end_message()


@click.command(name="heal-file")
@click.argument("file_name")
def heal_file(file_name: str) -> None:
    """The heal_file function is a wrapper for the bounty_routine function. It
    is designed to be called from the command line, and it takes one argument:
    the name of a file in your repository that you want to heal. It will then
    run the bounty_routine on that file, which will check out all commits where
    that file was changed and attempt to fix any errors found by flake8.

    :param file_name: str: Used to specify the name of the file that is
        being healed.
    :return: Nothing.  :doc-author: Julian M. Kleber
    """

    say_start_message()
    verify_branch()

    bounty_routine(object_name=file_name)

    say_end_message()


def bounty_routine(object_name: str) -> None:
    """
    The bounty_routine function is a wrapper for the following commands:
        1. black {object_name}
        2. find . -type f -wholename '{object_name}/*.py'
            -exec sed --in-place 's/[[:space:]]\+$/ /g' {} \+ #sanitize trailing whitespace
        3. autopep8 --in-place --recursive {object_name}  #reformat code according to PEP 8 style
            guide (except E501)

       The bounty_routine function also runs the following checks on your package's
       source code files,and reports any errors or warnings it finds in them:

       4. python -m flake8 {object_name} --count --select=F63,F7,F82,W291,W292  #check for common
       errors and bad practices in Python source code files; see
       https://flake8rules.readthedocs.io/en/latest/#error-codes for more information
       about these error codes; note that this command does not check all of Flake8's rules
       by default because some of them are too strict or pedantic (e..g., F401

    :param object_name:str: Used to Specify the name of the object to be passed into the function.
    :return: Julian M. Kleber

    :doc-author: Julian M. Kleber
    """

    subprocess.run(["black " + object_name], shell=True, check=True)
    subprocess.run(
        [
            f"find . -type f -wholename '{object_name}/*.py' "
            "-exec sed --in-place 's/[[:space:]]\+$//' "
            + "{} \+ #sanitize trailing whitespace"
        ],
        shell=True,
        check=True,
    )
    subprocess.run(
        [f"autopep8 --in-place --recursive {object_name}"], shell=True, check=True
    )
    subprocess.run(
        [
            f"python -m flake8 {object_name} --count --select=E9,F63,F7,F82"
            " --show-source --statistics"
        ],
        shell=True,
        check=True,
    )
    try:
        subprocess.run([f"mypy --strict {object_name}"], shell=True, check=True)
    except Exception as exc:
        print(str(exc))

    try:
        subprocess.run(
            [f"python -m pylint -f parseable {object_name}"], shell=True, check=True
        )
    except Exception as exc:
        print(str(exc))
    if object_name.endswith("/"):
        subprocess.run(
            [f"prettify-py format-dir {object_name}"], shell=True, check=True
        )
    else:
        subprocess.run(
            [f"prettify-py format-file {object_name}"], shell=True, check=True
        )
