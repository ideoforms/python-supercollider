import random
import pythonosc
from pythonosc.osc_server import AsyncIOOSCUDPServer, ThreadingOSCUDPServer, BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
import logging
from threading import Thread, Event
#from . import globals
#from .exceptions import SuperColliderConnectionError
import asyncio
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

        self.osc_server_thread = Thread(target=self._osc_server_listen)
        self.osc_server_thread.setDaemon(True)
        self.osc_server_thread.start()

        # Setting handlers
        self.dispatcher.map("/n_set", self.dummy_handler)
        self.dispatcher.map("/b_info", self.dummy_handler)
        self.dispatcher.map("/b_setn", self.dummy_handler)
        self.dispatcher.map("/done", self.dummy_handler)
        self.dispatcher.map("/status.reply", self.dummy_handler)
        self.dispatcher.map("/version.reply", self.dummy_handler)
        self.dispatcher.map("/synced", self.dummy_handler)
        self.dispatcher.map("/g_queryTree.reply", self.dummy_handler)

        # For timeout callbacks
        self.sync_event = Event()
        
        # scsynth node ID
        self.id = 0

        self.sync()

    def sync(self, num = 1):
        self._send_msg("/sync", num)
        #self.sc_client.send_message("/sync", num)
        self._await_response("/synced", None)


    def dummy_handler(self, address, *args):
        print(f"Dummy Handler - {address}: {args}")

    def callback_with_timeout(self, *args, rv=None):
        self.sync_event.set()

    def _send_msg(self, address, *args):
        self.sc_client.send_message(address, [*args])

    def _await_response(self, address, match_args=()):


        self.dispatcher.map(address, self.callback_with_timeout)
        responded_before_timeout = self.sync_event.wait(0.25)
        if not responded_before_timeout:
            print("Connection to SuperCollider server timed out. Is scsynth running?")
        elif responded_before_timeout:
            self.sync_event.clear()
        self.dispatcher.unmap(address, self.callback_with_timeout)

    def _osc_server_listen(self):
        print(f'Python OSC Serving @ {self.osc_server_address}')
        self.osc_server.serve_forever()
        print(f'OSC Server @ {self.osc_server_address} Stopped!')
