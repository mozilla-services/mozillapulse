# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

DEFAULT_PORT = 5672
DEFAULT_SSL_PORT = 5671

class PulseConfiguration:

    def __init__(self, **kwargs):

        # Default values for Mozilla pulse
        defaults = {
            # Connection defaults
            'user':       'public',
            'password':   'public',
            'host':       'pulse.mozilla.org',
            'vhost':      '/',
            'ssl':        True,
            # Message defaults
            'serializer': 'json',
            'broker_timezone': 'US/Pacific',
        }

        # Set any variables passed in.
        for key in kwargs:
            setattr(self, key, kwargs[key])

        # Set defaults for anything that isn't passed in.
        for key in defaults:
            if not hasattr(self, key):
                setattr(self, key, defaults[key])

        # Set defaults for special variables.
        if not hasattr(self, 'port'):
            if self.ssl:
                self.port = DEFAULT_SSL_PORT
            else:
                self.port = DEFAULT_PORT
