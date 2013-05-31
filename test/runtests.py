# Any copyright is dedicated to the Public Domain.
# http://creativecommons.org/publicdomain/zero/1.0/

import Queue
import multiprocessing
import time
import unittest
import uuid

from mozillapulse import consumers, publishers
from mozillapulse.messages import build, hg

# Default RabbitMQ host settings are as defined in the accompanying
# vagrant puppet files.
DEFAULT_RABBIT_HOST = '192.168.33.10'
DEFAULT_RABBIT_PORT = 5672
DEFAULT_RABBIT_VHOST = 'pulse'
DEFAULT_RABBIT_USER = 'pulse'
DEFAULT_RABBIT_PASSWORD = 'pulse'

# Global pulse configuration.
pulse_cfg = {}


class PulseTestBase(unittest.TestCase):

    """Launches a consumer in a separate process and publishes a message in
    the main process.  The consumer will send the received message back
    to the main process for validation.  We use processes instead of threads
    since it's easier to kill a process (the listen() call cannot be
    terminated otherwise).
    """

    proc = None

    # Override these.
    consumer = None
    publisher = None

    def tearDown(self):
        if self.proc:
            self.proc.terminate()
            self.proc.join()
            self.proc = None

    def _validate(self, msg):
        # Publish one message to ensure the exchange exists.  Since there is
        # no consumer yet, it will be discarded.
        publisher = self.publisher(**pulse_cfg)
        publisher.publish(msg)

        queue = multiprocessing.Queue()
        consumer_cfg = pulse_cfg.copy()
        consumer_cfg['applabel'] = str(uuid.uuid1())
        def consume():
            def cb(data, message):
                queue.put(data)
                message.ack()
            consumer = self.consumer(**consumer_cfg)
            consumer.configure(topic='#', callback=cb)
            consumer.listen()
        self.proc = multiprocessing.Process(target=consume)
        self.proc.start()

        # Wait until queue has been created by consumer process.
        consumer = self.consumer(**consumer_cfg)
        consumer.configure(topic='#', callback=lambda x, y: None)
        attempts = 0
        while attempts < 20:
            attempts += 1
            if consumer.queue_exists():
                break
            time.sleep(0.05)

        self.assertTrue(consumer.queue_exists())

        publisher.publish(msg)

        try:
            received_data = queue.get(timeout=5)
        except Queue.Empty:
            self.fail('did not receive message from consumer process')
        self.assertEqual(msg.routing_key, received_data['_meta']['routing_key'])
        received_payload = {}
        for k, v in received_data['payload'].iteritems():
            received_payload[k.encode('ascii')] = v.encode('ascii')
        self.assertEqual(msg.data, received_payload)

class TestCode(PulseTestBase):

    consumer = consumers.CodeConsumer
    publisher = publishers.CodePublisher

    def test(self):
        msg = hg.HgCommitMessage('mozilla-central')
        msg.set_data('id', '12345678')
        msg.set_data('when', '1369685091')
        msg.set_data('who', 'somedev@mozilla.com')
        self._validate(msg)


class TestBuild(PulseTestBase):

    consumer = consumers.BuildConsumer
    publisher = publishers.BuildPublisher

    def test(self):
        msg = build.BuildPostedMessage()
        msg.set_data('build_id', '20130528184905')
        msg.set_data('revision', 'abcdef1234')
        msg.set_data('url', 'http://test/build/')
        msg.set_data('repository', 'test-repo')
        msg.set_data('product', 'productfoo')
        msg.set_data('product_version', '1.0')
        msg.set_data('locale', 'en-US')
        msg.set_data('platform', 'linux64')
        msg.set_data('build_date', '2013-05-28 18:49:05')
        msg.set_data('package_type', 'debug')
        self._validate(msg)


def main(pulse_opts):
    global pulse_cfg
    pulse_cfg.update(pulse_opts)
    unittest.main()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--host', action='store', dest='host',
                      default=DEFAULT_RABBIT_HOST,
                      help='host running RabbitMQ; defaults to %s' %
                      DEFAULT_RABBIT_HOST)
    parser.add_option('--port', action='store', type='int', dest='port',
                      default=DEFAULT_RABBIT_PORT,
                      help='port on which RabbitMQ is running; defaults to %d'
                      % DEFAULT_RABBIT_PORT)
    parser.add_option('--vhost', action='store', dest='vhost',
                      default=DEFAULT_RABBIT_VHOST,
                      help='name of pulse vhost; defaults to "%s"' %
                      DEFAULT_RABBIT_VHOST)
    parser.add_option('--user', action='store', dest='user',
                      default=DEFAULT_RABBIT_USER,
                      help='name of pulse RabbitMQ user; defaults to "%s"' %
                      DEFAULT_RABBIT_USER)
    parser.add_option('--password', action='store', dest='password',
                      default=DEFAULT_RABBIT_PASSWORD,
                      help='password of pulse RabbitMQ user; defaults to "%s"'
                      % DEFAULT_RABBIT_PASSWORD)
    (opts, args) = parser.parse_args()
    main(opts.__dict__)
