# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import ConfigParser
import unittest

from mozillapulse.config import (PulseConfiguration, DEFAULT_PORT,
                                 DEFAULT_SSL_PORT)


class TestConfig(unittest.TestCase):

    def verify_defaults(self, pulse_cfg, except_opts=[]):
        for opt_name, opt_dflt in PulseConfiguration.defaults.iteritems():
            if opt_name not in except_opts:
                self.assertEqual(getattr(pulse_cfg, opt_name), opt_dflt)

    def test_config(self):
        cfg = ConfigParser.ConfigParser()
        pulse_cfg = PulseConfiguration.read_from_config(cfg)
        self.verify_defaults(pulse_cfg)
        cfg.add_section('pulse')
        pulse_cfg = PulseConfiguration.read_from_config(cfg)
        self.verify_defaults(pulse_cfg)
        cfg.set('pulse', 'user', 'foo')
        pulse_cfg = PulseConfiguration.read_from_config(cfg)
        self.assertEqual(pulse_cfg.user, 'foo')
        self.assertEqual(pulse_cfg.port, DEFAULT_SSL_PORT)
        self.verify_defaults(pulse_cfg, ['user'])
        cfg.set('pulse', 'ssl', 'off')
        pulse_cfg = PulseConfiguration.read_from_config(cfg)
        self.assertEqual(pulse_cfg.ssl, False)
        self.assertEqual(pulse_cfg.port, DEFAULT_PORT)
        self.verify_defaults(pulse_cfg, ['user', 'ssl', 'port'])
        cfg.set('pulse', 'port', '5555')
        pulse_cfg = PulseConfiguration.read_from_config(cfg)
        self.assertEqual(pulse_cfg.port, 5555)
        self.verify_defaults(pulse_cfg, ['user', 'ssl', 'port'])


if __name__ == '__main__':
    unittest.main()
