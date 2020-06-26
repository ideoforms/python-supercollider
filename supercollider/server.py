import liblo
import random
import logging
import threading
from . import globals
from .exceptions import SuperColliderConnectionError

logger = logging.getLogger(__name__)

class Server(object):
    def __init__(self, hostname="127.0.0.1", port=57110):
        """
        Create a new Server object, which is a local representation of a remote
        SuperCollider server.

        Args:
            hostname (str): Hostname or IP address of the server
            port (int): Port of the server
        """
        self.client_address = liblo.Address(hostname, port)

        #-----------------------------------------------------------------------
        # Set up OSC server and default handlers for receiving messages.
        #-----------------------------------------------------------------------
        self.osc_server = liblo.Server(random.randint(57200, 57900))
        self.osc_server.add_method(None, None, self._osc_handler)
        self.osc_server_thread = threading.Thread(target=self._osc_server_read)
        self.osc_server_thread.setDaemon(True)
        self.osc_server_thread.start()
        self.handlers = {
            "/n_set": {},
            "/b_info": {},
            "/b_setn" : {},
            "/done": {},
            "/status.reply": None,
            "/version.reply": None,
            "/synced": None,
            "/g_queryTree.reply": None
        }

        #-----------------------------------------------------------------------
        # Necessary when querying a node ID for add actions.
        #-----------------------------------------------------------------------
        self.id = 0
        try:
            self.sync()
        except SuperColliderConnectionError as e:
            self.osc_server.free()
            self.osc_server = None
            raise e

    def __del__(self):
        if  self.osc_server:
            self.osc_server.free()
            self.osc_server = None
        self.osc_server_thread.join()

    def sync(self):
        """
        Causes the server to immediately execute and flush all asynchronous commands.
        This command is always synchronous so blocks the current thread.

        This can be used as a `ping` functionality to check that the server is running
        and responding.
        """
        self._send_msg("/sync")
        return self._await_response("/synced", None, lambda n: n)
    
    def query_tree(self, group=None):
        self._send_msg("/g_queryTree", group.id if group else 0, 0)
        return self._await_response("/g_queryTree.reply")

    def get_status(self, callback=None, blocking=True):
        """
        Query the current Server status, including the number of active units, CPU
        load, etc.

        Example:
            >>> server.status
            {
                'num_ugens': 5,
                'num_synths': 1,
                'num_groups': 2,
                'num_synthdefs': 107,
                'cpu_average': 0.08170516043901443,
                'cpu_peak': 0.34912213683128357,
                'sample_rate_nominal': 44100.0,
                'sample_rate_actual': 44100.07866992249
            }
        """
        def _handler(args):
            args_dict = {
                "num_ugens": args[1],
                "num_synths": args[2],
                "num_groups": args[3],
                "num_synthdefs": args[4],
                "cpu_average": args[5],
                "cpu_peak": args[6],
                "sample_rate_nominal": args[7],
                "sample_rate_actual": args[8],
            }
            if callback:
                callback(args_dict)
            return args_dict

        self._send_msg("/status")
        if blocking:
            return self._await_response("/status.reply", None, _handler)
        elif callback:
            self._add_handler("/status.reply", None, _handler)

    def get_version(self, callback=None, blocking=True):
        """
        Returns the current Server version.

        Example:
            >>> server.version
            {
                'program_name': "scsynth",
                'version_major': 3,
                'version_minor': 10,
                'version_patch': ".3",
                'git_branch': "HEAD",
                'commit_hash': "67a1eb18"
            }
        """
        def _handler(args):
            args_dict = {
                "program_name": args[0],
                "version_major": args[1],
                "version_minor": args[2],
                "version_patch": args[3],
                "git_branch": args[4],
                "commit_hash": args[5]
            }
            if callback:
                callback(args_dict)
            return args_dict

        self._send_msg("/version")
        if blocking:
            return self._await_response("/version.reply", None, _handler)
        elif callback:
            self._add_handler("/version.reply", None, _handler)

    def _send_msg(self, msg, *args):
        liblo.send(self.client_address, msg, *args)

    def _await_response(self, address, match_args=(), callback=lambda rv=None: rv):
        event = threading.Event()
        rv = None

        def callback_with_timeout(*args):
            event.set()
            if callback:
                nonlocal rv
                rv = callback(*args)

        self._add_handler(address, match_args, callback_with_timeout)
        responded_before_timeout = event.wait(globals.RESPONSE_TIMEOUT)
        if not responded_before_timeout:
            raise SuperColliderConnectionError("Connection to SuperCollider server timed out. Is scsynth running?")

        return rv

    def _add_handler(self, address, match_args, callback):
        assert address in self.handlers

        if isinstance(self.handlers[address], dict):
            self.handlers[address][tuple(match_args)] = callback
        else:
            self.handlers[address] = callback

    def _osc_handler(self, address, args):
        logger.debug("Received OSC: %s, %s" % (address, args))
        if address == "/n_set":
            node_id, parameter, value = tuple(args)
            if (node_id, parameter) in self.handlers["/n_set"]:
                self.handlers["/n_set"][(node_id, parameter)](value)
        elif address == "/b_info":
            buffer_id, *values = tuple(args)
            if (buffer_id,) in self.handlers["/b_info"]:
                self.handlers["/b_info"][(buffer_id,)](values)
        elif address == "/b_setn":
            buffer_id, start_frame, stop_frame, *values = tuple(args)
            if (buffer_id,) in self.handlers["/b_setn"]:
                self.handlers["/b_setn"][(buffer_id,)](values)
        elif address == "/done":
            if tuple(args) in self.handlers["/done"]:
                self.handlers["/done"][tuple(args)]()
        elif address in self.handlers and self.handlers[address]:
            self.handlers[address](args)
        elif address == "/fail":
            logger.warning("Received failure: %s" % args)
        else:
            pass

    def _osc_server_read(self):
        while self.osc_server is not None:
            self.osc_server.recv(10)
