#!/usr/bin/env python3 

"""
Example: Audio routing with buses.

Before running this script, the SC server must be started, and the following
SynthDefs stored:

SynthDef(\dust, { |out = 0, gain = 0.0|
	var data = Dust.ar(10) * gain.dbamp;
	Out.ar(out, Pan2.ar(data));
}).store;

SynthDef(\reverb, { |in = 0, out = 2|
	var data = In.ar(in, 2);
	data = FreeVerb.ar(data, 0.7, 0.8, 0.5);
	Out.ar(out, data);
}).store;
"""

from supercollider import Server, Synth, Buffer, AudioBus, ADD_TO_TAIL

import time

#-------------------------------------------------------------------------------
# Create connection to default server on localhost:57110
#-------------------------------------------------------------------------------
server = Server()

#-------------------------------------------------------------------------------
# Create a Buffer, read and play a sample.
#-------------------------------------------------------------------------------
bus = AudioBus(server, 2)
synth = Synth(server, 'dust', { "out": bus })
reverb = Synth(server, 'reverb', { "in": bus, "out": 0 }, target=server, action=ADD_TO_TAIL)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    bus.free()
    synth.free()
    reverb.free()
