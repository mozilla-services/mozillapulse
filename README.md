# MozillaPulse

MozillaPulse is a Python package for interacting with [Mozilla Pulse][].
It contains classes for consumers, publishers, and messages.

In order to use a Mozilla Pulse consumer, you must register with
[PulseGuardian][] to create a Pulse user.  Here's an example of
creating a Buildbot consumer:

    from mozillapulse.consumers import BuildConsumer

    def callback(body, msg):
        print 'Received message: %s' % body

    c = BuildConsumer(user=<PulseGuardian user>,
                      password=<PulseGuardian password>,
                      topic='#',
                      callback=callback)
    c.listen()

See the HACKING.md file for instructions on setting up a local Pulse
instance for development.

[Mozilla Pulse]: https://wiki.mozilla.org/Auto-tools/Projects/Pulse
[PulseGuardian]: https://wiki.mozilla.org/Auto-tools/Projects/Pulse/PulseGuardian


## Running tests

If you want to run tests against this package:

- Install tox: `pip install tox`
- Run the vagrant instance. In the test repository run: `vagrant up`
- Run tox: `tox`
