"""Module implementing the Container interface in the package for LXC
containers.

:author: Julian M. Kleber
"""

import lxc
import sys

from lia.container.container import Container


class LXCContainer(Container):
    """Class implementing the abstract class Container for LXC containers.

    :author: Julian M. Kleber
    """

    def __init__(self, name):
        pass
