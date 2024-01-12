from typing import Optional, Union, Callable
from . import globals
from .buffer import Buffer
from .bus import Bus
from .server import Server

class Synth:
    def __init__(self,
                 server: Server,
                 name: str,
                 args: dict = None,
                 action: int = globals.ADD_TO_HEAD,
                 target: Optional[int] = None):
        """
        Create a new SuperCollider Synth object.

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
                    args_list += [item, value.id]
                elif isinstance(value, Bus):
                    args_list += [item, value.id]
                else:
                    args_list += [item, value]

        target_id = target.id if target else 0
        self.server._send_msg("/s_new", self.name, self.id, action, target_id, *args_list)

    def set(self,
            parameter: str,
            value: Union[int, float, str]) -> None:
        """
        Set a named parameter of the Synth.

        Args:
            parameter (str): The parameter name.
            value: The value. Can be of type int, float, str.
        """
        self.server._send_msg("/n_set", self.id, parameter, value)

    def get(self,
            parameter: str,
            callback: Optional[Callable] = None,
            blocking: bool = True) -> Union[int, float, str]:
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

        def _handler(_, *args):
            return args[2]

        self.server._send_msg("/s_get", self.id, parameter)

        if blocking:
            rv = self.server._await_response("/n_set", [self.id, parameter], _handler)
            return rv
        else:
            self.server.dispatcher.map("/n_set", lambda *args: callback(_handler(*args)))

    def free(self):
        """
        Free the Synth.
        """
        self.server._send_msg("/n_free", self.id)
