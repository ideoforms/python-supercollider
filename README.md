# Simple Python client for SuperCollider using python-osc

# Current status: `python-osc` version still not working

A lightweight Python module to control the [SuperCollider](https://supercollider.github.io) audio synthesis engine.
This project is forked from [ideoforms/python-supercollider](https://github.com/ideoforms/python-supercollider), hoping to continue and improve ideoform's work. 

### Motivation
This fork uses different dependencies. Specifically, it uses [python-osc](https://pypi.org/project/python-osc/) for OSC communication, instead of `pyliblo` (and `liblo` in general). There are a few reasons for this switch:
    + latest release of `pyliblo` was in 2015
    + `pyliblo3` is not frequently mantained
    + `liblo` sometimes is problematic to install, requiring compilation from source.
    + `python-osc` doesn't need external dependencies, there is frequent maintenance, and 20+ contributors

## Installation


Install the Python package:

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

## See also

* If you want a more comprehensive framework that lets you construct and compile SynthDefs from Python, take a look at [Supriya](https://github.com/josiah-wolf-oberholtzer/supriya).
* For an excellent Python + SuperCollider live coding environment, check out [FoxDot](https://foxdot.org)
