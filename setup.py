#!/usr/bin/env python3

from setuptools import setup

setup(
    name='supercollider',
    version='0.0.6',
    python_requires='>=3.9',
    description='Interact with the SuperCollider audio synthesis engine',
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author='Daniel Jones',
    author_email='dan-code@erase.net',
    url='https://github.com/ideoforms/supercollider',
    packages=['supercollider'],
    install_requires=['python-osc'],
    keywords=('sound', 'music', 'supercollider', 'synthesis'),
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis',
        'Topic :: Artistic Software',
        'Topic :: Communications',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
