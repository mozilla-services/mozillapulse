#!/usr/bin/env python

from distutils.core import setup

setup(name='MozillaPulse',
      version='.1',
      description='Library for interacting with the Mozilla Pulse message broker',
      author='Christian Legnitto',
      author_email='clegnitto@mozilla.com',
      packages=['mozillapulse','mozillapulse.messages'],
)

