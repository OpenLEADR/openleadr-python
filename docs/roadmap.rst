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

openleadr 0.5.11
~~~~~~~~~~~~~~~~

Released: 3 december 2020

New features:

- This update makes the list of Targets available as a dictionary of targets grouped by their type.
- You can now add Targets to events in multiple ways (``target``, ``targets``, and ``targets_by_type``).

Changes:

- The member names of the 'measurement' objects or dicts have been changed to be consistent everywhere:
    - item_name -> name
    - item_description -> description
    - item_units -> unit
    - si_scale_code -> scale
    This way, the parameters to client.add_report() are consistent with the Measurement object and the dicts that are passed around.
    Additionally, there is extra validation to prevent sending invalid measurements, and hints to correct any mistakes.


openleadr 0.5.10
~~~~~~~~~~~~~~~~

Released: 1 december 2020

Bug fixes:

- The on_created_event handler is now expected to receive the parameters (ven_id, event_id, opt_type). This was already in the docs, but not yet in the actual implementation. This has now been fixed.

openleadr 0.5.9
~~~~~~~~~~~~~~~

Released: 1 december 2020

New features:

- Added the ven fingerprint to the registration_info dict for the ``on_create_party_registration`` handler. This allows the VTN to verify the fingerprint upon registration, even when the VEN does not have a venID yet.

Changes:
- Converted the OpenADRServer.add_raw_event method to a normal (synchronous) method.

Bug fixes:
- The EiResponse.response_code would not always show up correctly, this is now fixed.

openleadr 0.5.8
~~~~~~~~~~~~~~~

Released: 30 november 2020

New features:

- Added the ``ven_id`` to the list of parameters for the ``on_register_report`` handler, so that this handler can know which VEN is registering reports
- Updated documentation to reflect the current API of OpenLEADR

openleadr 0.5.7
~~~~~~~~~~~~~~~

Released: 27 november 2020

Bugs fixed:

- Fixed a typo in the EventService.on_created_event placeholder function

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

