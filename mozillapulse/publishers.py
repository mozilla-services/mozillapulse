# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import warnings

from datetime import datetime

from kombu import Connection, Exchange, Producer
from pytz import timezone

from config import PulseConfiguration
from utils import *


# Exceptions we can raise
class InvalidExchange(Exception):
    pass

class MalformedMessage(Exception):
    pass


class GenericPublisher(object):
    """Generic publisher class that specific publishers inherit from."""

    def __init__(self, config, exchange=None, connect=True):
        self.config = config
        self.exchange = exchange
        self.connection = None
        if connect:
            self.connect()

    def connect(self):
        if not self.connection:
            self.connection = Connection(hostname=self.config.host,
                                         port=self.config.port,
                                         userid=self.config.user,
                                         password=self.config.password,
                                         virtual_host=self.config.vhost)

    def disconnect(self):
        if self.connection:
            self.connection.release()
            self.connection = None

    def publish(self, message):
        """Publishes a pulse message to the proper exchange."""

        if not self.exchange:
            raise InvalidExchange(self.exchange)

        if not message:
            raise MalformedMessage(message)

        message._prepare()

        if not self.connection:
            self.connect()

        producer = Producer(channel=self.connection,
                            exchange=Exchange(self.exchange, type='topic'),
                            routing_key=message.routing_key)

        # The message is actually a simple envelope format with a payload and
        # some metadata.
        final_data = {}
        final_data['payload'] = message.data
        final_data['_meta'] = message.metadata.copy()
        final_data['_meta'].update({
            'exchange': self.exchange,
            'routing_key': message.routing_key,
            'serializer': self.config.serializer,
            'sent': time_to_string(datetime.now(timezone(self.config.broker_timezone)))
        })

        producer.publish(final_data, serializer=self.config.serializer)


# ------------------------------------------------------------------------------
# Publishers for various exchanges
# ------------------------------------------------------------------------------

class PulseTestPublisher(GenericPublisher):

    def __init__(self, **kwargs):
        super(PulseTestPublisher, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.pulse.test')


class PulseMetaPublisher(GenericPublisher):

    def __init__(self, **kwargs):
        super(PulseMetaPublisher, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.pulse')


class BugzillaPublisher(GenericPublisher):

    def __init__(self, **kwargs):
        super(BugzillaPublisher, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.bugzilla')


class SimpleBugzillaPublisher(GenericPublisher):

    def __init__(self, **kwargs):
        exchange = 'org.mozilla.exchange.bugzilla.simple'
        if kwargs.get('dev'):
            exchange += '.dev'
        super(SimpleBugzillaPublisher, self).__init__(
            PulseConfiguration(**kwargs), exchange)


class CodePublisher(GenericPublisher):

    def __init__(self, **kwargs):
        super(CodePublisher, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.code')


class HgPublisher(CodePublisher):

    def __init__(self, **kwargs):
        super(HgPublisher, self).__init__(PulseConfiguration(**kwargs))
        warnings.warn('HgPublisher is now CodePublisher', DeprecationWarning)


class BuildPublisher(GenericPublisher):

    def __init__(self, **kwargs):
        super(BuildPublisher, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.build')


class QAPublisher(GenericPublisher):

    def __init__(self, **kwargs):
        super(QAPublisher, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.qa')
