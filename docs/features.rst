.. _feature_tour:

############
Feature Tour
############

Automatic registration
----------------------

Registering your VEN to a VTN is a process that requires some service discovery, exchange of reporting capabilitiets, assignment of a VEN_ID, et cetera. You don't have to see any of this in your own code. Just create a new OpenADRClient instance, provide a VTN URL, a VEN name, optionally provide signing certificates and a verification fingerprint, and registration happens automatically.


Automatic reporting
-------------------

If you're implementing a VEN (client), you configure which types of reports you can offer, you provide handlers that retrieve the measurements, and OpenLEADR will take care of the rest. It will offer the reports to the VTN, allow the VTN to pick the reports it requires, and it will call your data collection handlers at a set interval, and pack up the values into the reports.

If you're implementing a VTN (server), you configure which types of reports you wish to receive, and it will automatically request these reports from the VEN. Whenever new data arrives, it will call one of your handlers so you can hand the data off to your own systems for processing and archiving.


Event-driven
------------

Once you have configured your client or server, all routine interactions happen automatically: polling for new Events, requesting reports, et cetera. Whenever OpenLEADR needs some information or data that it does not have, it will call your handlers in order to get it. Your handlers only have to deal with a very specific set of cases and they can usually be quite simple.


Dict-style representations
--------------------------

Although OpenADR is an XML-based protocol that is either transported over HTTP or XMPP, you don't need to see any XML or custom object types at all. You use native Python dicts (and native Python types like `datetime.datetime` and `datetime.timedelta`) in your handlers.


Message Signing for secure communications
-----------------------------------------

If you provide a PEM-formatted certificate and key, all outgoing messages will be cryptographically signed. If you also provide a fingerprint for the other side's certificate, incoming messages can be securely authenticated and verified.

