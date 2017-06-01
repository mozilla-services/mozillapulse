#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup


setup(name='MozillaPulse',
      version='1.3',
      description='Helper library for interacting with the Mozilla Pulse '
                  'message system at pulse.mozilla.org',
      url='https://hg.mozilla.org/automation/mozillapulse/',
      author='Mark Cote',
      author_email='mcote@mozilla.com',
      license='MPL 2.0',
      packages=['mozillapulse', 'mozillapulse.messages'],
      install_requires=['kombu', 'pytz'],
      test_suite='test.unittests')
