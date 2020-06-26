import os
import wave
import struct
import pytest
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
        input_frames = list(struct.unpack("H" * len(data), input_binary))
        data_uint16 = [ int(sample * 32768) for sample in data ]
        assert input_frames == data_uint16

    os.unlink(output_path)

def test_buffer_read(server):
    output_path = "/tmp/output.wav"
    data = [ 0.01 * n for n in range(100) ]

    with wave.open(output_path, "w") as fd:
        fd.setnchannels(1)
        fd.setsampwidth(2)
        fd.setframerate(44100)
        output_frames = [ int(sample * 32768) for sample in data ]
        output_binary = struct.pack("H" * len(output_frames), *output_frames)
        fd.writeframes(output_binary)
    buf = supercollider.Buffer.read(server, output_path)
    samples = buf.get(0, 100)
    assert data == pytest.approx(samples, abs=0.0001)
