# Python client for SuperCollider

A lightweight Python module to control the [SuperCollider](https://supercollider.github.io) audio synthesis engine.

## Installation

To install the client library:

```python
pip3 install supercollider
```

## Usage

Before using the library, start the SuperCollider server, either through the SuperCollider GUI or with `scsynth -u 57110`.

Within the SC client, create the below SynthDef:

```
SynthDef(\sine, { |out = 0, freq = 440.0, gain = 0.0|
    Out.ar(out, SinOsc.ar(freq) * gain.dbamp);
}).store;
```

From Python, you can now create and trigger Synths:

```python
from supercollider import Server, Synth

server = Server()

synth = Synth(server, "sine", { "freq" : 440.0, "gain" : -12.0 })
synth.set("freq", 880.0)
```

For further examples, see [examples](https://github.com/ideoforms/python-supercollider/tree/master/examples).

## License

This library is made available under the terms of the MIT license.

## Contributors

 - Thanks to [Itaborala](https://github.com/Itaborala) for porting from liblo to python-osc

## See also

* If you want a more comprehensive framework that lets you construct and compile SynthDefs from Python, take a look at [Supriya](https://github.com/josiah-wolf-oberholtzer/supriya).
* For an excellent Python + SuperCollider live coding environment, check out [FoxDot](https://foxdot.org)
