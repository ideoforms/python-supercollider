from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from threading import Thread, Event
from .exceptions import SuperColliderConnectionError
from typing import Optional, Callable
from . import globals
import logging
import socket

logger = logging.getLogger(__name__)

class Server:
    def __init__(self, hostname: str = "127.0.0.1", port: int = 57110):
        """
        Create a new Server object, which is a local representation of a remote
        SuperCollider server.

        Supercollider communication is (unfortunatelly for UDP) made in the same
        port used by the client. Hence, the OSC server and the UDP client should
        share the same port. Setting this up is possible, but slightly harder.
        Check this github issue to see how this is possible with python-osc:
        https://github.com/attwad/python-osc/issues/41

        Args:
            hostname (str): Hostname or IP address of the server
            port (int): Port of the server
        """

        # UDP Client for sending messages
        self.client_address = (hostname, port)
        self.sc_client = SimpleUDPClient(hostname, port)
        self.sc_client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sc_client._sock.bind(('', 0))

        # OSC Server for receiving messages.
        self.dispatcher = Dispatcher()
        self.osc_server_address = ("127.0.0.1", self.sc_client._sock.getsockname()[1])
        ThreadingOSCUDPServer.allow_reuse_address = True
        self.osc_server = ThreadingOSCUDPServer(self.osc_server_address, self.dispatcher)

        self.osc_server_thread = Thread(target=self._osc_server_listen, daemon=True)
        self.osc_server_thread.start()

        # For callback timeouts
        self.event = Event()

        # SC node ID for Add actions
        self.id = 0

        self.sync()

    #--------------------------------------------------------------------------------
    # Client messages
    #--------------------------------------------------------------------------------

    def _send_msg(self, address: str, *args) -> None:
        self.sc_client.send_message(address, [*args])

    def sync(self, ping_id: int = 1):
        def _handler(address, *args):
            return args

        self._send_msg("/sync", ping_id)
        return self._await_response("/synced", None, _handler)

    def query_tree(self, group=None):
        def _handler(address, *args):
            return args

        self._send_msg("/g_queryTree", group.id if group else 0, 0)
        return self._await_response("/g_queryTree.reply", callback=_handler)

    def get_status(self):
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

        def _handler(address, *args):
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

        self._send_msg("/status")

        return self._await_response("/status.reply", None, _handler)

    def get_version(self) -> dict:
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

        def _handler(*args):
            version_dict = {
                "program_name": args[1],
                "version_major": args[2],
                "version_minor": args[3],
                "version_patch": args[4],
                "git_branch": args[5],
                "commit_hash": args[6]}

            return version_dict

        self._send_msg("/version")

        return self._await_response("/version.reply", None, _handler)

    #--------------------------------------------------------------------------------
    # Callback timeout logic
    #--------------------------------------------------------------------------------

    def _await_response(self,
                        address: str,
                        match_args=(),
                        callback: Optional[Callable] = None) -> list:
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
        if responded_before_timeout:
            self.event.clear()
        else:
            raise SuperColliderConnectionError("Connection to SuperCollider server timed out. Is scsynth running?")

        self.dispatcher.unmap(address, _callback_with_timeout)

        return rv

    #--------------------------------------------------------------------------------
    # OSC server thread
    #--------------------------------------------------------------------------------

    def _osc_server_listen(self):
        logger.debug(f'Listening for OSC messages on @ {self.osc_server_address}')
        self.osc_server.serve_forever()
        logger.warning(f'OSC server @ {self.osc_server_address} stopped')

    def clear_all_handlers(self):
        """
        Useful for cleaning up after using handlers with blocking=False.
        """
        for address, handlers in self.dispatcher._map.items():
            for handler in handlers.copy():
                self.dispatcher.unmap(address, handler)
