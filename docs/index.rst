.. OpenLEADR documentation master file, created by
   sphinx-quickstart on Thu Jul  9 14:09:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
Welcome to OpenLEADR
====================

A friendly and compliant OpenADR implementation for Python 3.

Key Features
============

- Fully compliant OpenADR 2.0b implementation for both servers (Virtual Top Node) and clients (Virtual End Node)
- Fully asyncio: you set up the coroutines that can handle certain events, and they get called when needed.
- Fully pythonic: all messages are represented as simple Python dictionaries. All XML parsing and generation is done for you.

Take a :ref:`feature_tour`!

Project Status
==============

The current version is |release|.

This project is still a work in progress. Please see our :ref:`roadmap` for information.

License
=======

This project is licensed under the Apache 2.0 license.

Development and contributing
============================

The source code of this project can be found on `GitHub <https://github.com/openleadr>`_. Feature requests, bug reports and pull requests can be posted there.

Library Installation
====================

.. code-block:: bash

   $ pip install openleadr

OpenLEADR is compatible with Python 3.6+

Getting Started
===============

Client example::

    from openleadr import OpenADRClient
    import asyncio

    async def main():
        client = OpenADRClient(ven_name="Device001",
                               vtn_url="http://localhost:8080/OpenADR2/Simple/2.0b")
        client.on_event = handle_event
        await client.run()

    async def handle_event(event):
        """
        This coroutine will be called
        when there is an event to be handled.
        """
        print("There is an event!")
        print(event)
        # Do something to determine whether to Opt In or Opt Out
        return 'optIn'

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

This will connect to an OpenADR server (indicated by the vtn_url parameter), handle registration, start polling for events and reports, and will call your coroutines whenever an event or report is created for you.

We have more examples available over at the :ref:`examples` page.


Table of Contents
=================

.. toctree::
   :name: mastertoc
   :maxdepth: 2

   features
   openadr
   client
   server
   examples
   logging
   representations
   message_signing
   roadmap
   API Reference <api/modules>

Representations of OpenADR payloads
===================================

OpenLEADR uses Python dictionaries and vanilla Python types (like datetime and timedelta) to represent the OpenADR payloads. These pages serve as a reference to these representations.

For example, this XML payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrResponse ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads" />
          </ei:eiResponse>
          <ei:venID>o57b65be83</ei:venID>
        </oadrResponse>
      </oadrSignedObject>
    </oadrPayload>

is represented in OpenLEADR as:

.. code-block:: python3

    {'response': {'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': 'o57b65be83'}

Read more about the representations at :ref:`representations`


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
