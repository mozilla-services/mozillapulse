#!/usr/bin/env python


from setuptools import setup

setup(name='MozillaPulse',
      version='0.6',
      description='Helper library for interacting with the Mozilla Pulse ' +
                  'message system at pulse.mozilla.org',
      author='Christian Legnitto',
      author_email='clegnitto@mozilla.com',
      packages=['mozillapulse','mozillapulse.messages'],
      install_requires=['carrot', 'pytz'],
)
