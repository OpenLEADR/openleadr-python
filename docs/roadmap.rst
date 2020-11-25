.. _roadmap:

==========================
Project Roadmap
==========================

OpenLEADR is under development. The current version is |release|.

Upcoming releases
-----------------

======= ================================== ====================
Version Main features                      Target timeframe
======= ================================== ====================
0.6.0   Implement XMPP transport           Januari 2020
1.0.0   Certification by OpenADR Alliance  T.B.A.
======= ================================== ====================


Changelog
---------

openleadr 0.5.5
~~~~~~~~~~~~~~~

Released: 23 november 2020

New features:

- Message signing now uses the correct C14n algorithm, as required by OpenADR
- Preliminary VEN support for multiple events in one DistributeEvent message

openleadr 0.5.4
~~~~~~~~~~~~~~~

Released: 23 november 2020

New features:

- Preliminary support for TELEMETRY_STATUS reports
- Changed the server.add_event to be a normal function (not a coroutine), which allows you to call it from a synchronous function if needed.

openleadr 0.5.3
~~~~~~~~~~~~~~~

Released: 20 november 2020

New features:

- Support for custom units in Reports is back, and is now compliant with the XML Schema.
- Support for specifying the measurement (unit) in an EventSignal is added, and builds on the work of the report units.


openleadr 0.5.2
~~~~~~~~~~~~~~~

Released: 19 november 2020


Bug fixes:

- The 'full' report data collection mode now works correctly
- Various codestyle improvements and cleanup

Known issues:

- The support for out-of-schema measurements in repors has been removed, because they would not pass XML validation. We are exploring solutions to this problem. Track the progress here: `Issue #20 <https://github.com/OpenLEADR/openleadr-python/issues/20>`_

openleadr 0.5.1
~~~~~~~~~~~~~~~

Released: 19 november 2020

New features:

- When using SSL connections, the client will provide server side SSL certificates. The VTN will verify the fingerprint of these certificates against the known fingerprint for that ven. This should complete the VEN authentication process.


Bug fixes:

- Report messages now validate according to the XML schema. A few corrections were made to the templates from version 0.5.0.


Known issues:

- The support for out-of-schema measurements in repors has been removed, because they would not pass XML validation. We are exploring solutions to this problem. Track the progress here: `Issue #20 <https://github.com/OpenLEADR/openleadr-python/issues/20>`_


openleadr 0.5.0
~~~~~~~~~~~~~~~

Released: 16 november 2020

First release to pypi.org.

New features:

- This release implements reporting functionality into the client and the server. This is a major new area of functionality for OpenLEADR.

openleadr 0.4.0
~~~~~~~~~~~~~~~

Released: 16 november 2020

Only released to git.

New features:

- This release implements XML Message Signing for client and servers.

