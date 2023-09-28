from click import echo

from lia.conversation.emojis import (
    angered_face,
    broken_heart,
    kissing_cat,
    partying_face,
    smiling_face_with_sunglasses,
)
from lia.conversation.error import subprocess_error


def say_sphinx_success_message() -> str:
    message = (
        f"Respect, You passed the sphinx {partying_face}\n"
        f"Your project is now of high quality {smiling_face_with_sunglasses}"
    )
    return message


def say_sphinx_error_message() -> str:
    """Sphinx error message if generating of the docs failed or the folder is
    not accessible :author: Julian M.

    Kleber
    """

    message1 = subprocess_error()
    message2 = (
        message1 + "\n"
        f"Please make sure that you have setup your docs folder properly {kissing_cat}"
    )
    return message2
