# Contributing

## Tests

To run unit tests:

* start the SuperCollider server
* store the following synthdef: `SynthDef(\sine, { |out = 0, freq = 440.0| Out.ar(out, SinOsc.ar(freq)); }).store;`
* run `python3 setup.py test`

## Distribution

To push to PyPi:

* increment version in `setup.py`
* tag and create GitHub release
* `python3 setup.py sdist`
* `twine upload dist/supercollider-x.y.z.tar.gz`
