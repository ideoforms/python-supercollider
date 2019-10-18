# Contributing

## Tests

To run unit tests:

* start the SuperCollider server
* run `python3 setup.py test`

## Distribution

To push to PyPi:

* increment version in `setup.py`
* tag and create GitHub release
* `python3 setup.py sdist`
* `twine upload dist/supercollider-x.y.z.tar.gz`
