from . import globals
from .buffer import Buffer
from .bus import Bus

class Synth(object):
    """ Encapsulates a SuperCollider Synth object.
    """
    def __init__(self, server, name, args=None, action=globals.ADD_TO_HEAD, target=None):
        """
        Create a new Synth.

        Args:
            server (Server): The SC server on which the Synth is created.
            name (str): The name of the SynthDef.
            args (dict): A dict of parameters and values.
            target (int): The Group to create the Synth in, default 0.
            action (int): The add action. See supercollider.globals for available actions.
        """
        self.server = server
        self.name = name
        self.args = args
        self.id = globals.LAST_NODE_ID
        globals.LAST_NODE_ID += 1

        args_list = []
        if args:
            for item, value in args.items():
                # TODO: Move this to a more general place (so `set` can also work with Bus/Buffer objects)
                if isinstance(value, Buffer):
                    args_list += [ item, value.id ]
                elif isinstance(value, Bus):
                    args_list += [ item, value.id ]
                else:
                    args_list += [ item, value ]

        target_id = target.id if target else 0
        self.server._send_msg("/s_new", self.name, self.id, action, target_id, *args_list)

    def set(self, parameter, value):
        """
        Set a named parameter of the Synth.

        Args:
            parameter (str): The parameter name.
            value: The value. Can be of type int, float, str.
        """
        self.server._send_msg("/n_set", self.id, parameter, value)

    def get(self, parameter, callback=None, blocking=True):
        """
        Get the current value of a named parameter of the Synth.

        Args:
            parameter (str): The name of the parameter to query.
            callback (function): Called when the return value is received from the SC server.
            blocking (bool): Set to False to query the value asynchronously and return None.

        Example:
            >>> synth.get("freq")
            440.0
        """

        self.server._send_msg("/s_get", self.id, parameter)

        if blocking:
            rv = self.server._await_response("/n_set", [self.id, parameter])
            return rv
        else:
            self.server._add_handler("/n_set", [self.id, parameter], callback)

    def free(self):
        """
        Free the Synth.
        """
        self.server._send_msg("/n_free", self.id)
