"""Module for generating generic input."""


def get_input(input_prompt: str) -> str:
    """The get_input function takes a string as an argument and returns the
    user's input. The function prompts the user for input, converts their
    answer to lowercase, and returns it.

    :param input_prompt: str: Used to Prompt the user for input.
    :return: The answer of the user.  :doc-author: Julian M. Kleber
    """

    answer = input(input_prompt)
    answer = answer.lower()

    return answer
