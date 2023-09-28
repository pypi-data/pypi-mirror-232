"""
Test the sphinx support from lia 

:author: Julian M. Kleber
"""
import subprocess


def test_sphinx_quickstart(): 

    out = subprocess.Popen(
        ["python", "./lia/sphinx/generate_docs.py"], stdin=PIPE, stdout=PIPE
    )
    out.stdin.write(b"y\n")
    outputlog, errorlog = out.communicate()
    out.stdin.close()

    assert errorlog is None
