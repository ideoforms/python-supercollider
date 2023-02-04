import random
import pythonosc
from pythonosc.osc_server import AsyncIOOSCUDPServer, ThreadingOSCUDPServer, BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
import logging
import threading
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

        Args:
            hostname (str): Hostname or IP address of the server
            port (int): Port of the server
        """

        def epo_dummy_handler(address, *args):
            print(f"{address}: {args}")
        self.po_server_address = ("127.0.0.1", 57130)
        self.po_client_address = (hostname, port)
        self.po_dispatcher = Dispatcher()
        self.po_dispatcher.map("/n_set", self.po_dummy_handler)
        self.po_dispatcher.map("/b_info", self.po_dummy_handler)
        self.po_dispatcher.map("/b_setn", self.po_dummy_handler)
        self.po_dispatcher.map("/done", self.po_dummy_handler)
        self.po_dispatcher.map("/status.reply", self.po_dummy_handler)
        self.po_dispatcher.map("/version.reply", self.po_dummy_handler)
        self.po_dispatcher.map("/synced", self.po_dummy_handler)
        self.po_dispatcher.map("/g_queryTree.reply", self.po_dummy_handler)

        self.po_osc_client = SimpleUDPClient(hostname, port)
        self.po_osc_client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.po_osc_client._sock.bind(('',0))
        self.po_server_address = (hostname, self.po_osc_client._sock.getsockname()[1])
        ThreadingOSCUDPServer.allow_reuse_address = True
        self.po_osc_server = ThreadingOSCUDPServer(self.po_server_address, self.po_dispatcher)
        print(f'Chosen Address @ {self.po_server_address}')
        #self.po_osc_server.serve_forever()
        #self.po_osc_client_thread = threading.Thread(target=self._client_listen)
        #self.po_osc_client_thread.setDaemon(True)
        #self.running = True
        #self.po_osc_client_thread.start()
        self.po_osc_server_thread = threading.Thread(target=self._osc_server_listen)
        self.po_osc_server_thread.setDaemon(True)
        self.po_osc_server_thread.start()
        self.po_sync_event = threading.Event()
        self.sync()

    def po_dummy_handler(self, address, *args):
        print(f"{address}: {args}")

    def sync(self, num = None):
        self.po_osc_client.send_message("/sync", num)
        self._await_response("/synced", None)
    def _client_listen(self):
        print(f'Client Listening')
        self.po_osc_client._sock.setblocking(1)
        while self.running:
            data, server = self.po_osc_client._sock.recvfrom(57110)
            print(data, server)
    def _osc_server_listen(self):
        print(f'OSC Serving @ {self.po_server_address}')
        self.po_osc_server.serve_forever()
        print(f'OSC Serving @ {self.po_server_address}')

    def callback_with_timeout(self, *args, rv=None):
        self.po_sync_event.set()
        print(args)

    def _await_response(self, address, match_args=()):


        self.po_dispatcher.map(address, self.callback_with_timeout)
        responded_before_timeout = self.po_sync_event.wait(0.25)
        if not responded_before_timeout:
            print("Not responding!")
        elif responded_before_timeout:
            self.po_sync_event.clear()

        self.po_dispatcher.unmap(address, self.callback_with_timeout)
