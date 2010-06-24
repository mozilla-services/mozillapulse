from carrot.connection import BrokerConnection
from carrot.messaging import Consumer

from config import PulseConfiguration
from utils import *

from datetime import datetime

# Exceptions we can raise
class InvalidTopic(Exception):
    pass

class InvalidAppLabel(Exception):
    pass

class InvalidCallback(Exception):
    pass

class MalformedMessage(Exception):
    pass


# Generic publisher class that specific consumers inherit from
class GenericConsumer(object):

    def __init__(self, config, exchange=None, connect=True):
        self.config = config
        self.exchange = exchange
        self.connection = None
        if connect:
            self.connect()

    # Sets vairables
    def configure(self, **kwargs):
        for x in kwargs:
            setattr(self, x, kwargs[x])

    # Connect to the message broker
    def connect(self):
        if not self.connection:
            self.connection = BrokerConnection(hostname=self.config.host,
                                               port=self.config.port,
                                               userid=self.config.user,
                                               password=self.config.password,
                                               virtual_host=self.config.vhost)

    # Disconnect from the message broker
    def disconnect(self):
        if self.connection:
            self.connection.close()

    # Support purging messages that are already in the queue on the broker
    # TODO: I think this is only supported by the amqp backend
    def purge_existing_messages(self):

        # Make sure there is an applabel given
        if not self.applabel:
            raise InvalidAppLabel(self.applabel)
        
        # Purge the queue of existing messages
        self.connection.create_backend().queue_purge(self.applabel)

    # Blocks and calls the callback when a message comes into the queue
    # For info on one script listening to multiple channels, see
    # http://ask.github.com/carrot/changelog.html#id1
    def listen(self, callback=None):

        # One can optionally provide a callback to listen (if it wasn't already)
        if callback:
            self.callback = callback

        # Make suere there is an exchange given
        if not self.exchange:
            raise InvalidExchange(self.exchange)

        # Make sure there is a topic given
        if not self.topic:
            raise InvalidTopic(self.topic)

        # Make sure there is an applabel given
        if not self.applabel:
            raise InvalidAppLabel(self.applabel)

        # Make sure there is a callback given
        if not self.callback or not hasattr(self.callback, '__call__'):
            raise InvalidCallback(self.callback)

        # Connect to the broker if we haven't already
        if not self.connection:
            self.connect()

        # Set up our broker publisher
        self.consumer = Consumer(connection=self.connection,
                                   queue=self.applabel,
                                   exchange=self.exchange,
                                   exchange_type="topic",
                                   routing_key=self.topic)

        # Register the callback the user wants
        self.consumer.register_callback(self.callback)

        print "Listening for %s and registered %s" % (self.topic, self.callback)

        # This blocks, and then calls the user callback every time a message 
        # comes in
        self.consumer.wait()

        # Likely never get here but can't hurt
        self.disconnect()

# ------------------------------------------------------------------------------
# Consumers for various topics
# ------------------------------------------------------------------------------

class BugzillaConsumer(GenericConsumer):
    
    def __init__(self, **kwargs):
        for x in ['applabel','topic','callback']:
            if x in kwargs:
                setattr(self, x, kwargs[x])
                del kwargs[x]

        super(BugzillaConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.bugzilla')

class HgConsumer(GenericConsumer):
    
    def __init__(self, **kwargs):
        for x in ['applabel','topic','callback']:
            if x in kwargs:
                setattr(self, x, kwargs[x])
                del kwargs[x]

        super(HgConsumer, self).__init__(PulseConfiguration(**kwargs), 'org.mozilla.exchange.hg')
