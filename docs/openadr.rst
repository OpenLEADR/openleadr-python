==============
OpenADR Basics
==============

If you are coming to this module and are not (yet) familiar with the workings of OpenADR, read this.

High-level overview
===================

OpenADR is a protocol that allows a server (called a Virtual Top Node or VTNs) to communicate 'Events' to connected clients (Called Virtual End Nodes or VENs). These Events are usually energy-related instructions to temporarily increase or reduce the power consumption by one or more devices represented by the VEN. The VEN periodically (typically every 10 seconds or so) sends a Poll request to the VTN to check if there are new events for them.

The VEN will then decide whether or not to comply with the request in the Event, and send an Opt In or Opt Out response to the VTN.

In order to track what happens after, there is a Reports mechanism in place that allows the VEN and the VTN to agree on what data should be reported.


.. _registration:

Registration
============

Here is the registration page



.. _openadr_events:

Events
======

This is the registration

.. _openadr_reports:

Reports
=======

This is the reports
