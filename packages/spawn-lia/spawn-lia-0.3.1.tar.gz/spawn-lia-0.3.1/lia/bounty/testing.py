"""Module to execute automatized tests.

:author: Julian M. Kleber
"""
import subprocess


def test_package() -> None:
    """The test_package function is used to test the package. It is called by
    the main function if the user chooses to run tests. The function uses
    subprocess and pytest to run all of our tests in a single command.

    :doc-author: Julian M. Kleber
    """
    try:
        subprocess.run(["python -m pytest tests/"], shell=True, check=True)
    except Exception as exc:
        print(str(exc))
