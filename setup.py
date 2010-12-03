#!/usr/bin/env python

from distutils.core import setup

setup(name='MozillaPulse',
      version='.3',
      description='Helper library for interacting with the Mozilla Pulse ' +
                  'message system at pulse.mozilla.org',
      author='Christian Legnitto',
      author_email='clegnitto@mozilla.com',
      packages=['mozillapulse','mozillapulse.messages'],
)

