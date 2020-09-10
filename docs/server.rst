.. _server:

======
Server
======

If you are implementing an OpenADR Server ("Virtual Top Node") using pyOpenADR, read this page.

.. _server_registration:

Registration
============

If a client (VEN) wants to register for the first time, it will go through a Registration procedure.

.. admonition:: Implementation Checklist

    1. Create a handler that decides what to do with new registrations, based on their ``venID``.


The client will send a :ref:`oadrQueryRegistration` message. The server will respond with a :ref:`oadrCreatedPartyRegistration` message containing a list of its capabilities, notably the implemented OpenADR protocol versions and the available Transport Mechanisms (HTTP and/or XMPP).

The client will then usually send a :ref:`oadrCreatePartyRegistration` message, in which it registers to a specific OpenADR version and Transport Method. The server must then decide what it wants to do with this registration.

In the case that the registration is accepted, the VTN will generate a RegistrationID for this VEN and respond with a :ref:`oadrCreatedPartyRegistration` message.

In your application, when a VEN sends a :ref:`oadrCreatePartyRegistration` request, it will call your ``on_register_party`` handler. This handler must somehow look up what to do with this request, and respond with a ``registration_id``.

Example implementation:

.. code-block:: python3

    from pyopenadr.utils import generate_id

    async def on_create_party_registration(payload):
        ven_id = payload['ven_id']
        # Check whether or not this VEN is allowed to register
        result = await database.query("""SELECT COUNT(*)
                                           FROM vens
                                          WHERE ven_id = ?""",
                                      (payload['ven_id'],))
        if result == 1:
            # Generate an ID for this registration
            registration_id = generate_id()

            # Store the registration in a database (pseudo-code)
            await database.query("""UPDATE vens
                                       SET registration_id = ?
                                     WHERE ven_id = ?""",
                                 (registration_id, ven_id))

            # Return the registration ID.
            # This will be put into the correct form by the OpenADRServer.
            return registration_id

.. _server_events:

Events
======

The server (VTN) is expected to know when it needs to inform the clients (VENs) of certain events that they must respond to. This could be a predicted shortage or overage of available power in a certain electricity grid area, for example.

The VTN must determine when VENs are relevant and which Events to send to them. The next time the VEN polls for new messages (using a :ref:`oadrPoll` or :ref:`oadrRequestEvent` message), it will send the Event in a :ref:`oadrDistributeEvent` message to the client. The client will then evaluate whether or not it indends to comply with the request, and respond with an :ref:`oadrCreatedEvent` message containing an optStatus of ``'optIn'`` or ``'optOut'``.

.. admonition:: Implementation Checklist

    In your application, the creation of Events is completely up to you. PyOpenADR will only call your ``on_poll`` handler with a ``ven_id``. This handler must be able to either retrieve the next event for this VEN out of some storage or queue, or make up the Event in real time.

    - ``on_created_event(payload)`` handler is called whenever the VEN sends an :ref:`oadrCreatedEvent` message, probably informing you of what they intend to do with the event you gave them.
    - ``on_request_event(ven_id)``: this should return the next event (if any) that you have for the VEN. If you return ``None``, a blank :ref:`oadrResponse` will be returned to the VEN.
    - ``on_request_report(ven_id)``: this should return then next report (if any) that you have for the VEN. If you return None, a blank :ref:`oadrResponse` will be returned to the VEN.
    - ``on_poll(ven_id)``: this should return the next message in line, which is usually either a new :ref:`oadrUpdatedReport` or a :ref:`oadrDistributeEvent` message.


The Event consists of three main sections:

1. A time period for when this event is supposed to be active
2. A list of Targets to which the Event applies. This can be the VEN as a whole, or specific groups, assets, geographic areas, et cetera that this VEN represents.
3. A list of Signals, which form the content of the Event. This can be price signals, load reduction signals, et cetera. Each signal has a name, a type, multiple Intervals that contain the relative start times, and some payload value for the client to interpret.



.. _server_reports:

Reports
=======

Reporting is probably the most complicated of interactions within OpenADR. It involves the following steps:

1. Party A makes its reporting capabilities known to party B using a :ref:`oadrRegisterReport` message.
2. Party B responds with an :ref:`oadrRegisteredReport` message, optionally including an :ref:`oadrReportRequest` section that tells party A which party B is interested in.
3. Party A reponds with an oadrCreatedReport message telling party B that it will periodically generate the reports.

This ceremony is performed once with the VTN as party A and once with the VEN as party A.

The VEN party can collect the reports it requested from the VTN using either the :ref:`oadrPoll` or :ref:`oadrRequestReport` messages. The VTN will respond with an :ref:`oadrUpdateReport` message containing the actual report. The VEN should then respond with a :ref:`oadrUpdatedReport` message.

The VEN should actively supply the reports to the VTN using :ref:`oadrUpdateReport` messages, to which the VTN will respond with :ref:`oadrUpdatedReport` messages.

.. admonition:: Implementation Checklist

    To benefit from the automatic reporting engine in pyOpenADR, you should implement the following items yourself:

    1. Configure the OpenADRServer() instance with your reporting capabilities and requirements
    2. Implement a handlers that can retrieve the reports from your backend system
    3. Implement a handler that deal with reports that come in from the clients


.. _server_implement:

Things you should implement
===========================

You should implement the following handlers:

- ``on_poll(ven_id)``
- ``on_request_event(ven_id)``
- ``on_request_report(payload)``
- ``on_create_party_registration(payload)``

.. _server_meta:

Non-OpenADR signals from the server
===================================

The pyOpenADR Server can call the following handlers, which are not part of the regular openADR communication flow, but can help you develop a more robust event-driven system:

- ``on_ven_online(ven_id)``: called when a VEN sends an :ref:`oadrPoll`, :ref:`oadrRequestEvent` or :ref:`oadrRequestReport` message after it had been offline before.
- ``on_ven_offline(ven_id)``: called when a VEN misses 3 consecutive poll intervals (configurable).

Example implementation:

.. code-block:: python3

    from pyopenadr import OpenADRServer

    server = OpenADRServer(vtn_id='MyVTN')
    server.add_handler('on_ven_online', on_ven_online)
    server.add_handler('on_ven_offline', on_ven_offline)

    async def on_ven_online(ven_id):
        print(f"VEN {ven_id} is now online again!")

    async def on_ven_offline(ven_id):
        print(f"VEN {ven_id} has gone AWOL")
