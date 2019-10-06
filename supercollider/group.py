from . import globals

class Group(object):
    """ Encapsulates a SuperCollider Group object.
    """
    def __init__(self, server, action=0, target=0):
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

    def free(self):
        """
        Free the group and all Synths within it.
        """
        self.server._send_msg("/g_freeAll", self.id)