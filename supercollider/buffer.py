from . import globals
import os

class Buffer(object):
    """ Encapsulates a SuperCollider Buffer object.
    """
    def __init__(self, server, id=None):
        """
        Create a new Buffer.

        Args:
            server (Server): The SC server on which the Group is created.
        """
        self.server = server
        self.num_frames = None
        self.num_channels = None

        if id is None:
            self.id = globals.LAST_BUFFER_ID
            globals.LAST_BUFFER_ID += 1
        else:
            self.id = id

    @classmethod
    def alloc(cls, server, num_frames, num_channels=1):
        buf = Buffer(server)
        buf.num_frames = num_frames
        buf.num_channels = num_channels
        buf.server._send_msg("/b_alloc", buf.id, num_frames, num_channels)
        return buf

    @classmethod
    def read(cls, server, path, start_frame=0, num_frames=0):
        if not path.startswith("/"):
            path = os.path.abspath(path)
        buf = Buffer(server)
        buf.server._send_msg("/b_allocRead", buf.id, path, start_frame, num_frames)
        return buf

    def setn(self, samples):
        self.server._send_msg("/b_setn", self.id, 0, len(samples), *samples)

    def fill(self, count, value):
        self.server._send_msg("/b_fill", self.id, 0, count, value)

    def free(self):
        """
        Free the buffer.
        """
        self.server._send_msg("/b_free", self.id)

    def get_info(self, fn):
        """
        Get the buffer's status.
        """

        def _handler(*args):
            rv = {
                "num_frames" : args[0],
                "num_channnels" : args[1],
                "sample_rate"  : args[2]
            }
            fn(rv)

        self.server._send_msg("/b_query", self.id)
        self.server._add_handler("/b_info", [ self.id ], _handler)
