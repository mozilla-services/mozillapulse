mozillapulse tests
==================

This directory contains some basic feature tests for the mozillapulse package.
Since mozillapulse is just a layer on top of an AMQP server, they require a
RabbitMQ server with a vhost and a user with full read-write privileges
(technically consumers and producers require different privileges, but for
the sake of simplicity, the tests only use one user).

To ease setup, a Vagrantfile has been provided with a RabbitMQ configuration.
By default, the host is created at 192.168.33.10, and RabbitMQ is configured
with a vhost called "pulse" that has a user "pulse" with password "pulse" that
has full permissions.  If you change this setup, or use your own RabbitMQ
installation, you must use the appropriate options with runtests.py.

The tests in runtests.py are very basic, just to ensure that the common APIs
work properly.  Not all consumers and publishers are tested, since they are
all derived classes with very few differences.

Since GenericConsumer.listen() is not intended to exit, we launch it in a
separate process (using the multiprocessing module) instead of a thread, since
it is easier to terminate a process.  We use a queue to return the received
data to the main process to compare with the published data.

To run the tests with the provided Vagrantfile, ensure you have vagrant and
virtualbox installed, then run

* vagrant up
* python runtests.py

No options are required if you are using the supplied Vagrantfile and have not
modified it.  Otherwise, run "python runtests.py -h" to see the available
options.

These tests are specifically not referenced in mozillapulse's setup.py since
they require some setup.