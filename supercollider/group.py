from __future__ import annotations

from . import globals
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import Server

class Group:
    def __init__(self,
                 server: Server,
                 action: int = 0,
                 target: int = 0):
        """
        Create a new Group.

        Args:
            server (Server): The SC server on which the Group is created.
            target (int): The Group to create the Group in, default 0.
            action (int): The add action.
        """
        self.server = server
        self.id = globals.LAST_NODE_ID
        globals.LAST_NODE_ID += 1

        self.server._send_msg("/g_new", self.id, action, target)

    def free(self) -> None:
        """
        Free the group and all Synths within it.
        """
        # /g_deepFree does not free the group itself; must also call /n_free.
        self.server._send_msg("/g_deepFree", self.id)
        self.server._send_msg("/n_free", self.id)
