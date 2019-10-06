import liblo
import logging
import threading

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
            "/n_set": {}
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
        def _handle_status(args):
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
        self.handlers["/status.reply"] = _handle_status
        self._send_msg("/status")

    def _send_msg(self, msg, *args):
        liblo.send(self.client_address, msg, *args)

    def _add_handler(self, address, node_id, parameter, fn):
        assert address in self.handlers
        self.handlers[address][(node_id, parameter)] = fn

    def _osc_handler(self, address, args):
        logger.debug("Received OSC: %s, %s" % (address, args))
        if address == "/n_set":
            node_id, parameter, value = tuple(args)
            if (node_id, parameter) in self.handlers["/n_set"]:
                handler = self.handlers["/n_set"][(node_id, parameter)]
                handler(value)
        elif address == "/status.reply":
            if self.handlers[address]:
                self.handlers[address](args)
        elif address == "/fail":
            logger.warning("Received failure: %s" % args)
        else:
            pass

    def _osc_server_read(self):
        while True:
            self.osc_server.recv(10)
