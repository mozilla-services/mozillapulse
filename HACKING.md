Setting up a Pulse system is essentially just setting up a RabbitMQ
server with appropriately configured users.  You can install your own
RabbitMQ instance, or you can use the Vagrant box in the test/
directory.  Either way, you'll probably want the management plugin
installed so you can use the web UI to see your connections,
exchanges, queues, etc.:

    rabbitmq-plugins enable rabbitmq_management

The easiest way to test your setup is with a heartbeat publisher and
consumer.  First you'll need a heartbeat user that will be responsible
for publishing the messages.  We'll create one with an insecure
password, since this is a local setup for development purposes.  On a
real system, ensure the password is something hard to guess.

On the system running RabbitMQ, run

    rabbitmqctl add_user heartbeat heartbeat
    rabbitmqctl set_permissions heartbeat '^exchange/pulse/.*' '^exchange/pulse/.*' '^exchange/pulse/.*'

Next you need to create an account for the consumer.  You can set up
[PulseGuardian][] alongside RabbitMQ and create a user that way, or
you can just create one manually (again, with an insecure password):

    rabbitmqctl add_user hbconsumer hbconsumer
    rabbitmqctl set_permissions hbconsumer '^queue/hbconsumer/.*' '^queue/hbconsumer/.*' '^(queue/hbconsumer/.*|exchange/.*)'

Now run the heartbeat publisher.  It's found in the [pulseshims][]
repository.  You'll need a config.ini file looking something like this
(assuming RabbitMQ is running locally):

    [heartbeat]
    host = localhost
    user = heartbeat
    password = heartbeat
    ssl = False

Now run it in a little loop, outputting a heartbeat every few seconds:

    while [ 1 ]; do python heartbeat.py; sleep 5; done

If you have the management plugin installed, you should see the
exchange created with a inbound message rate of about 0.20 per second.

Now you can create a consumer to read the heartbeat messages:

    from mozillapulse.consumers import PulseTestConsumer

    def callback(body, msg):
        print 'Received message: %s' % body

    c = PulseTestConsumer(user='hbconsumer',
                          password='hbconsumer',
                          host='localhost',
                          ssl=False,
                          topic='#',
                          callback=callback)
    c.listen()

You should see a message coming in every five seconds, like so:

    Received message: {u'payload': {u'what': u'This is a heartbeat', u'why': u'This lets users know pulse is up and the setup works'}, u'_meta': {u'sent': u'2014-08-01T12:46:42+01:00', u'routing_key': u'heartbeat', u'serializer': u'json', u'exchange': u'exchange/pulse/test'}}
    Received message: {u'payload': {u'what': u'This is a heartbeat', u'why': u'This lets users know pulse is up and the setup works'}, u'_meta': {u'sent': u'2014-08-01T12:46:47+01:00', u'routing_key': u'heartbeat', u'serializer': u'json', u'exchange': u'exchange/pulse/test'}}

You now have a working local Pulse environment.

[pulseshims]: https://hg.mozilla.org/automation/pulseshims/
[PulseGuardian]: https://wiki.mozilla.org/Auto-tools/Projects/Pulse/PulseGuardian
