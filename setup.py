#!/usr/bin/env python3

from setuptools import setup

setup(
    name = 'supercollider',
    version = '0.0.5',
    description = 'Interact with the SuperCollider audio synthesis engine',
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    author = 'Daniel Jones',
    author_email = 'dan-code@erase.net',
    url = 'https://github.com/ideoforms/supercollider',
    packages = ['supercollider'],
    install_requires = ['cython', 'pyliblo >= 0.9.1'],
    keywords = ('sound', 'music', 'supercollider', 'synthesis'),
    classifiers = [
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis',
        'Topic :: Artistic Software',
        'Topic :: Communications',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    setup_requires = ['pytest-runner'],
    tests_require = ['pytest']
)
