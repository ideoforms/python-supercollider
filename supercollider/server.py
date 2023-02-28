import random
from pythonosc.osc_server import ThreadingOSCUDPServer, AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
import logging
from threading import Thread, Event
import asyncio
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

        self.osc_server_thread = Thread(target=self._osc_server_listen)
        self.osc_server_thread.setDaemon(True)
        self.osc_server_thread.start()


        # Setting handlers
        self.dispatcher.map("/n_set", self.simple_handler)
        #self.dispatcher.map("/b_info", self.dummy_handler)
        #self.dispatcher.map("/b_setn", self.dummy_handler)
        #self.dispatcher.map("/done", self.dummy_handler)
        #self.dispatcher.map("/status.reply", self.dummy_handler)
        #self.dispatcher.map("/version.reply", self.dummy_handler)
        #self.dispatcher.map("/synced", self.simple_handler)
        #self.dispatcher.map("/g_queryTree.reply", self.simple_handler)
        self.dispatcher.set_default_handler(self._osc_handler)

        # For timeout callbacks
        self.sync_event = Event()
        
        # scsynth node ID
        self.id = 0

        self.sync()


    def _send_msg(self, address, *args):
        self.sc_client.send_message(address, [*args])

    def simple_handler(self, address, *args):
        #print(f"Simple Handler - {address}: {args}")
        return args

    def param_handler(self, address, *args):
        return args[2]

    def buf_handler(self, address, *args):
        #print(f"Buffer Handler - {address}: {args}")
        return args[3:]

    def sync(self, num = 1):
        self._send_msg("/sync", num)
        #self.sc_client.send_message("/sync", num)
        return self._await_response("/synced", None, self.simple_handler)

    def query_tree(self, group=None):
        self._send_msg("/g_queryTree", group.id if group else 0, 0)
        return self._await_response("/g_queryTree.reply", callback=self.simple_handler)
    
    def get_status(self):
        self._send_msg("/status")


        def status_handler(address, *args):
            """Converts the status reply into a dictionary with the following keys: 
                num_ugens, num_synths, num_groups, num_synthdefs, cpu_average, cpu_peak, sample_rate_nominal, sample_rate_actual
                add 1 to the index of the args list to get the value for each"""
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

        return self._await_response("/status.reply", None, status_handler)

    def get_version(self):
        self._send_msg("/version")
        def version_handler(*args):
            """Converts the version reply into a dictionary with the following keys: 
            program_name, version_major, version_minor, version_patch, git_branch, commit_hash"""
            version_dict = {
                    "program_name": args[1],
                    "version_major": args[2],
                    "version_minor": args[3],
                    "version_patch": args[4],
                    "git_branch": args[5],
                    "commit_hash": args[6]}
            
            return version_dict

        return self._await_response("/version.reply", None, version_handler)

    def dummy_handler(self, address, *args):
        print(f"Dummy Handler - {address}: {args}")

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

    def _await_response(self, address, match_args=(), callback=_osc_handler):

        rv = None
        def _callback_with_timeout(*args):
            self.sync_event.set()
            if callback:
                nonlocal rv
                rv = callback(address, *args[1:])
                #print(f"Timeout rv: {rv}")

        self.dispatcher.map(address, _callback_with_timeout)
        responded_before_timeout = self.sync_event.wait(0.25)
        if not responded_before_timeout:
            raise SuperColliderConnectionError("Connection to SuperCollider server timed out. Is scsynth running?")
        elif responded_before_timeout:
            self.sync_event.clear()
        self.dispatcher.unmap(address, _callback_with_timeout)
        #print(f"rv: {rv}")  
        return rv

    def _osc_server_listen(self):
        logger.debug(f'Python OSC Serving @ {self.osc_server_address}')
        self.osc_server.serve_forever()
        logger.warning(f'OSC Server @ {self.osc_server_address} Stopped!')
