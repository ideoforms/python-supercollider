#!/usr/bin/env python3 

"""
Example: Write the contents of a Buffer to disk.
"""

from supercollider import Server, Synth, Buffer, HEADER_FORMAT_WAV
import math

OUTPUT_FILE = "/tmp/440.wav"

#-------------------------------------------------------------------------------
# Create connection to default server on localhost:57110
#-------------------------------------------------------------------------------
server = Server()

#-------------------------------------------------------------------------------
# Create a Buffer, generate a 440Hz sine, and write to a .wav.
#-------------------------------------------------------------------------------
length = 1024
server_status = server.get_status()
sample_rate = server_status["sample_rate_nominal"]

buf = Buffer.alloc(server, length)
buf.set([ math.sin(n * math.pi * 2.0 * 440.0 / sample_rate) for n in range(int(length)) ])
buf.write(OUTPUT_FILE, HEADER_FORMAT_WAV)
print("Written buffer to %s" % OUTPUT_FILE)
