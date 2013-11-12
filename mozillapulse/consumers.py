# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from amqp import ChannelError
from kombu import Connection, Exchange, Queue

from config import PulseConfiguration
from utils import *

# Exceptions we can raise
class InvalidTopic(Exception):
    pass

class InvalidAppLabel(Exception):
    pass

class InvalidCallback(Exception):
    pass

class MalformedMessage(Exception):
    pass


class GenericConsumer(object):
    """Generic publisher class that specific consumers inherit from.
    FIXME: Mandatory properties, like "topic", should not be set from generic
    functions like configure() but should instead be explicitly required
    somewhere, e.g. the constructor.
    """

    def __init__(self, config, exchange=None, connect=True, heartbeat=False,
                 **kwargs):
        self.config     = config
        self.exchange   = exchange
        self.connection = None
        self.durable    = False
        self.applabel   = ''
        self.heartbeat  = heartbeat
        for x in ['applabel','topic','callback','durable']:
            if x in kwargs:
                setattr(self, x, kwargs[x])
                del kwargs[x]

        if connect:
            self.connect()

    def configure(self, **kwargs):
        """Sets variables."""

        for x in kwargs:
            setattr(self, x, kwargs[x])

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

    def purge_existing_messages(self):
        """Purge messages that are already in the queue on the broker.
        TODO: I think this is only supported by the amqp backend.
        """

        if self.durable and not self.applabel:
            raise InvalidAppLabel('Durable consumers must have an applabel')

        if not self.connection:
            self.connect()

        queue = self._create_queue(self.applabel)
        try:
            queue(self.connection).purge()
        except ChannelError, e:
            if e.message == 404:
                pass
            raise

    def queue_exists(self):
        self._check_params()
        if not self.connection:
            self.connect()

        queue = self._create_queue(self.applabel)
        try:
            queue(self.connection).queue_declare(passive=True)
        except ChannelError, e:
            if e.message == 404:
                return False
            raise
        return True

    def delete_queue(self):
        self._check_params()
        if not self.connection:
            self.connect()

        queue = self._create_queue(self.applabel)
        try:
            queue(self.connection).delete()
        except ChannelError, e:
            if e.message != 404:
                raise

    def listen(self, callback=None):
        """Blocks and calls the callback when a message comes into the queue.
        For info on one script listening to multiple channels, see
        http://ask.github.com/carrot/changelog.html#id1.
        """

        # One can optionally provide a callback to listen (if it wasn't already)
        if callback:
            self.callback = callback

        self._check_params()

        if not self.connection:
            self.connect()

        exchange = Exchange(self.exchange, type='topic')

        # Create a queue and bind to the first key.
        queue = self._create_queue(self.applabel, exchange, self.topic[0])
        consumer = self.connection.Consumer(queue, callbacks=[self.callback])

        # Bind to any additional keys.
        for routing_key in self.topic[1:]:
            consumer.queues[0].bind_to(exchange, routing_key)


        if self.heartbeat:
            hb_exchange = Exchange('org.mozilla.exchange.pulse.test',
                                   type='topic')
            consumer.queues[0].bind_to(hb_exchange, 'heartbeat')

        with consumer:
            while True:
                self.connection.drain_events()

        # Likely never get here but can't hurt.
        self.disconnect()

    def _check_params(self):
        if not self.exchange:
            raise InvalidExchange(self.exchange)

        if not self.topic:
            raise InvalidTopic(self.topic)

        if self.durable and not self.applabel:
            raise InvalidAppLabel('Durable consumers must have an applabel')

        if not self.callback or not hasattr(self.callback, '__call__'):
            raise InvalidCallback(self.callback)

        # We support multiple bindings if we were given an array for the topic.
        if not isinstance(self.topic, list):
            self.topic = [self.topic]

    def _create_queue(self, name, exchange=None, routing_key=''):
        return Queue(name=name,
                     exchange=exchange,
                     routing_key=routing_key,
                     durable=self.durable,
                     exclusive=False,
                     auto_delete=not self.durable)


# ------------------------------------------------------------------------------
# Consumers for various topics
# ------------------------------------------------------------------------------

class PulseTestConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(PulseTestConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.pulse.test', **kwargs)


class PulseMetaConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(PulseMetaConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.pulse', **kwargs)


class BugzillaConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(BugzillaConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.bugzilla', **kwargs)


class SimpleBugzillaConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(SimpleBugzillaConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.bugzilla.simple', **kwargs)


class CodeConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(CodeConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.code', **kwargs)


class HgConsumer(CodeConsumer):

    def __init__(self, **kwargs):
        pass
        #super(CodeConsumer, self).__init__(PulseConfiguration(**kwargs), 'hg.push.mozilla.central', **kwargs)


class BuildConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(BuildConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.build', **kwargs)


class NormalizedBuildConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(NormalizedBuildConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.build.normalized', **kwargs)


class QAConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(QAConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.qa', **kwargs)
