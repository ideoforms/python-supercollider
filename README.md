# Python client for SuperCollider

A lightweight Python module to control the [SuperCollider](https://supercollider.github.io) audio synthesis engine.

## Installation

The `liblo` library is required for the underlying OSC communications.

```
brew install liblo # macOS
apt-get install liblo7 # Linux
```

Install the Python package:

```python
pip3 install supercollider
```

## Usage

```python
from supercollider import Server, Synth

server = Server()

synth = Synth(server, "sine", { "freq" : 440.0, "gain" : -12.0 })
synth.set("freq", 880.0)
```

## See also

If you want a more fully-fledged approach that lets you construct and compile `SynthDef`s from Python, you'd be better with [Supriya](https://github.com/josiah-wolf-oberholtzer/supriya).
