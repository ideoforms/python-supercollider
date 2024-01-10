import random
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
import logging
from threading import Thread, Event
from . import globals
from .exceptions import SuperColliderConnectionError
import socket 

logger = logging.getLogger(__name__)

class Server(object):
    def __init__(self, hostname="127.0.0.1", port=57110):
        """
        Create a new Server object, which is a local representation of a remote
        SuperCollider server.

        Supercollider communication is (unfortunatelly for UDP) made in the same
        port used by the client. Hence, the OSC server and the UDP client should
        share the same port. Setting this up is possible, but slightly harder.
        Check this github issue to see how this is possible with pythonosc:
        https://github.com/attwad/python-osc/issues/41

        Args:
            hostname (str): Hostname or IP address of the server
            port (int): Port of the server
        """

        # UDP Client for sending messages
        self.client_address = (hostname, port)
        self.sc_client = SimpleUDPClient(hostname, port)
        self.sc_client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sc_client._sock.bind(('',0))

        # OSC Server for receiving messages.
        self.dispatcher = Dispatcher()
        self.osc_server_address = ("127.0.0.1", self.sc_client._sock.getsockname()[1])
        ThreadingOSCUDPServer.allow_reuse_address = True
        self.osc_server = ThreadingOSCUDPServer(self.osc_server_address, self.dispatcher)

        self.osc_server_thread = Thread(target=self._osc_server_listen, daemon=True)
        self.osc_server_thread.start()

        # Callbacks witout await_response timeout
        # self.dispatcher.map("/example", self.dummy_handler)

        # For callback timeouts
        self.event = Event()
        
        # SC node ID for Add actions
        self.id = 0

        self.sync()

    # ------------------- Handlers ------------------- #
    # TODO: Move handlers to a separate file or class
    def dummy_handler(self, address, *args):
        pass

    def simple_handler(self, address, *args):
        return args

    def param_handler(self, address, *args):
        return args[2]

    def buf_handler(self, address, *args):
        return args[3:]

    def status_handler(self, address, *args):
        status_dict = {
                "num_ugens": args[1],
                "num_synths": args[2],
                "num_groups": args[3],
                "num_synthdefs": args[4],
                "cpu_average": args[5],
                "cpu_peak": args[6],
                "sample_rate_nominal": args[7],
                "sample_rate_actual": args[8]}
            
        return status_dict

    def version_handler(self, *args):
        version_dict = {
                "program_name": args[1],
                "version_major": args[2],
                "version_minor": args[3],
                "version_patch": args[4],
                "git_branch": args[5],
                "commit_hash": args[6]}
            
        return version_dict
    
    # ------------------- Client Messages ------------------- #
    def _send_msg(self, address, *args):
        self.sc_client.send_message(address, [*args])

    def sync(self, ping_id = 1):
        self._send_msg("/sync", ping_id)
        return self._await_response("/synced", None, self.simple_handler)

    def query_tree(self, group=None):
        self._send_msg("/g_queryTree", group.id if group else 0, 0)
        return self._await_response("/g_queryTree.reply", callback=self.simple_handler)
    
    def get_status(self):
        self._send_msg("/status")

        return self._await_response("/status.reply", None, self.status_handler)

    def get_version(self):
        self._send_msg("/version")

        return self._await_response("/version.reply", None, self.version_handler)

    # ------------------- Callback Timeout Logic ------------------- #
    def _await_response(self, address, match_args=(), callback=None):

        rv = None
        # Sets the thread event when message is received
        # It also overwrites the callback (dispatcher) function to capture the return value.
        # This is necessary because the dispatcher handler can't return anything.
        # Make sure to unmap the callback before it is overwritten to avoid duplicate callbacks.
        def _callback_with_timeout(*args):
            self.event.set()
            if callback:
                nonlocal rv
                rv = callback(address, *args[1:])

        self.dispatcher.map(address, _callback_with_timeout)

        responded_before_timeout = self.event.wait(globals.RESPONSE_TIMEOUT)
        if not responded_before_timeout:
            raise SuperColliderConnectionError("Connection to SuperCollider server timed out. Is scsynth running?")
        elif responded_before_timeout:
            self.event.clear()

        self.dispatcher.unmap(address, _callback_with_timeout)

        return rv

    # ------------------- OSC Server Thread ------------------- #
    def _osc_server_listen(self):
        logger.debug(f'Python OSC Serving @ {self.osc_server_address}')
        self.osc_server.serve_forever()
        logger.warning(f'OSC Server @ {self.osc_server_address} Stopped!')
