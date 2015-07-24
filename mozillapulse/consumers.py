# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import uuid

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

class InvalidExchange(Exception):
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
        self.config = config
        self.exchange = exchange
        self.connection = None
        self.durable = False
        self.applabel = ''
        self.heartbeat = heartbeat
        for x in ['applabel', 'topic', 'callback', 'durable']:
            if x in kwargs:
                setattr(self, x, kwargs[x])
                del kwargs[x]

        # Only used if there is no applabel.
        self.queue_gen_name = None

        if connect:
            self.connect()

    @property
    def queue_name(self):
        # This is a property instead of being set in the constructor since
        # applabel can be set later via configure().
        queue_name = 'queue/%s/' % self.config.user
        if self.applabel:
            queue_name += self.applabel
        else:
            if not self.queue_gen_name:
                self.queue_gen_name = str(uuid.uuid1())
            queue_name += self.queue_gen_name
        return queue_name

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
                                         virtual_host=self.config.vhost,
                                         ssl=self.config.ssl)

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

        queue = self._create_queue()
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

        queue = self._create_queue()
        try:
            queue(self.connection).queue_declare(passive=True)
        except ChannelError, e:
            if e.message == 404 or e.reply_code == 404:
                return False
            raise
        return True

    def delete_queue(self):
        self._check_params()
        if not self.connection:
            self.connect()

        queue = self._create_queue()
        try:
            queue(self.connection).delete()
        except ChannelError, e:
            if e.message != 404:
                raise

    def listen(self, callback=None, on_connect_callback=None):
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

        exchange = Exchange(self.exchange[0], type='topic')

        # Raise an error if the exchange doesn't exist.
        exchange(self.connection).declare(passive=True)

        # Create a queue.
        queue = self._create_queue(exchange, self.topic[0])
        if on_connect_callback:
            on_connect_callback()

        # Don't autodeclare, since we don't want consumers trying to
        # declare exchanges.
        consumer = self.connection.Consumer(queue, auto_declare=False,
                                            callbacks=[self.callback])

        consumer.queues[0].queue_declare()
        # Bind to the first key.
        consumer.queues[0].queue_bind()

        # Bind to any additional keys.
        for new_exchange, new_topic in zip(self.exchange[1:], self.topic[1:]):
            exchange = Exchange(new_exchange, type='topic')
            exchange(self.connection).declare(passive=True)

            consumer.queues[0].bind_to(new_exchange, new_topic)

        if self.heartbeat:
            hb_exchange = Exchange('exchange/pulse/test', type='topic')
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

        # We support multiple exchanges if we were given an array for
        # the exchange. In this case, the exchange list and the topic
        # list must have the same length.
        if not isinstance(self.exchange, list):
            self.exchange = [self.exchange] * len(self.topic)
        elif len(self.exchange) != len(self.topic):
            raise InvalidExchange(
                "The list of exchanges must have the same length as the list of"
                " topics.")

    def _create_queue(self, exchange=None, routing_key=''):
        return Queue(name=self.queue_name,
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
        super(PulseTestConsumer, self).__init__(
            PulseConfiguration(**kwargs), 'exchange/pulse/test', **kwargs)


class PulseMetaConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(PulseMetaConsumer, self).__init__(
            PulseConfiguration(**kwargs), 'exchange/pulse/', **kwargs)


class SimpleBugzillaConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        exchange = 'exchange/bugzilla/simple'
        if kwargs.get('dev'):
            exchange += '/dev'
        super(SimpleBugzillaConsumer, self).__init__(PulseConfiguration(
                **kwargs), exchange, **kwargs)


class CodeConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(CodeConsumer, self).__init__(
            PulseConfiguration(**kwargs), 'exchange/code/', **kwargs)


class BuildConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(BuildConsumer, self).__init__(
            PulseConfiguration(**kwargs), 'exchange/build/', **kwargs)


class NormalizedBuildConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(NormalizedBuildConsumer, self).__init__(
            PulseConfiguration(**kwargs), 'exchange/build/normalized',
            **kwargs)


class QAConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(QAConsumer, self).__init__(
            PulseConfiguration(**kwargs), 'exchange/qa/', **kwargs)


class MozReviewConsumer(GenericConsumer):

    def __init__(self, **kwargs):
        super(MozReviewConsumer, self).__init__(
            PulseConfiguration(**kwargs), 'exchange/mozreview/', **kwargs)
