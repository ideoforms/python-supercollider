#!/usr/bin/env python3 

#-------------------------------------------------------------------------------
# Example of buffer creation and playback.
#
# Before running this script, the SC server must be started, and the following
# SynthDef stored:
#
# SynthDef(\playbuf, { |out = 0, bufnum = 0, gain = 0.0|
#     var data = PlayBuf.ar(1, bufnum, loop: 1) * gain.dbamp;
#     Out.ar(out, Pan2.ar(data));
# }).store;
#-------------------------------------------------------------------------------

from supercollider import Server, Synth, Buffer

import time
import math
import random

#-------------------------------------------------------------------------------
# Create connection to default server on localhost:57110
#-------------------------------------------------------------------------------
server = Server()

#-------------------------------------------------------------------------------
# Create a Buffer, loop playback, and periodically rewrite its contents
# with uniformly random samples.
#-------------------------------------------------------------------------------
buf = Buffer.alloc(server, 1024)
print("Created buffer: %s" % buf.info)

synth = Synth(server, 'playbuf', { "buffer" : buf, "gain" : -18.0 })
try:
    while True:
        buf.setn([ random.uniform(-1, 1) for n in range(buf.num_frames) ])
        time.sleep(0.1)
except KeyboardInterrupt:
    synth.free()
    buf.free()
