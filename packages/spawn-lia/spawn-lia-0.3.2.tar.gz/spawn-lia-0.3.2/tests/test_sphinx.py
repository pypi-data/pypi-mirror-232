"""
Test the sphinx support from lia 

:author: Julian M. Kleber
"""
import subprocess
from subprocess import PIPE, Popen


def test_sphinx_quickstart():
    out = subprocess.run(["lia", "mkdocs", "-d", "lia"], capture_output=True)
    assert "Your project is now of high quality" in str(out)
    # case 2
    out = subprocess.run(["lia", "mkdocs", "-d", "fantasy dir"], capture_output=True)
    assert "returned non-zero exit status" in str(out)
