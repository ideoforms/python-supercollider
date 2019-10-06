from . import globals

class Buffer(object):
    """ Encapsulates a SuperCollider Buffer object.
    """
    def __init__(self, server, num_frames, num_channels=1):
        """
        Create a new Buffer.

        Args:
            server (Server): The SC server on which the Group is created.
        """
        self.server = server
        self.num_frames = num_frames
        self.num_channels =  num_channels

        self.id = globals.LAST_BUFFER_ID
        globals.LAST_BUFFER_ID += 1

        self.server._send_msg("/b_alloc", self.id, num_frames, num_channels)

    def setn(self, samples):
        self.server._send_msg("/b_setn", self.id, 0, len(samples), *samples)

    def fill(self, count, value):
        self.server._send_msg("/b_fill", self.id, 0, count, value)

    def free(self):
        """
        Free the buffer.
        """
        self.server._send_msg("/b_free", self.id)
