#!/usr/bin/env python3

"""
Slightly contrived approach to additive synthesis,
demonstrating how a Group can be used to contain 
multiple Synths.

Requires the \sine synth defined in hello-world.py.
"""

fundamental_min = 220
fundamental_max = 1760
partial_count = 5
partial_attenuate = -6.0
tone_duration = 0.1

from supercollider import Server, Group, Synth

import time
import random

def create_group(freq):
    group = Group(server)
    for n in range(1, partial_count + 1):
        Synth(server, "sine", {
            "freq": freq * n * random.uniform(0.99, 1.01),
            "gain": partial_attenuate * n
        }, target=group)
    return group

server = Server()

try:
    while True:
        freq = random.uniform(fundamental_min, fundamental_max)
        group = create_group(freq)
        time.sleep(tone_duration)
        group.free()
except KeyboardInterrupt:
    group.free()
