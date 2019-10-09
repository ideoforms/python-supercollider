#!/usr/bin/env python3

from setuptools import setup

setup(
    name = 'supercollider',
    version = '0.0.3',
    description = 'Interact with the SuperCollider audio synthesis engine',
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    author = 'Daniel Jones',
    author_email = 'dan-code@erase.net',
    url = 'https://github.com/ideoforms/supercollider',
    packages = ['supercollider'],
    install_requires = ['pyliblo >= 0.9.1'],
    keywords = ('sound', 'music', 'supercollider', 'synthesis'),
    classifiers = [
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Artistic Software',
        'Topic :: Communications',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ]
)
