"""This is lia's main program.

:author: Julian M. Kleber
"""
import click


# spells
from lia.bounty.heal import heal, heal_file
from lia.support.deploy import deploy
from lia.git_operations.push import push
from lia.sphinx.generate_docs import mkdocs


@click.group()
def spells() -> None:
    """Collection for Lia's spells.

    For more info ask for help on each specific spell.
    """
    pass  # pragma: no cover


spells.add_command(heal)
spells.add_command(heal_file)
spells.add_command(deploy)
spells.add_command(push)
spells.add_command(mkdocs)

if __name__ == "__main__":
    spells()
