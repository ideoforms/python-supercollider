#!/usr/bin/env python3

"""
Example: Create a sine wave synth.

Before running this script, the SC server must be started, and the following
SynthDef stored:

SynthDef(\sine, { |out = 0, freq = 440.0, gain = 0.0|
    Out.ar(out, SinOsc.ar(freq) * gain.dbamp);
}).store;
"""

from supercollider import Server, Synth
import time

#-------------------------------------------------------------------------------
# Create connection to default server on localhost:57110
#-------------------------------------------------------------------------------
server = Server()
print("Created server")
print("Server version: %s" % server.get_version())

#-------------------------------------------------------------------------------
# Create a Synth, set its parameter, query the parameter, and free it.
#-------------------------------------------------------------------------------
try:
    synth = Synth(server, "sine", { "freq" : 440.0, "gain" : -18.0 })
    print("Created synth")
    print("Frequency: %.1f" % synth.get("freq"))
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    synth.free()
    print("Freed synth")
