# Python client for SuperCollider

A lightweight Python module to control the [SuperCollider](https://supercollider.github.io) audio synthesis engine.

## Usage

```python
pip3 install supercollider
```

## Example

```python
from supercollider import Server, Synth

server = Server()

synth = Synth(server, "sine", { "freq" : 440.0, "gain" : -12.0 })
synth.set("freq", 880.0)
synth.get("freq", lambda n: print(n))
```
