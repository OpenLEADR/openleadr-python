.. pyOpenAdr documentation master file, created by
   sphinx-quickstart on Thu Jul  9 14:09:27 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
Welcome to pyOpenADR
====================

Dead-simple Python implementation of an OpenADR client and server.

Key Features
============

- Fully compliant OpenADR 2.0b implementation for both servers (Virtual Top Node) and clients (Virtual End Node)
- Fully asyncio: you set up the coroutines that can handle certain events, and they get called when needed.
- All messages are represented as simple Python dictionaries. All XML parsing and generation is done for you.
- You only have to deal with your own logic.

Library Installation
====================

.. code-block:: bash

   $ pip install pyopenadr

pyOpenADR is compatible with Python 3.6+

Getting Started
===============

Client example::

    from pyopenadr import OpenADRClient
    import asyncio

    async def main():
        client = OpenADRClient(ven_name="Device001",
                               vtn_url="http://localhost:8080/OpenADR2/Simple/2.0b")
        client.on_event = handle_event
        client.on_report = handle_report
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

    async def handle_report(report):
        """
        This coroutine will be called
        when there is a report from the VTN.
        """
        print("There is a report!")
        print(report)

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()

This will connect to an OpenADR server (indicated by the vtn_url parameter), handle registration, start polling for events and reports, and will call your coroutines whenever an event or report is created for you.

We have more examples available over at the :ref:`examples` page.

Source Code
===========

The source code for this project is hosted at GitHub.

Table of Contents
=================

.. toctree::
   :name: mastertoc
   :maxdepth: 2

   openadr
   client
   server
   representations
   examples


Representations of OpenADR payloads
===================================

PyOpenADR uses Python dictionaries and vanilla Python types (like datetime and timedelta) to represent the OpenADR payloads. These pages serve as a reference to these representations.

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

is represented in pyOpenADR as:

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
