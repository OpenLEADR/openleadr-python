======
Client
======

An OpenADR Client (Virtual End Node or VEN) usually represents an entity that owns controllable devices. This can be electric vehicles, generators, wind turbines, refrigerated warehouses, et cetera. The client connects to a server, usualy representing a utility company, to discuss possible cooperation on energy usage throughout the day.

In your application, you mostly only have to deal with two things: Events and Reports.

.. _client_events:

Dealing with Events
===================

Events are informational or instructional messages from the server (VTN) which inform you of price changes, request load reduction, et cetera. Whenever there is an Event for your VEN, your ``on_event`` handler will be called with the event as its ``payload`` parameter.

The Event consists of three main sections:

1. A time period for when this event is supposed to be active (``active_period``)
2. A list of Targets to which the Event applies (``target``). This can be the VEN as a whole, or specific groups, assets, geographic areas, et cetera that this VEN represents.
3. A list of Signals (``signals``), which form the content of the Event. This can be price signals, load reduction signals, et cetera. Each signal has a name, a type, multiple Intervals that contain the relative start times, and some payload value for the client to interpret.

After you evaluate all these properties, you have only one decision to make: Opt In or Opt Out. Your handler must return either the string ``optIn`` or ``optOut``, and OpenLEADR will see to it that your response is correctly formatted for the server.

Example implementation:

.. code-block:: python3

    async def on_event(event):
        # Check if we can opt in to this event
        first_signal = event['event_signals'][0]
        intervals = first_signal['intervals']
        target = event['target']
        ...
        return 'optIn'

An example event dict might look like this:

.. code-block:: python3

    {
        'event_id': '123786-129831',
        'active_period': {'dtstart': datetime.datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                          'duration': datetime.timedelta(minutes=30)}
        'event_signals': [{'signal_name': 'simple',
                           'signal_type': 'level',
                           'intervals': [{'dtstart': datetime.datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                                          'duration': datetime.timedelta(minutes=10),
                                          'signal_payload': 1},
                                          {'dtstart': datetime.datetime(2020, 1, 1, 12, 10, 0, tzinfo=timezone.utc),
                                          'duration': datetime.timedelta(minutes=10),
                                          'signal_payload': 0},
                                          {'dtstart': datetime.datetime(2020, 1, 1, 12, 20, 0, tzinfo=timezone.utc),
                                          'duration': datetime.timedelta(minutes=10),
                                          'signal_payload': 1}],
       'targets': [{'resource_id': 'Device001'}],
       'targets_by_type': {'resource_id': ['Device001']}
    }

Please note that you can access the targets in two ways, which may be useful if there are more than one target:

1. As a list of Target dicts
2. As a dictionary of targets, grouped by target type.

For example:

.. code-block:: python3

    {
        'event_id': 'event123',
        # ...
        # As a list of Target dicts
        'targets': [{'resource_id': 'resource01'},
                    {'resource_id': 'resource02'},
                    {'group_id': 'group01'},
                    {'group_id': 'group02'}],
        # Grouped by target type
        'targets_by_type': {'resource_id': ['resource01', 'resource02'],
                            'group_id': ['group01', 'group02']}
    }

It is up to you which you want to use.


.. _client_reports:

Dealing with Reports
====================

The VTN Server will most likely want to receive some reports like metering values or availability status from you.

You can easily add reporting capabilities to your OpenADRClient object using the ``client.add_report`` method. In this method, you supply a callback function that will retrieve the current value for that measurement, as well as the resource_id, the measurement (like 'voltage', 'power', 'temperature', et cetera), optionally a unit and scale, and a sampling rate at which you can support this metervalue.

OpenLEADR will then offer this report to the VTN, and if they request this report from you, your callback function will automatically be called when needed.

Please see the :ref:`reporting` section for detailed information.


.. _client_signing_messages:

Signing outgoing messages
=========================

You can sign your outgoing messages using a public-private key pair in PEM format. This allows the receiving party to verify that the messages are actually coming from you.

If you want you client to automatically sign your outgoing messages, use the following configuration:

.. code-block:: python3

    async def main():
        client = OpenADRClient(ven_name='MyVEN',
                               vtn_url='https://localhost:8080/',
                               cert='/path/to/cert.pem',
                               key='/path/to/key.pem',
                               passphrase='my-key-password')
        ...

.. _client_validating_messages:

Validating incoming messages
============================

You can validate incoming messages against a public key.

.. code-block:: python3

    async def main():
        client = OpenADRClient(ven_name='MyVEN',
                               vtn_url='https://localhost:8080/',
                               vtn_fingerprint='AA:BB:CC:DD:EE:FF:11:22:33:44')

This will automatically validate check that incoming messages are signed by the private key that belongs to the provided (public) certificate. If validation fails, you will see a Warning emitted, but the message will not be delivered to your handlers, protecting you from malicious messages being processed by your system. The sending party will see an error message returned.

You should use both of the previous examples combined to secure both the incoming and the outgoing messages.
