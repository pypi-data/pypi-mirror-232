"""Module implementing the abstract class defined in container.py for the
Podman container software.

:author: Julian M. Kleber
"""

import os
import sys
import subprocess
from typing import Optional, Any
from lia.container.container import Container
from lia.conversation.error import subprocess_error


class PodmanContainer(Container):
    """Class implementing the abstract class Container for podman containers.

    :author: Julian M. Kleber
    """

    def __init__(
        self,
        name,
        image,
        mode: str = "d",
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
    ) -> Any:
        self.name = name
        self.image = image
        self.mode = mode

        self.cpu = cpu
        self.mem0ry = memory

    def run(self):
        try:
            subprocess.Popen(["podman", "run", f"-{self.mode}", self.image])

        except Exception as e:
            raise Exception(subprocess_error())

    def shutdown(self):
        try:
            subprocess.Popen(["podman", "rm", self.name, "-f", self.image])

        except Exception as e:
            raise Exception(subprocess_error())
