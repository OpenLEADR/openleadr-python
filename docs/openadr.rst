==============
OpenADR Basics
==============

If you are coming to this module and are not (yet) familiar with the OpenADR protocol, read this. Of course, you should also consult the documentation from `the OpenADR website <https://www.openadr.org>`_.

High-level overview
===================

OpenADR is a protocol that allows a server (called a Virtual Top Node or VTNs) to communicate 'Events' to connected clients (Called Virtual End Nodes or VENs). These Events are usually energy-related instructions, for instance to temporarily increase or reduce the power consumption by one or more devices represented by the VEN, or te inform the VEN that prices are about to change. The VEN periodically (typically every 10 seconds or so) sends a Poll request to the VTN to check if there are new events for them.

The VEN decides whether or not to comply with the request in the Event, and sends an Opt In or Opt Out response to the VTN.

In order to track what happens after, there is a Reports mechanism in place that allows the VEN and the VTN to agree on what data should be reported, and to report this data at a requested interval.

Although multiple transport formats are supported (HTTP and XMPP), OpenADR is designed for only the VTN to be public-accessible, with the VENs possibly being behind NAT or firewalls. All communications are therefore initiated by the client (VEN), and the server can request additional messages from the client in its response to the original request.


.. _registration:

Registration
============

(Information on the Registration procedures)



.. _openadr_events:

Events
======

(Information on the Events procedures)

.. _openadr_reports:

Reports
=======

(Information on the Reports procedures)
