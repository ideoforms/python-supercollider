from __future__ import annotations
from . import globals
from .globals import SAMPLE_FORMAT_FLOAT
from .globals import HEADER_FORMAT_WAV
from typing import TYPE_CHECKING, Callable
import os

if TYPE_CHECKING:
    from .server import Server

class Buffer:
    def __init__(self,
                 server: Server,
                 id: int = 0):
        """
        Creates a Buffer object, but does not allocate any memory for it. This constructor should only be used if
        you want to create an object to interface with an already-created buffer.

        If the `id` passed is None, the created Buffer will have an automatically-allocated id.

        Args:
            server (Server): The SC server on which the Group is created.
            id (int): The buffer's unique ID, or None to auto-allocate.
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
    def alloc(cls, server: Server, num_frames: int, num_channels: int = 1, blocking: bool = True):
        """
        Create and allocate a new Buffer.

        Args:
            server (Server): The SC server on which the Buffer is allocated.
            num_frames (int): The number of frames to allocate.
            num_channels (int): The number of channels in the buffer.
            blocking (bool): Wait for the alloc task to complete before returning.

        Returns:
            A new Buffer object.
        """
        buf = Buffer(server, id=None)
        buf.num_frames = num_frames
        buf.num_channels = num_channels
        buf.server._send_msg("/b_alloc", buf.id, num_frames, num_channels)

        if blocking:
            buf.server._await_response("/done", ["/b_alloc", buf.id])

        return buf

    @classmethod
    def read(cls,
             server: Server,
             path: str,
             start_frame: int = 0,
             num_frames: int = 0,
             blocking: bool = True) -> Buffer:
        """
        Create a new Buffer and read its contents from disk.

        Args:
            server (Server): The SC server on which the Buffer is created.
            path (str): The pathname to the audio file to read.
            start_frame (int): The frame index to start reading from.
            num_frames (int): The number of frames to read.
            blocking (bool): Wait for the read task to complete before returning.

        Returns:
            A new Buffer object.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        if not os.path.exists(path):
            raise FileNotFoundError("File not found: %s" % path)

        if not path.startswith("/"):
            path = os.path.abspath(path)
        buf = Buffer(server, id=None)
        buf.server._send_msg("/b_allocRead", buf.id, path, start_frame, num_frames)

        def _handler(address, *args):
            return args

        if blocking:
            buf.server._await_response("/done", ["/b_allocRead", buf.id], _handler)

        return buf

    def write(self,
              path: str,
              header_format: int = HEADER_FORMAT_WAV,
              sample_format: int = SAMPLE_FORMAT_FLOAT,
              num_frames: int = -1,
              start_frame: int = 0,
              leave_open: bool = False,
              blocking: bool = True):
        """
        Write the Buffer's contents to an audio file.

        Args:
            path (str): Pathname to the audio file to write.
            header_format (str): Format of the file. See `supercollider.globals` for supported formats.
            sample_format (str):  Format of the audio samples. See `supercollider.globals` for supported formats.
            num_frames (int): The number of frames to write. Defaults to the full buffer.
            start_frame (int): Index of the first frame to write.
            leave_open (bool): Whether to leave the file open after write.
            blocking (bool): Wait for the write task to complete before returning.
        """
        self.server._send_msg("/b_write", self.id, path, header_format, sample_format,
                              num_frames, start_frame, int(leave_open))

        if blocking:
            self.server._await_response("/done", ["/b_write", self.id])

    def get(self, start_index: int = 0, count: int = 1024) -> list[float]:
        """
        Query the Buffer's contents.

        Note that, as per the SuperCollider Command Reference, this is not designed to query
        a lot of samples.

        https://doc.sccode.org/Reference/Server-Command-Reference.html

        Args:
            start_index (int): Index of first frame in the Buffer to read from.
            count (int): Number of samples to retrieve.
        """

        def _handler(address, *args):
            return args[3:]

        self.server._send_msg("/b_getn", self.id, start_index, count)
        return self.server._await_response("/b_setn", [self.id], _handler)

    def set(self, samples: list[float], start_index: int = 0):
        """
        Set the Buffer's contents to the values given in the supplied float array.

        Args:
            samples (List[float]): Array of floats to write to the Buffer.
            start_index (int): Index of first frame in the Buffer to write to.
        """
        self.server._send_msg("/b_setn", self.id, start_index, len(samples), *samples)

    def fill(self, count: int, value: float, start_index: int = 0):
        """
        Fill the Buffer's contents with a specified sample.

        Args:
            count (int): The number of frames to write.
            value (float): The sample to write.
            start_index (int): Index of first frame in the Buffer to write to.
        """
        self.server._send_msg("/b_fill", self.id, start_index, count, value)

    def free(self):
        """
        Free the buffer.
        """
        self.server._send_msg("/b_free", self.id)

    def get_info(self, callback: Callable = None, blocking: bool = True):
        """
        Returns info about the Buffer.

        Example:
            >>> buffer.info
            {'num_frames': 1024, 'num_channels': 1, 'sample_rate': 44100.0}
        """

        def _handler(address, *args):
            rv = {
                "num_frames": args[1],
                "num_channels": args[2],
                "sample_rate": args[3]
            }

            return rv

        self.server._send_msg("/b_query", self.id)
        if blocking:
            return self.server._await_response("/b_info", [self.id], _handler)
        else:
            self.server.dispatcher.map("/b_info", lambda *args: callback(_handler(*args)))
