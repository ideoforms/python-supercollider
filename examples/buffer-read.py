#!/usr/bin/env python3 

"""
Example: Read and play an audio file.

Before running this script, the SC server must be started, and the following
SynthDef stored:

SynthDef(\playbuf, { |out = 0, bufnum = 0, gain = 0.0|
    var data = PlayBuf.ar(1, bufnum, loop: 1) * gain.dbamp;
    Out.ar(out, Pan2.ar(data));
}).store;

You will also need to download some sample audio:
curl https://nssdc.gsfc.nasa.gov/planetary/sound/apollo_13_problem.wav -o apollo.wav
"""

AUDIO_FILE = "apollo.wav"

from supercollider import Server, Synth, Buffer
import time

#-------------------------------------------------------------------------------
# Create connection to default server on localhost:57110
#-------------------------------------------------------------------------------
server = Server()

#-------------------------------------------------------------------------------
# Read sample data into a Buffer.
#-------------------------------------------------------------------------------
buf = Buffer.read(server, AUDIO_FILE)
buf_info = buf.get_info()
print("Read buffer, sample rate %d, duration %.1fs" % (buf_info["sample_rate"], buf_info["num_frames"] / buf_info["sample_rate"]))

#-------------------------------------------------------------------------------
# Calculate the required playback rate (akin to SC BufRateScale.kr)
# and begin playback.
#-------------------------------------------------------------------------------
server_status = server.get_status()
server_sample_rate = server_status["sample_rate_nominal"]
buffer_sample_rate = buf_info["sample_rate"]
rate = buffer_sample_rate / server_sample_rate
synth = Synth(server, 'playbuf', {"buffer": buf, "rate": rate})

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    synth.free()
    buf.free()
