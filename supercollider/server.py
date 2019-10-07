import liblo
import logging
import threading
from . import globals

logger = logging.getLogger(__name__)

OSC_CLIENT_PORT = 57150


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
        self.osc_server = liblo.Server(OSC_CLIENT_PORT)
        self.osc_server.add_method(None, None, self._osc_handler)
        self.osc_server_thread = threading.Thread(target=self._osc_server_read)
        self.osc_server_thread.setDaemon(True)
        self.osc_server_thread.start()
        self.handlers = {
            "/n_set": {},
            "/b_info": {},
            "/done": {},
            "/status.reply": None,
            "/version.reply": None
        }

    def get_status(self, fn):
        """
        Query the current Server status, including the number of active units, CPU
        load, etc.

        Args:
            fn (function): Callback to receive server status, which is passed a
                           dict of key/value pairs.

        Example:
            >>> server.get_status(lambda status: print(status))
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
            fn(args_dict)
        self._add_handler("/status.reply", None, _handler)
        self._send_msg("/status")

    def get_version(self, fn):
        """
        Query the current Server version.

        Args:
            fn (function): Callback to receive server version, which is passed a
                           dict of key/value pairs.

        Example:
            >>> server.get_version(lambda version: print(version))
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
            fn(args_dict)
        self._add_handler("/version.reply", None, _handler)
        self._send_msg("/version")

    def _send_msg(self, msg, *args):
        liblo.send(self.client_address, msg, *args)

    def _await_response(self, address, match_args):
        event = threading.Event()

        def callback():
            event.set()
        self._add_handler(address, match_args, callback)

        event.wait(globals.RESPONSE_TIMEOUT)

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
                handler = self.handlers["/n_set"][(node_id, parameter)]
                handler(value)
        elif address == "/b_info":
            buffer_id = args[0]
            values = args[1:]
            if (buffer_id,) in self.handlers["/b_info"]:
                handler = self.handlers["/b_info"][(buffer_id,)]
                handler(*values)
        elif address == "/status.reply" or address == "/version.reply":
            if self.handlers[address]:
                self.handlers[address](args)
        elif address == "/fail":
            logger.warning("Received failure: %s" % args)
        elif address == "/done":
            if tuple(args) in self.handlers["/done"]:
                self.handlers["/done"][tuple(args)]()
        else:
            pass

    def _osc_server_read(self):
        while True:
            self.osc_server.recv(10)
