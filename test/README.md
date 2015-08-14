mozillapulse tests
==================

This directory contains some basic feature tests for the mozillapulse package.
Tests in unittests.py are unittests that can be run on their own without
any special environment.

Tests in runtests.py require a RabbitMQ server with a vhost and the following
users and password settings:

USERNAME    |PASSWORD
------------|--------
build       | build
code        | code
pulse       | pulse
taskcluster | taskcluster

as well as the following user permission settings (as per the
[security model][]):

	Conf:	"^(queue/<user>/.*|exchange/<user>/.*)"
	Write: 	"^(queue/<user>/.*|exchange/<user>/.*)"
	Read: 	"^(queue/<user>/.*|exchange/.*)"

where <user> is replaced with each of the usernames above.

To ease setup, a Vagrantfile has been provided with a RabbitMQ configuration.
By default, the host is created at 192.168.33.10, RabbitMQ is configured
with a vhost called "/" and the users/permissions specified above.
If you use your own RabbitMQ installation, you must use the appropriate
options with runtests.py.

The tests in runtests.py ensure that the common APIs work properly and that
the user permissions listed above actually enforce the security model
(arguably the latter should go into the PulseGuardian repository, however).
Not all consumers and publishers are tested, since they are all derived
classes with very few differences.

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

[security model]: https://wiki.mozilla.org/Auto-tools/Projects/Pulse#Security_Model
