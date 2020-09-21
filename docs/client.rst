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

    from openadr import OpenADRClient

    async def on_event(payload):
        # Check if we can opt in to this event
        start_time = payload['events'][0]['active_period']['dtstart']
        duration = payload['events'][0]['active_period']['duration']

        await can_we_do_this(from_time=payload[''])
        return 'optIn'


.. _client_reports:

Dealing with Reports
====================

The VTN Server will most like want to receive some reports like metering values or availability status from you.
Providing reports
-----------------

If you tell OpenLEADR what reports you are able to provide, and give it a handler that will retrieve those reports from your own systems, OpenLEADR will make sure that the server receives the reports it asks for and at the requested interval.

For example: you can provide 15-minute meter readings for an energy meter at your site. You have a coroutine set up like this:

.. code-block:: python3

    async def get_metervalue():
        current_value = await meter.read()
        return current_value

And you configure this report in OpenLEADR using an :ref:`oadrReportDescription` dict:

.. code-block:: python3

    async def main():
        client = OpenADRClient(ven_name='MyVEN', vtn_url='https://localhost:8080/')
        report_description = {''}
        client.add_report({'report'})

The only thing you need to provide is the current value for the item you are reporting. OpenLEADR will format the complete :ref:`oadrReport` message for you.



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
