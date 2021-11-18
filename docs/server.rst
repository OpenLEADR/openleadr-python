.. _server:

======
Server
======

If you are implementing an OpenADR Server ("Virtual Top Node") using OpenLEADR, read this page.

.. _server_example:

1-minute VTN example
====================

Here's an example of a server that accepts registrations from a VEN named
'ven_123', requests all reports that it offers, and creates an Event for this
VEN.

.. code-block:: python3

    import asyncio
    from datetime import datetime, timezone, timedelta
    from openleadr import OpenADRServer, enable_default_logging
    from functools import partial

    enable_default_logging()

    async def on_create_party_registration(registration_info):
        """
        Inspect the registration info and return a ven_id and registration_id.
        """
        if registration_info['ven_name'] == 'ven123':
            ven_id = 'ven_id_123'
            registration_id = 'reg_id_123'
            return ven_id, registration_id
        else:
            return False

    async def on_register_report(ven_id, resource_id, measurement, unit, scale,
                                 min_sampling_interval, max_sampling_interval):
        """
        Inspect a report offering from the VEN and return a callback and sampling interval for receiving the reports.
        """
        callback = partial(on_update_report, ven_id=ven_id, resource_id=resource_id, measurement=measurement)
        sampling_interval = min_sampling_interval
        return callback, sampling_interval

    async def on_update_report(data, ven_id, resource_id, measurement):
        """
        Callback that receives report data from the VEN and handles it.
        """
        for time, value in data:
            print(f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}")

    async def event_response_callback(ven_id, event_id, opt_type):
        """
        Callback that receives the response from a VEN to an Event.
        """
        print(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")

    # Create the server object
    server = OpenADRServer(vtn_id='myvtn')

    # Add the handler for client (VEN) registrations
    server.add_handler('on_create_party_registration', on_create_party_registration)

    # Add the handler for report registrations from the VEN
    server.add_handler('on_register_report', on_register_report)

    # Add a prepared event for a VEN that will be picked up when it polls for new messages.
    server.add_event(ven_id='ven_id_123',
                     signal_name='simple',
                     signal_type='level',
                     intervals=[{'dtstart': datetime(2021, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                                 'duration': timedelta(minutes=10),
                                 'signal_payload': 1}],
                     callback=event_response_callback)

    # Run the server on the asyncio event loop
    loop = asyncio.get_event_loop()
    loop.create_task(server.run())
    loop.run_forever()

Read on for more details!

.. _server_registration:

Registration
============

If a client (VEN) wants to register for the first time, it will go through a Registration procedure.

.. admonition:: Implementation Checklist

    1. Create a handler that decides what to do with new registrations, based on their registration info.


The client will send a :ref:`oadrQueryRegistration` message. The server will respond with a :ref:`oadrCreatedPartyRegistration` message containing a list of its capabilities, notably the implemented OpenADR protocol versions and the available Transport Mechanisms (HTTP and/or XMPP).

The client will then usually send a :ref:`oadrCreatePartyRegistration` message, in which it registers to a specific OpenADR version and Transport Method. The server must then decide what it wants to do with this registration.

In the case that the registration is accepted, the VTN will generate a venID and a RegistrationID for this VEN and respond with a :ref:`oadrCreatedPartyRegistration` message.

In your application, when a VEN sends a :ref:`oadrCreatePartyRegistration` request, it will call your ``on_create_party_registration`` handler. This handler must somehow look up what to do with this request, and respond with a ``ven_id, registration_id`` tuple.

Example implementation:

.. code-block:: python3

    from openleadr.utils import generate_id

    async def on_create_party_registration(payload):
        ven_name = payload['ven_name']
        # Check whether or not this VEN is allowed to register
        result = await database.query("""SELECT COUNT(*)
                                           FROM vens
                                          WHERE ven_name = ?""",
                                      (payload['ven_name'],))
        if result == 1:
            # Generate an ID for this registration
            ven_id = generate_id()
            registration_id = generate_id()

            # Store the registration in a database (pseudo-code)
            await database.query("""UPDATE vens
                                       SET ven_id = ?
                                       registration_id = ?
                                     WHERE ven_name = ?""",
                                 (ven_id, registration_id, ven_name))

            # Return the registration ID.
            # This will be put into the correct form by the OpenADRServer.
            return ven_id, registration_id

.. _server_events:

Events
======

The server (VTN) is expected to know when it needs to inform the clients (VENs) of certain events that they must respond to. This could be a predicted shortage or overage of available power in a certain electricity grid area, for example.

The easiest way to supply events to a VEN is by using OpenLEADR's built-in message queing system. You simply add an event for a ven using the ``server.add_event`` method. You supply the ven_id for which the event is required, as well as the ``signal_name``, ``signal_type``, ``intervals`` and ``targets``. This will build an event object with a single signal for a VEN. If you need more flexibility, you can alternatively construct the event dictionary yourself and supply it directly to the ``add_raw_event`` method.

The VEN can decide whether to opt in or opt out of the event. To be notified of their opt status, you supply a callback handler which will be called when the VEN has responded to the event request.

.. code-block:: python3

    from openleadr import OpenADRServer
    from functools import partial
    from datetime import datetime, timezzone

    async def event_callback(ven_id, event_id, opt_status):
        print(f"VEN {ven_id} responded {opt_status} to event {event_id}")

    server = OpenADRServer(vtn_id='myvtn')
    event_id = server.add_event(ven_id='ven123',
                                signal_name='simple',
                                signal_type='level',
                                intervals=[{'dtstart': datetime(2020. 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                                            'signal_payload': 1},
                                            {'dtstart': datetime(2020. 1, 1, 12, 15, 0, tzinfo=timezone.utc),
                                            'signal_payload': 0}],
                                target=[{'resource_id': 'Device001'}],
                                callback=event_callback)


Alternatively, you can use the handy constructors in ``openleadr.objects`` to format parts of the event:

.. code-block:: python3

    from openleadr import OpenADRServer
    from openleadr.objects import Target, Interval
    from datetime import datetime, timezone
    from functools import partial

    async def event_callback(ven_id, event_id, opt_status):
        print(f"VEN {ven_id} responded {opt_status} to event {event_id}")

    server = OpenADRServer(vtn_id='myvtn')
    event_id = server.add_event(ven_id='ven123',
                                signal_name='simple',
                                signal_type='level',
                                intervals=[Interval(dtstart=datetime(2020, 1, 1, 12, 15, 0, tzinfo=timezone.utc),
                                                    signal_payload=0),
                                           Interval(dtstart=datetime(2020, 1, 1, 12, 15, 0, tzinfo=timezone.utc),
                                                    signal_payload=1)]
                                target=[Target(resource_id='Device001')],
                                callback=event_callback)

If you want to add a "raw" event directly, you can use this example as a guid:

.. code-block:: python3

    from openleadr import OpenADRServer
    from openleadr.objects import Event, EventDescriptor, EventSignal, Target, Interval
    from datetime import datetime, timezone
    from functools import partial

    async def event_callback(ven_id, event_id, opt_status):
        print(f"VEN {ven_id} responded {opt_status} to event {event_id}")

    server = OpenADRServer(vtn_id='myvtn')
    now = datetime.now()
    event = Event(event_descriptor=EventDescriptor(event_id='event001',
                                                   modification_number=0,
                                                   event_status='far',
                                                   market_context='http://marketcontext01'),
                  event_signals=[EventSignal(signal_id='signal001',
                                             signal_type='level',
                                             signal_name='simple',
                                             intervals=[Interval(dtstart=now,
                                                                 duration=timedelta(minutes=10),
                                                                 signal_payload=1)]),
                                 EventSignal(signal_id='signal002',
                                             signal_type='price',
                                             signal_name='ELECTRICITY_PRICE',
                                             intervals=[Interval(dtstart=now,
                                                                 duration=timedelta(minutes=10),
                                                                 signal_payload=1)])],
                  targets=[Target(ven_id='ven123')])

    server.add_raw_event(ven_id='ven123', event=event, callback=event_callback)

If you want to add an event and wait for the response in a single coroutine, you can pass an asyncio Future instead of a function or coroutine as the callback argument:

.. code-block:: python3

    import asyncio

    ...

    async def generate_event():
        loop = asyncio.get_event_loop()
        opt_status_future = loop.create_future()
        server.add_event(..., callback=opt_status_future)
        opt_status = await opt_status_future
        print(f"The opt status for this event is {opt_status}")


A word on event targets
-----------------------

The Target of your Event is an indication for the VEN which resources or devices should be affected. You can supply the target of the event in serveral ways:

- Assigning the ``target`` parameter with a single ``objects.Target`` object.
- Assigning the ``targets`` parameter with a list of ``objects.Target`` objects.
- Assigning the ``targets_by_type`` parameters with a dict, that lists targets grouped by their type, like this:

.. code-block:: python3

    server.add_event(...
                     targets_by_type={'resource_id': ['resource01', 'resource02'],
                                      'group_id': ['group01', 'group02']}
                     )

If you dont assign any Target, the target will be set to the ``ven_id`` that you specified.


.. _server_reports:

Reports
=======

Please see the :ref:`reporting` section.


.. _server_implement:

Things you should implement
===========================

You should implement the following handlers:

- ``on_create_party_registration(registration_info)``
- ``on_register_report(ven_id, resource_id, measurement, unit, scale, min_sampling_interval, max_sampling_interval)``
- ``ven_lookup(ven_id)``: a function that returns a dict with the `'ven_name'`, ``'ven_id'``, ``'fingerprint'`` and ``'registration_id'`` for the given ``ven_id`` (see below.). This is used to automatically reject requests from VENs that the VTN does not know, and to authenticate the VENs message signatures.

Optionally:

- ``on_poll(ven_id)``; only if you don't want to use the internal message queue.
- ``ven_lookup(ven_id)``: a function or coroutine that openleadr can use to check if we know a VEN. Signature:

.. _server_signing_messages:

Signing Messages
================

The OpenLEADR can sign your messages and validate incoming messages. For some background, see the :ref:`message_signing`.

Example implementation:

.. code-block:: python3

    from openleadr import OpenADRServr

    def ven_lookup(ven_id):
        # Look up the information about this VEN.
        ven_info = database.lookup('vens').where(ven_id=ven_id) # Pseudo code
        if ven_info:
            return {'ven_id': ven_info['ven_id'],
                    'ven_name': ven_info['ven_name'],
                    'fingerprint': ven_info['fingerprint'],
                    'registration_id': ven_info['registration_id']}
        else:
            return {}

    server = OpenADRServer(vtn_id='MyVTN',
                           cert='/path/to/cert.pem',
                           key='/path/to/private/key.pem',
                           passphrase='mypassphrase',
                           fingerprint_lookup=fingerprint_lookup)

The VEN's fingerprint should be obtained from the VEN outside of OpenADR.


.. _server_message_handlers:

Message Handlers
================

Your server has to deal with the different OpenADR messages. The way this works is that OpenLEADR will expose certain modules at the appropriate endpoints (like /oadrPoll and /EiRegister), and figure out what type of message is being sent. It will then call your handler with the contents of the message that are relevant for you to handle. This section provides an overview with examples for the different kinds of messages that you can expect and what should be returned.

.. _server_on_register_report:

on_register_report
------------------

The VEN informs you which reports it has available. If you want to periodically receive any of these reports, you should return a list of the r_ids that you want to receive.

Signature:

.. code-block:: python3

    async def on_register_report(ven_id, resource_id, measurement, unit, scale,
                                 min_sampling_interval, max_sampling_interval):
        # If we want this report:
        return (callback, requested_sampling_interval)
        # or
        return None

.. _server_on_query_registration:

on_query_registration
---------------------

A prospective VEN is requesting information about your VTN, like the versions and transports you support. You should not implement this handler and let OpenLEADR handle this response.

.. _server_on_create_party_registration:

on_create_party_registration
----------------------------

The VEN tries to register with you. You will receive a registration_info dict that contains, among other things, a field `ven_name` which is how the VEN identifies itself. If the VEN is accepted, you return a ``ven_id, registration_id`` tuple. If not, return ``False``:

.. code-block:: python3

    async def on_create_party_registration(registration_info):
        ven_name = registration_info['ven_name']
        ...
        if ven_is_known:
            return ven_id, registration_id
        else
            return None

During this step, the VEN probably does not have a ``venID`` yet. If they connected using a secure TLS connection, the ``registration_info`` dict will contain the fingerprint of the public key that was used for this connection (``registration_info['fingerprint']``). Your ``on_create_party_registration`` handler should check this fingerprint value against a value that you received offline, to be sure that the ven with this venName is the correct VEN.

.. _server_on_cancel_party_registration:

on_cancel_party_registration
----------------------------

The VEN informs you that they are cancelling their registration and no longer wish to be contacted by you.

You should deregister the VEN internally, and return `None`.

Return: ``None``


.. _server_on_poll:

on_poll
-------

You only need to implement this if you don't want to use the automatic internal message queue. If you add this handler to the server, the internal message queue will be automatically disabled.

The VEN is requesting the next message that you have for it. You should return a tuple of message_type and message_payload as a dict. If there is no message for the VEN, you should return `None`.

Signature:

.. code-block:: python3

    async def on_poll(ven_id):
        ...
        return message_type, message_payload

If you implement your own on_poll handler, you should also include your own ``on_created_event`` handler that retrieves the opt status for a distributed event.

.. _server_on_created_event:

on_created_event
----------------

You only need to implement this if you don't want to use the automatic internal message queue. Otherwise, you supply a per-event callback function when you add the event to the internal queue.

Signature:

.. code-block:: python3

    async def on_created_event(ven_id, event_id, opt_status):
        print("Ven {ven_id} returned {opt_status} for event {event_id}")
        # return None
