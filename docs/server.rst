.. _server:

======
Server
======

If you are implementing an OpenADR Server ("Virtual Top Node") using OpenLEADR, read this page.

.. _server_registration:

Registration
============

If a client (VEN) wants to register for the first time, it will go through a Registration procedure.

.. admonition:: Implementation Checklist

    1. Create a handler that decides what to do with new registrations, based on their registration info.


The client will send a :ref:`oadrQueryRegistration` message. The server will respond with a :ref:`oadrCreatedPartyRegistration` message containing a list of its capabilities, notably the implemented OpenADR protocol versions and the available Transport Mechanisms (HTTP and/or XMPP).

The client will then usually send a :ref:`oadrCreatePartyRegistration` message, in which it registers to a specific OpenADR version and Transport Method. The server must then decide what it wants to do with this registration.

In the case that the registration is accepted, the VTN will generate a RegistrationID for this VEN and respond with a :ref:`oadrCreatedPartyRegistration` message.

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

The VTN must determine when VENs are relevant and which Events to send to them. The next time the VEN polls for new messages (using a :ref:`oadrPoll` or :ref:`oadrRequestEvent` message), it will send the Event in a :ref:`oadrDistributeEvent` message to the client. The client will then evaluate whether or not it indends to comply with the request, and respond with an :ref:`oadrCreatedEvent` message containing an optStatus of ``'optIn'`` or ``'optOut'``.

(Documentation for this section is in progress)


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

    To benefit from the automatic reporting engine in OpenLEADR, you should implement the following items yourself:

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

The OpenLEADR Server can call the following handlers, which are not part of the regular openADR communication flow, but can help you develop a more robust event-driven system:

- ``on_ven_online(ven_id)``: called when a VEN sends an :ref:`oadrPoll`, :ref:`oadrRequestEvent` or :ref:`oadrRequestReport` message after it had been offline before.
- ``on_ven_offline(ven_id)``: called when a VEN misses 3 consecutive poll intervals (configurable).

Example implementation:

.. code-block:: python3

    from openleadr import OpenADRServer

    server = OpenADRServer(vtn_id='MyVTN')
    server.add_handler('on_ven_online', on_ven_online)
    server.add_handler('on_ven_offline', on_ven_offline)

    async def on_ven_online(ven_id):
        print(f"VEN {ven_id} is now online again!")

    async def on_ven_offline(ven_id):
        print(f"VEN {ven_id} has gone AWOL")

.. _server_signing_messages:

Signing Messages
================

The OpenLEADR can sign your messages and validate incoming messages. For some background, see the :ref:`message_signing`.

Example implementation:

.. code-block:: python3

    from openleadr import OpenADRServr

    def fingerprint_lookup(ven_id):
        # Look up the certificate fingerprint that is associated with this VEN.
        fingerprint = database.lookup('certificate_fingerprint').where(ven_id=ven_id) # Pseudo code
        return fingerprint

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

.. _server_on_created_event:

on_created_event
----------------

The VEN informs you that they created an Event that you sent to them. You don't have to return anything.

Return: `None`

.. _server_on_request_event:

on_request_event
----------------

The VEN is requesting the next Event that you have for it. You should return an Event. If you have no Events for this VEN, you should return `None`.

.. _server_on_register_report:

on_register_report
------------------

The VEN informs you which reports it has available. If you want to periodically receive any of these reports, you should return a list of the r_ids that you want to receive.

Signature:

.. code-block:: python3

    async def on_register_report(ven_id, reports):


.. _server_on_created_report:

on_created_report
-----------------

The VEN informs you that it created the automatic reporting that you requested. You don't have to return anything.

Return: `None`

.. _server_on_update_report:

on_update_report
----------------

The VEN is sending you a fresh report with data. You don't have to return anything.

Signature:

.. code-block:: python3

    async def on_update_report(ven_id, report):
        ...
        return None

.. _server_on_poll:

on_poll
-------

The VEN is requesting the next message that you have for it. You should return a tuple of message_type and message_payload as a dict. If there is no message for the VEN, you should return `None`.

Signature:

.. code-block:: python3

    async def on_poll(ven_id):
        ...
        return message_type, message_payload

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

.. _server_on_cancel_party_registration:

on_cancel_party_registration
----------------------------

The VEN informs you that they are cancelling their registration and no longer wish to be contacted by you.

You should deregister the VEN internally, and return `None`.

Return: `None`
