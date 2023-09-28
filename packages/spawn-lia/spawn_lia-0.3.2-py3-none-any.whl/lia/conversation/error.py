from lia.conversation.emojis import angered_face, broken_heart
from click import echo


def subprocess_error() -> str:
    """Standard error message for subprocesses.

    :author: Julian M. Kleber
    """

    message = f"Oh no {broken_heart}\n" f"There was an error in a subprocess."
    return message
