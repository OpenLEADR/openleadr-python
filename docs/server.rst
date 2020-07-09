.. _server:

======
Server
======

The page contains all information about pyOpenADR Server API.


.. _server_registration:

Registration
============

If a client (VEN) wants to register for the first time, it will go through a Registration procedure.

The client will send a :ref:`oadrQueryRegistration` message. The server will respond with a :ref:`oadrCreatedPartyRegistration` message containing a list of its capabilities, notable the implemented OpenADR protocol versions and the available Transport Mechanisms (HTTP and/or XMPP).

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

In your application, the creation of Events is completely up to you. PyOpenADR will only call your ``on_poll`` handler with a ``ven_id``. This handler must be able to either retrieve the next event for this VEN out of some storage or queue, or make up the Event in real time.


.. _server_reports:

Reports
=======
