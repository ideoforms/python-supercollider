from . import globals

class Synth(object):
    """ Encapsulates a SuperCollider Synth object.
    """
    def __init__(self, server, name, args=None, action=0, target=None):
        """
        Create a new Synth.

        Args:
            server (Server): The SC server on which the Synth is created.
            name (str): The name of the SynthDef.
            args (dict): A dict of parameters and values.
            target (int): The Group to create the Synth in, default 0.
            action (int): The add action.
        """
        self.server = server
        self.name = name
        self.args = args
        self.id = globals.LAST_NODE_ID
        globals.LAST_NODE_ID += 1

        args_list = []
        if args:
            args_list = [b for a in list(args.items()) for b in a]

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

    def get(self, parameter, fn):
        """
        Get the current value of a named parameter of the Synth.
        This action is asynchronous as it queries the server. It thus returns None,
        and a function `fn` must be specified to receive the return value.

        Args:
            parameter:
            fn: Handler which is passed the value as a single argument.

        Example:
            >>> synth.get("freq", lambda f: print(f))
            440.0
        """
        self.server._add_handler("/n_set", self.id, parameter, fn)
        self.server._send_msg("/s_get", self.id, parameter)

    def free(self):
        """
        Free the Synth.
        """
        self.server._send_msg("/n_free", self.id)
