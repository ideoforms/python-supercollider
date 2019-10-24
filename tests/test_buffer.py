import os
import wave
import struct
import supercollider

from tests.shared import server

def test_buffer_write(server):
    length = 1024

    output_path = "/tmp/output.wav"
    data = [ 0.01 * n for n in range(100) ]
    buf = supercollider.Buffer.alloc(server, len(data))
    buf.set(data)

    buf.write(output_path, supercollider.HEADER_FORMAT_WAV, supercollider.SAMPLE_FORMAT_INT16)
    assert os.path.exists(output_path)

    with wave.open(output_path, "r") as fd:
        input_binary = fd.readframes(len(data))
        print(len(input_binary))
        input_frames = list(struct.unpack("H" * len(data), input_binary))
        data = [ int(f * 32768) for f in data ]
        assert input_frames == data

    os.unlink(output_path)
