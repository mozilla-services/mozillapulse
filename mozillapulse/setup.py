#!/usr/bin/env python

# This is a distutils setup script for the mozillapulse module.
# Install the module by running `python setup.py install`

from distutils.core import setup

setup(name="Mozilla Pulse Client Library",
      version='0.1',
      description="Mozilla-specific client library for connecting to the Mozilla Pulse message broker",
      author="Christian Legnitto",
      author_email="clegnitto@mozilla.com",
      packages=["mozillapulse"]
)
