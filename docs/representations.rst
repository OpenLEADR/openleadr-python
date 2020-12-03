.. _representations:

=======================
Payload Representations
=======================

In OpenLEADR, the complex hierarchies of the OpenADR XML-payloads are represented as Python dictionaries. These have been simplified as much as possible, allowing for a more natural and more readable experience.

This means that you don't have to instantiate objects and sub-objects and sub-sub-objects, but that you can define the entire object in a single, declarative statement. This kan keep a simple implementation very compact. The downside is that there is little help from your IDE and there is little discoverability for what contents can be provided in the messages. This page can be used as a reference for that information.

To help you, all outgong messages are validated against the XML schema, and you will receive warnings if your messages don't comply to the schema.

The following general principles have been applied to representing OpenADR objects in OpenLEADR:

- All property names are represented in snake_case instead of CamelCase or mixedCase names. For example: ``requestID`` becomes ``request_id``.
- For all properties, the ``oadr*`` and ``Ei*`` prefixes have been stripped away. For example: ``eiResponse`` becomes ``response`` and ``oadrResponse`` becomes ``response``.
- OpenADR timestamps are converted to Python ``datetime.datetime`` objects.
- OpenADR time intervals are converted to Python ``datetime.timedelta`` objects.
- Properties that might have more than 1 copy in the XML representation are put in a list, even if there is just one. This list will be identified by the pluralized version of the original property name. For example:

.. code-block:: xml

    <...>
        <signal>1234</signal>
        <signal>5678</signal>
    <...>

Will become:

.. code-block:: python3

    ...
    "signals": [1234, 5678],
    ...

- The messages are usually used as a ``message_name, message_payload`` tuple. The message name is kept, for instance, ``oadrCanceledOpt``, and the payload is given as a dict.

Below is an alphabetized overview of all payloads with their XML and Python representations.

.. _oadrCanceledOpt:

oadrCanceledOpt
===============

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCanceledOpt xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">8d4a231d-ded4-48ee-b236-df2a7c436a15</requestID>
          </ei:eiResponse>
          <ei:optID>72c8a37d-508c-438c-a721-12269c6ca70d</ei:optID>
        </oadr:oadrCanceledOpt>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'opt_id': '72c8a37d-508c-438c-a721-12269c6ca70d',
     'response': {'request_id': '8d4a231d-ded4-48ee-b236-df2a7c436a15',
                  'response_code': 200,
                  'response_description': 'OK'}}


.. _oadrCanceledPartyRegistration:

oadrCanceledPartyRegistration
=============================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCanceledPartyRegistration xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">ef7ed945-c7af-45ae-a930-4868713cb150</requestID>
          </ei:eiResponse>
          <ei:registrationID>b01be3d8-5337-4e6c-80b1-805f13bb51b2</ei:registrationID>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrCanceledPartyRegistration>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'registration_id': 'b01be3d8-5337-4e6c-80b1-805f13bb51b2',
     'response': {'request_id': 'ef7ed945-c7af-45ae-a930-4868713cb150',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrCanceledReport:

oadrCanceledReport
==================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCanceledReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">845d63ae-c2a1-41e4-bd01-c4e8fc7743e2</requestID>
          </ei:eiResponse>
          <oadr:oadrPendingReports>
            <ei:reportRequestID>f63796ea-504f-4318-842b-86472873777f</ei:reportRequestID>
            <ei:reportRequestID>39ba35e5-6b3d-4b9e-8f29-d94a25e7079c</ei:reportRequestID>
          </oadr:oadrPendingReports>
        </oadr:oadrCanceledReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': 'f63796ea-504f-4318-842b-86472873777f'},
                         {'request_id': '39ba35e5-6b3d-4b9e-8f29-d94a25e7079c'}],
     'response': {'request_id': '845d63ae-c2a1-41e4-bd01-c4e8fc7743e2',
                  'response_code': 200,
                  'response_description': 'OK'}}


.. _oadrCanceledReport:

oadrCanceledReport
==================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCanceledReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">15a398db-c313-4a30-a8fd-080b682e48ad</requestID>
          </ei:eiResponse>
          <oadr:oadrPendingReports>
            <ei:reportRequestID>43722761-4cc3-4684-ae79-8ad2c14e3c3c</ei:reportRequestID>
            <ei:reportRequestID>bf4c3dfb-1175-4a9a-976a-ae81b52b4082</ei:reportRequestID>
          </oadr:oadrPendingReports>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrCanceledReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': '43722761-4cc3-4684-ae79-8ad2c14e3c3c'},
                         {'request_id': 'bf4c3dfb-1175-4a9a-976a-ae81b52b4082'}],
     'response': {'request_id': '15a398db-c313-4a30-a8fd-080b682e48ad',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrCancelOpt:

oadrCancelOpt
=============

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCancelOpt xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">95448074-273c-4d13-a202-d6a7672d6cb9</requestID>
          <ei:optID>f3fd6b1d-dffd-4f30-962b-fb19b1dd5b70</ei:optID>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrCancelOpt>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'opt_id': 'f3fd6b1d-dffd-4f30-962b-fb19b1dd5b70',
     'request_id': '95448074-273c-4d13-a202-d6a7672d6cb9',
     'ven_id': '123ABC'}


.. _oadrCancelPartyRegistration:

oadrCancelPartyRegistration
===========================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCancelPartyRegistration xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">4fb73f76-16ab-4c3c-8a04-bbb77bc637b7</requestID>
          <ei:registrationID>31c1113c-9512-4f42-a858-9a97b98f5597</ei:registrationID>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrCancelPartyRegistration>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'registration_id': '31c1113c-9512-4f42-a858-9a97b98f5597',
     'request_id': '4fb73f76-16ab-4c3c-8a04-bbb77bc637b7',
     'ven_id': '123ABC'}


.. _oadrCancelReport:

oadrCancelReport
================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCancelReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">0571ae19-b935-47c3-b457-4a0aec9ada0f</requestID>
          <ei:reportRequestID>273cb2df-c4b0-4efe-bda3-2cf76f6a3538</ei:reportRequestID>
          <reportToFollow xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">true</reportToFollow>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrCancelReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'report_request_id': '273cb2df-c4b0-4efe-bda3-2cf76f6a3538',
     'report_to_follow': True,
     'request_id': '0571ae19-b935-47c3-b457-4a0aec9ada0f',
     'ven_id': '123ABC'}


.. _oadrCreatedEvent:

oadrCreatedEvent
================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreatedEvent xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <eiCreatedEvent xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">
            <ei:eiResponse>
              <ei:responseCode>200</ei:responseCode>
              <ei:responseDescription>OK</ei:responseDescription>
              <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">a4740d85-7682-423c-b8c6-211117f087b6</requestID>
            </ei:eiResponse>
            <ei:eventResponses>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">b9636992-8ce2-4f4b-aac3-ec6f1e42afd7</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>011d969c-9481-4c03-af00-e9ec3c018ceb</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">d77d6ed7-3bbb-4e7b-ae44-c816f9974a89</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>4d66b7a2-e7ca-4eca-99d4-c67dda00f1f4</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">b363c569-c459-4e84-8725-5388eabbf160</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>b73bb2b5-3c5c-424c-93ec-23b36881f803</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
            </ei:eventResponses>
            <ei:venID>123ABC</ei:venID>
          </eiCreatedEvent>
        </oadr:oadrCreatedEvent>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'event_responses': [{'event_id': '011d969c-9481-4c03-af00-e9ec3c018ceb',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'b9636992-8ce2-4f4b-aac3-ec6f1e42afd7',
                          'response_code': 200,
                          'response_description': 'OK'},
                         {'event_id': '4d66b7a2-e7ca-4eca-99d4-c67dda00f1f4',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'd77d6ed7-3bbb-4e7b-ae44-c816f9974a89',
                          'response_code': 200,
                          'response_description': 'OK'},
                         {'event_id': 'b73bb2b5-3c5c-424c-93ec-23b36881f803',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'b363c569-c459-4e84-8725-5388eabbf160',
                          'response_code': 200,
                          'response_description': 'OK'}],
     'response': {'request_id': 'a4740d85-7682-423c-b8c6-211117f087b6',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrCreatedReport:

oadrCreatedReport
=================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreatedReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">1bb8cdc4-5d02-4bf1-b78b-6d09db5c55f7</requestID>
          </ei:eiResponse>
          <oadr:oadrPendingReports>
            <ei:reportRequestID>8a04e06b-7836-4513-ae11-f1d08c248f4b</ei:reportRequestID>
            <ei:reportRequestID>9193998f-adf2-426d-8475-52e0553a997c</ei:reportRequestID>
          </oadr:oadrPendingReports>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrCreatedReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': '8a04e06b-7836-4513-ae11-f1d08c248f4b'},
                         {'request_id': '9193998f-adf2-426d-8475-52e0553a997c'}],
     'response': {'request_id': '1bb8cdc4-5d02-4bf1-b78b-6d09db5c55f7',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrCreatedEvent:

oadrCreatedEvent
================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreatedEvent xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <eiCreatedEvent xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">
            <ei:eiResponse>
              <ei:responseCode>200</ei:responseCode>
              <ei:responseDescription>OK</ei:responseDescription>
              <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">cd07668c-f675-4859-ae2d-b32f218609a3</requestID>
            </ei:eiResponse>
            <ei:eventResponses>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">cff4b658-b2dc-478b-a67c-9724c129ae1e</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>9388d5e4-005e-46c3-b4d0-a3527f406a0e</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">6b155b7c-b562-4774-9e80-ef94466376bb</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>63aec037-6e13-4463-8000-119d2190bfdd</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optOut</ei:optType>
              </ei:eventResponse>
            </ei:eventResponses>
            <ei:venID>123ABC</ei:venID>
          </eiCreatedEvent>
        </oadr:oadrCreatedEvent>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'event_responses': [{'event_id': '9388d5e4-005e-46c3-b4d0-a3527f406a0e',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'cff4b658-b2dc-478b-a67c-9724c129ae1e',
                          'response_code': 200,
                          'response_description': 'OK'},
                         {'event_id': '63aec037-6e13-4463-8000-119d2190bfdd',
                          'modification_number': 1,
                          'opt_type': 'optOut',
                          'request_id': '6b155b7c-b562-4774-9e80-ef94466376bb',
                          'response_code': 200,
                          'response_description': 'OK'}],
     'response': {'request_id': 'cd07668c-f675-4859-ae2d-b32f218609a3',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrCreatedPartyRegistration:

oadrCreatedPartyRegistration
============================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreatedPartyRegistration xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">14ab2770-c92a-4d11-b00f-129768d0964d</requestID>
          </ei:eiResponse>
          <ei:registrationID>0271323d-fd75-490f-ab05-4fcb846e00b8</ei:registrationID>
          <ei:venID>123ABC</ei:venID>
          <ei:vtnID>VTN123</ei:vtnID>
          <oadr:oadrProfiles>
            <oadr:oadrProfile>
              <oadr:oadrProfileName>2.0b</oadr:oadrProfileName>
              <oadr:oadrTransports>
                <oadr:oadrTransport>
                  <oadr:oadrTransportName>simpleHttp</oadr:oadrTransportName>
                </oadr:oadrTransport>
              </oadr:oadrTransports>
            </oadr:oadrProfile>
          </oadr:oadrProfiles>
        </oadr:oadrCreatedPartyRegistration>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'profiles': [{'profile_name': '2.0b',
                   'transports': [{'transport_name': 'simpleHttp'}]}],
     'registration_id': '0271323d-fd75-490f-ab05-4fcb846e00b8',
     'response': {'request_id': '14ab2770-c92a-4d11-b00f-129768d0964d',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC',
     'vtn_id': 'VTN123'}


.. _oadrCreatedReport:

oadrCreatedReport
=================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreatedReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">5b14fda6-e7b6-492e-8a5b-8576e48b7c19</requestID>
          </ei:eiResponse>
          <oadr:oadrPendingReports>
            <ei:reportRequestID>05ac1205-bac7-4c41-8f61-7ff95e80deff</ei:reportRequestID>
            <ei:reportRequestID>9aa68adb-7b46-4e3d-850d-344e82484e06</ei:reportRequestID>
          </oadr:oadrPendingReports>
        </oadr:oadrCreatedReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': '05ac1205-bac7-4c41-8f61-7ff95e80deff'},
                         {'request_id': '9aa68adb-7b46-4e3d-850d-344e82484e06'}],
     'response': {'request_id': '5b14fda6-e7b6-492e-8a5b-8576e48b7c19',
                  'response_code': 200,
                  'response_description': 'OK'}}


.. _oadrCreateOpt:

oadrCreateOpt
=============

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreateOpt xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0" xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06" ei:schemaVersion="2.0b">
          <ei:optID>745e589d-19d5-43fb-86fa-e499504339a6</ei:optID>
          <ei:optType>optIn</ei:optType>
          <ei:optReason>participating</ei:optReason>
          <ei:venID>VEN123</ei:venID>
          <ei:createdDateTime>2020-12-03T14:22:07.606847Z </ei:createdDateTime>
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">a5590690-cb65-47a6-9eb7-4951c3d6d865</requestID>
          <ei:qualifiedEventID>
            <ei:eventID>36eb3e4e-3959-4f32-a2ed-725e54c11cb7</ei:eventID>
            <ei:modificationNumber>1</ei:modificationNumber>
          </ei:qualifiedEventID>
          <ei:eiTarget>
            <ei:venID>123ABC</ei:venID>
          </ei:eiTarget>
        </oadr:oadrCreateOpt>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'created_date_time': datetime.datetime(2020, 12, 3, 14, 22, 7, 606847, tzinfo=datetime.timezone.utc),
     'event_id': '36eb3e4e-3959-4f32-a2ed-725e54c11cb7',
     'modification_number': 1,
     'opt_id': '745e589d-19d5-43fb-86fa-e499504339a6',
     'opt_reason': 'participating',
     'opt_type': 'optIn',
     'request_id': 'a5590690-cb65-47a6-9eb7-4951c3d6d865',
     'targets': [{'ven_id': '123ABC'}],
     'targets_by_type': {'ven_id': ['123ABC']},
     'ven_id': 'VEN123'}


.. _oadrCreatePartyRegistration:

oadrCreatePartyRegistration
===========================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreatePartyRegistration xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">2774add6-fc64-4167-9dd1-602ce68639f2</requestID>
          <ei:venID>123ABC</ei:venID>
          <oadr:oadrProfileName>2.0b</oadr:oadrProfileName>
          <oadr:oadrTransportName>simpleHttp</oadr:oadrTransportName>
          <oadr:oadrTransportAddress>http://localhost</oadr:oadrTransportAddress>
          <oadr:oadrReportOnly>false</oadr:oadrReportOnly>
          <oadr:oadrXmlSignature>false</oadr:oadrXmlSignature>
          <oadr:oadrVenName>test</oadr:oadrVenName>
          <oadr:oadrHttpPullModel>true</oadr:oadrHttpPullModel>
        </oadr:oadrCreatePartyRegistration>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'http_pull_model': True,
     'profile_name': '2.0b',
     'report_only': False,
     'request_id': '2774add6-fc64-4167-9dd1-602ce68639f2',
     'transport_address': 'http://localhost',
     'transport_name': 'simpleHttp',
     'ven_id': '123ABC',
     'ven_name': 'test',
     'xml_signature': False}


.. _oadrCreateReport:

oadrCreateReport
================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrCreateReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">365e7ddd-7193-4a6a-8a48-7632f32e772a</requestID>
          <oadr:oadrReportRequest>
            <ei:reportRequestID>d2b7bade5f</ei:reportRequestID>
            <ei:reportSpecifier xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0">
              <ei:reportSpecifierID>9c8bdc00e7</ei:reportSpecifierID>
              <xcal:granularity>
                <xcal:duration>PT15M</xcal:duration>
              </xcal:granularity>
              <ei:reportBackDuration>
                <xcal:duration>PT15M</xcal:duration>
              </ei:reportBackDuration>
              <ei:reportInterval>
                <xcal:properties>
                  <xcal:dtstart>
                    <xcal:date-time>2019-11-19T11:00:18.672768Z</xcal:date-time>
                  </xcal:dtstart>
                  <xcal:duration>
                    <xcal:duration>PT2H</xcal:duration>
                  </xcal:duration>
                </xcal:properties>
              </ei:reportInterval>
              <ei:specifierPayload>
                <ei:rID>d6e2e07485</ei:rID>
                <ei:readingType>Direct Read</ei:readingType>
              </ei:specifierPayload>
            </ei:reportSpecifier>
          </oadr:oadrReportRequest>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrCreateReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'report_requests': [{'report_request_id': 'd2b7bade5f',
                          'report_specifier': {'granularity': datetime.timedelta(seconds=900),
                                               'report_back_duration': datetime.timedelta(seconds=900),
                                               'report_interval': {'dtstart': datetime.datetime(2019, 11, 19, 11, 0, 18, 672768, tzinfo=datetime.timezone.utc),
                                                                   'duration': datetime.timedelta(seconds=7200)},
                                               'report_specifier_id': '9c8bdc00e7',
                                               'specifier_payloads': [{'r_id': 'd6e2e07485',
                                                                       'reading_type': 'Direct '
                                                                                       'Read'}]}}],
     'request_id': '365e7ddd-7193-4a6a-8a48-7632f32e772a',
     'ven_id': '123ABC'}


.. _oadrDistributeEvent:

oadrDistributeEvent
===================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrDistributeEvent xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">123</requestID>
          </ei:eiResponse>
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">2f888a2c-dcc2-4424-8084-57c26a49fa06</requestID>
          <ei:vtnID>VTN123</ei:vtnID>
          <oadr:oadrEvent>
            <ei:eiEvent>
              <ei:eventDescriptor>
                <ei:eventID>541c76cb-36db-4ece-bf06-1ec80d06aa5d</ei:eventID>
                <ei:modificationNumber>1</ei:modificationNumber>
                <ei:modificationDateTime>2020-12-03T14:22:07.606894Z</ei:modificationDateTime>
                <ei:priority>1</ei:priority>
                <ei:eiMarketContext>
                  <marketContext xmlns="http://docs.oasis-open.org/ns/emix/2011/06">http://MarketContext1</marketContext>
                </ei:eiMarketContext>
                <ei:createdDateTime>2020-12-03T14:22:07.606894Z</ei:createdDateTime>
                <ei:eventStatus>near</ei:eventStatus>
                <ei:testEvent>false</ei:testEvent>
                <ei:vtnComment>This is an event</ei:vtnComment>
              </ei:eventDescriptor>
              <ei:eiActivePeriod>
                <properties xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                  <dtstart>
                    <date-time>2020-12-03T14:23:07.606894Z</date-time>
                  </dtstart>
                  <duration>
                    <duration>PT9M</duration>
                  </duration>
                </properties>
                <components xmlns="urn:ietf:params:xml:ns:icalendar-2.0"/>
              </ei:eiActivePeriod>
              <ei:eiEventSignals>
                <ei:eiEventSignal>
                  <strm:intervals xmlns:strm="urn:ietf:params:xml:ns:icalendar-2.0:stream" xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0">
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>0</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>8.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>1</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>10.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>2</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>12.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>3</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>14.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>4</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>16.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>5</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>18.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>6</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>20.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>7</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>10.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <xcal:duration>
                        <xcal:duration>PT1M</xcal:duration>
                      </xcal:duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>8</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>20.0</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                  </strm:intervals>
                  <ei:signalName>LOAD_CONTROL</ei:signalName>
                  <ei:signalType>x-loadControlCapacity</ei:signalType>
                  <ei:signalID>ca5a2b4b-69b4-40ee-93ca-dbfa23da545d</ei:signalID>
                  <power:voltage xmlns:scale="http://docs.oasis-open.org/ns/emix/2011/06/siscale" xmlns:power="http://docs.oasis-open.org/ns/emix/2011/06/power">
                    <power:itemDescription>Voltage</power:itemDescription>
                    <power:itemUnits>V</power:itemUnits>
                    <scale:siScaleCode>none</scale:siScaleCode>
                  </power:voltage>
                  <ei:currentValue>
                    <ei:payloadFloat>
                      <ei:value>0.0</ei:value>
                    </ei:payloadFloat>
                  </ei:currentValue>
                </ei:eiEventSignal>
              </ei:eiEventSignals>
              <ei:eiTarget>
                <ei:venID>VEN001</ei:venID>
                <ei:venID>VEN002</ei:venID>
              </ei:eiTarget>
            </ei:eiEvent>
            <oadr:oadrResponseRequired>always</oadr:oadrResponseRequired>
          </oadr:oadrEvent>
        </oadr:oadrDistributeEvent>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'events': [{'active_period': {'dtstart': datetime.datetime(2020, 12, 3, 14, 23, 7, 606894, tzinfo=datetime.timezone.utc),
                                   'duration': datetime.timedelta(seconds=540)},
                 'event_descriptor': {'created_date_time': datetime.datetime(2020, 12, 3, 14, 22, 7, 606894, tzinfo=datetime.timezone.utc),
                                      'event_id': '541c76cb-36db-4ece-bf06-1ec80d06aa5d',
                                      'event_status': 'near',
                                      'market_context': 'http://MarketContext1',
                                      'modification_date_time': datetime.datetime(2020, 12, 3, 14, 22, 7, 606894, tzinfo=datetime.timezone.utc),
                                      'modification_number': 1,
                                      'priority': 1,
                                      'test_event': False,
                                      'vtn_comment': 'This is an event'},
                 'event_signals': [{'current_value': 0.0,
                                    'intervals': [{'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 8.0,
                                                   'uid': 0},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 10.0,
                                                   'uid': 1},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 12.0,
                                                   'uid': 2},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 14.0,
                                                   'uid': 3},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 16.0,
                                                   'uid': 4},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 18.0,
                                                   'uid': 5},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 20.0,
                                                   'uid': 6},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 10.0,
                                                   'uid': 7},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 20.0,
                                                   'uid': 8}],
                                    'measurement': {'description': 'Voltage',
                                                    'name': 'voltage',
                                                    'scale': 'none',
                                                    'unit': 'V'},
                                    'signal_id': 'ca5a2b4b-69b4-40ee-93ca-dbfa23da545d',
                                    'signal_name': 'LOAD_CONTROL',
                                    'signal_type': 'x-loadControlCapacity'}],
                 'response_required': 'always',
                 'targets': [{'ven_id': 'VEN001'}, {'ven_id': 'VEN002'}],
                 'targets_by_type': {'ven_id': ['VEN001', 'VEN002']}}],
     'request_id': '2f888a2c-dcc2-4424-8084-57c26a49fa06',
     'response': {'request_id': 123,
                  'response_code': 200,
                  'response_description': 'OK'},
     'vtn_id': 'VTN123'}


.. _oadrPoll:

oadrPoll
========

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrPoll xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrPoll>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'ven_id': '123ABC'}


.. _oadrQueryRegistration:

oadrQueryRegistration
=====================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrQueryRegistration xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">455dd699-ab81-4df6-8f74-79100db81082</requestID>
        </oadr:oadrQueryRegistration>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'request_id': '455dd699-ab81-4df6-8f74-79100db81082'}


.. _oadrRegisteredReport:

oadrRegisteredReport
====================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrRegisteredReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">19906000-b93a-4c09-a828-2cfed5b46232</requestID>
          </ei:eiResponse>
          <oadr:oadrReportRequest>
            <ei:reportRequestID>7b72a678-950a-48fd-9885-359af6a30033</ei:reportRequestID>
            <ei:reportSpecifier xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0">
              <ei:reportSpecifierID>f5b4071e-1825-4ddf-8100-3d487e3744ff</ei:reportSpecifierID>
              <xcal:granularity>
                <xcal:duration>PT15M</xcal:duration>
              </xcal:granularity>
              <ei:reportBackDuration>
                <xcal:duration>PT15M</xcal:duration>
              </ei:reportBackDuration>
              <ei:reportInterval>
                <xcal:properties>
                  <xcal:dtstart>
                    <xcal:date-time>2020-12-03T14:22:07.606944Z</xcal:date-time>
                  </xcal:dtstart>
                  <xcal:duration>
                    <xcal:duration>PT2H</xcal:duration>
                  </xcal:duration>
                </xcal:properties>
              </ei:reportInterval>
              <ei:specifierPayload>
                <ei:rID>7616cdd8-c54b-4060-985f-05b033d2a97e</ei:rID>
                <ei:readingType>Direct Read</ei:readingType>
              </ei:specifierPayload>
            </ei:reportSpecifier>
          </oadr:oadrReportRequest>
          <oadr:oadrReportRequest>
            <ei:reportRequestID>d157baf8-db5f-44b7-9f2c-5e18b4b4799b</ei:reportRequestID>
            <ei:reportSpecifier xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0">
              <ei:reportSpecifierID>811d8648-2f81-48ee-85f0-6c45613a2736</ei:reportSpecifierID>
              <xcal:granularity>
                <xcal:duration>PT15M</xcal:duration>
              </xcal:granularity>
              <ei:reportBackDuration>
                <xcal:duration>PT15M</xcal:duration>
              </ei:reportBackDuration>
              <ei:reportInterval>
                <xcal:properties>
                  <xcal:dtstart>
                    <xcal:date-time>2020-12-03T14:22:07.606964Z</xcal:date-time>
                  </xcal:dtstart>
                  <xcal:duration>
                    <xcal:duration>PT2H</xcal:duration>
                  </xcal:duration>
                </xcal:properties>
              </ei:reportInterval>
              <ei:specifierPayload>
                <ei:rID>81cbec7c-01a8-4d80-a99a-0957cce79839</ei:rID>
                <ei:readingType>Direct Read</ei:readingType>
              </ei:specifierPayload>
            </ei:reportSpecifier>
          </oadr:oadrReportRequest>
          <ei:venID>VEN123</ei:venID>
        </oadr:oadrRegisteredReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'report_requests': [{'report_request_id': '7b72a678-950a-48fd-9885-359af6a30033',
                          'report_specifier': {'granularity': datetime.timedelta(seconds=900),
                                               'report_back_duration': datetime.timedelta(seconds=900),
                                               'report_interval': {'dtstart': datetime.datetime(2020, 12, 3, 14, 22, 7, 606944, tzinfo=datetime.timezone.utc),
                                                                   'duration': datetime.timedelta(seconds=7200)},
                                               'report_specifier_id': 'f5b4071e-1825-4ddf-8100-3d487e3744ff',
                                               'specifier_payloads': [{'r_id': '7616cdd8-c54b-4060-985f-05b033d2a97e',
                                                                       'reading_type': 'Direct '
                                                                                       'Read'}]}},
                         {'report_request_id': 'd157baf8-db5f-44b7-9f2c-5e18b4b4799b',
                          'report_specifier': {'granularity': datetime.timedelta(seconds=900),
                                               'report_back_duration': datetime.timedelta(seconds=900),
                                               'report_interval': {'dtstart': datetime.datetime(2020, 12, 3, 14, 22, 7, 606964, tzinfo=datetime.timezone.utc),
                                                                   'duration': datetime.timedelta(seconds=7200)},
                                               'report_specifier_id': '811d8648-2f81-48ee-85f0-6c45613a2736',
                                               'specifier_payloads': [{'r_id': '81cbec7c-01a8-4d80-a99a-0957cce79839',
                                                                       'reading_type': 'Direct '
                                                                                       'Read'}]}}],
     'response': {'request_id': '19906000-b93a-4c09-a828-2cfed5b46232',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': 'VEN123'}


.. _oadrRequestEvent:

oadrRequestEvent
================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrRequestEvent xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <eiRequestEvent xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">
            <requestID>58b56698-20e3-43f1-bae2-aa95e2cea367</requestID>
            <ei:venID>123ABC</ei:venID>
          </eiRequestEvent>
        </oadr:oadrRequestEvent>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'request_id': '58b56698-20e3-43f1-bae2-aa95e2cea367', 'ven_id': '123ABC'}


.. _oadrRequestReregistration:

oadrRequestReregistration
=========================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrRequestReregistration xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrRequestReregistration>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'ven_id': '123ABC'}


.. _oadrRegisterReport:

oadrRegisterReport
==================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrRegisterReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">d37a5398-50f0-45bd-9b19-6b5b6bb61c02</requestID>
          <oadr:oadrReport xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0" xmlns:strm="urn:ietf:params:xml:ns:icalendar-2.0:stream">
            <ei:eiReportID>62ae2f36-49b8-49c9-8ffc-4af19a536b17</ei:eiReportID>
            <oadr:oadrReportDescription xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
              <ei:rID>08dd7433-2798-4a9f-a030-0a0b5021fdc8</ei:rID>
              <ei:reportSubject>
                <ei:resourceID>123ABC</ei:resourceID>
              </ei:reportSubject>
              <ei:reportDataSource>
                <ei:resourceID>123ABC</ei:resourceID>
              </ei:reportDataSource>
              <ei:reportType>reading</ei:reportType>
              <ei:readingType>Direct Read</ei:readingType>
              <emix:marketContext>http://localhost</emix:marketContext>
              <oadr:oadrSamplingRate>
                <oadr:oadrMinPeriod>PT1M</oadr:oadrMinPeriod>
                <oadr:oadrMaxPeriod>PT1M</oadr:oadrMaxPeriod>
                <oadr:oadrOnChange>true</oadr:oadrOnChange>
              </oadr:oadrSamplingRate>
            </oadr:oadrReportDescription>
            <ei:reportRequestID>f585d124-96ee-46f4-b882-c106dbc0d90e</ei:reportRequestID>
            <ei:reportSpecifierID>96e61860-b171-4ce4-8715-5a47894f59d3</ei:reportSpecifierID>
            <ei:reportName>METADATA_HISTORY_USAGE</ei:reportName>
            <ei:createdDateTime>2020-12-03T14:22:07.607003Z</ei:createdDateTime>
          </oadr:oadrReport>
          <ei:venID>123ABC</ei:venID>
          <ei:reportRequestID>54451870-32f1-4ad1-b9c4-27120f8b354c</ei:reportRequestID>
        </oadr:oadrRegisterReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'report_request_id': '54451870-32f1-4ad1-b9c4-27120f8b354c',
     'reports': [{'created_date_time': datetime.datetime(2020, 12, 3, 14, 22, 7, 607003, tzinfo=datetime.timezone.utc),
                  'report_descriptions': [{'market_context': 'http://localhost',
                                           'r_id': '08dd7433-2798-4a9f-a030-0a0b5021fdc8',
                                           'reading_type': 'Direct Read',
                                           'report_data_source': {'resource_id': '123ABC'},
                                           'report_subject': {'resource_id': '123ABC'},
                                           'report_type': 'reading',
                                           'sampling_rate': {'max_period': datetime.timedelta(seconds=60),
                                                             'min_period': datetime.timedelta(seconds=60),
                                                             'on_change': True}}],
                  'report_id': '62ae2f36-49b8-49c9-8ffc-4af19a536b17',
                  'report_name': 'METADATA_HISTORY_USAGE',
                  'report_request_id': 'f585d124-96ee-46f4-b882-c106dbc0d90e',
                  'report_specifier_id': '96e61860-b171-4ce4-8715-5a47894f59d3'}],
     'request_id': 'd37a5398-50f0-45bd-9b19-6b5b6bb61c02',
     'ven_id': '123ABC'}


.. _oadrRegisterReport:

oadrRegisterReport
==================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrRegisterReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">8a4f859883</requestID>
          <oadr:oadrReport xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0" xmlns:strm="urn:ietf:params:xml:ns:icalendar-2.0:stream">
            <xcal:duration>
              <xcal:duration>PT2H</xcal:duration>
            </xcal:duration>
            <ei:eiReportID>622e2178-afa1-46e5-89ec-f00387fea5b0</ei:eiReportID>
            <oadr:oadrReportDescription xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
              <ei:rID>1aed6a1f-f8c9-4fc1-9de1-1a0c5e1cd67a</ei:rID>
              <ei:reportDataSource>
                <ei:resourceID>resource1</ei:resourceID>
              </ei:reportDataSource>
              <ei:reportType>x-resourceStatus</ei:reportType>
              <ei:readingType>x-notApplicable</ei:readingType>
              <emix:marketContext>http://MarketContext1</emix:marketContext>
              <oadr:oadrSamplingRate>
                <oadr:oadrMinPeriod>PT1M</oadr:oadrMinPeriod>
                <oadr:oadrMaxPeriod>PT1M</oadr:oadrMaxPeriod>
                <oadr:oadrOnChange>false</oadr:oadrOnChange>
              </oadr:oadrSamplingRate>
            </oadr:oadrReportDescription>
            <ei:reportRequestID>fd27d669-9917-4096-ba1e-c3f5ae8a6886</ei:reportRequestID>
            <ei:reportSpecifierID>789ed6cd4e_telemetry_status</ei:reportSpecifierID>
            <ei:reportName>METADATA_TELEMETRY_STATUS</ei:reportName>
            <ei:createdDateTime>2019-11-20T15:04:52.638621Z</ei:createdDateTime>
          </oadr:oadrReport>
          <oadr:oadrReport xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0" xmlns:strm="urn:ietf:params:xml:ns:icalendar-2.0:stream">
            <xcal:duration>
              <xcal:duration>PT2H</xcal:duration>
            </xcal:duration>
            <ei:eiReportID>584d3b60-a8c6-4967-9f32-599a615a57c6</ei:eiReportID>
            <oadr:oadrReportDescription xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
              <ei:rID>resource1_energy</ei:rID>
              <ei:reportDataSource>
                <ei:resourceID>resource1</ei:resourceID>
              </ei:reportDataSource>
              <ei:reportType>usage</ei:reportType>
              <power:energyReal xmlns:scale="http://docs.oasis-open.org/ns/emix/2011/06/siscale" xmlns:power="http://docs.oasis-open.org/ns/emix/2011/06/power">
                <power:itemDescription>RealEnergy</power:itemDescription>
                <power:itemUnits>Wh</power:itemUnits>
                <scale:siScaleCode>n</scale:siScaleCode>
              </power:energyReal>
              <ei:readingType>Direct Read</ei:readingType>
              <emix:marketContext>http://MarketContext1</emix:marketContext>
              <oadr:oadrSamplingRate>
                <oadr:oadrMinPeriod>PT1M</oadr:oadrMinPeriod>
                <oadr:oadrMaxPeriod>PT1M</oadr:oadrMaxPeriod>
                <oadr:oadrOnChange>false</oadr:oadrOnChange>
              </oadr:oadrSamplingRate>
            </oadr:oadrReportDescription>
            <oadr:oadrReportDescription xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
              <ei:rID>resource1_power</ei:rID>
              <ei:reportDataSource>
                <ei:resourceID>resource1</ei:resourceID>
              </ei:reportDataSource>
              <ei:reportType>usage</ei:reportType>
              <power:powerReal xmlns:scale="http://docs.oasis-open.org/ns/emix/2011/06/siscale" xmlns:power="http://docs.oasis-open.org/ns/emix/2011/06/power">
                <power:itemDescription>RealPower</power:itemDescription>
                <power:itemUnits>W</power:itemUnits>
                <scale:siScaleCode>n</scale:siScaleCode>
                <power:powerAttributes>
                  <power:hertz>50</power:hertz>
                  <power:voltage>230</power:voltage>
                  <power:ac>true</power:ac>
                </power:powerAttributes>
              </power:powerReal>
              <ei:readingType>Direct Read</ei:readingType>
              <emix:marketContext>http://MarketContext1</emix:marketContext>
              <oadr:oadrSamplingRate>
                <oadr:oadrMinPeriod>PT1M</oadr:oadrMinPeriod>
                <oadr:oadrMaxPeriod>PT1M</oadr:oadrMaxPeriod>
                <oadr:oadrOnChange>false</oadr:oadrOnChange>
              </oadr:oadrSamplingRate>
            </oadr:oadrReportDescription>
            <ei:reportRequestID>538cf64f-901f-4bdf-ac7c-f5f72d4b4682</ei:reportRequestID>
            <ei:reportSpecifierID>789ed6cd4e_telemetry_usage</ei:reportSpecifierID>
            <ei:reportName>METADATA_TELEMETRY_USAGE</ei:reportName>
            <ei:createdDateTime>2019-11-20T15:04:52.638621Z</ei:createdDateTime>
          </oadr:oadrReport>
          <oadr:oadrReport xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0" xmlns:strm="urn:ietf:params:xml:ns:icalendar-2.0:stream">
            <xcal:duration>
              <xcal:duration>PT2H</xcal:duration>
            </xcal:duration>
            <ei:eiReportID>41907ef1-2f5b-45aa-b5fb-171098145438</ei:eiReportID>
            <oadr:oadrReportDescription xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
              <ei:rID>resource1_energy</ei:rID>
              <ei:reportDataSource>
                <ei:resourceID>resource1</ei:resourceID>
              </ei:reportDataSource>
              <ei:reportType>usage</ei:reportType>
              <power:energyReal xmlns:scale="http://docs.oasis-open.org/ns/emix/2011/06/siscale" xmlns:power="http://docs.oasis-open.org/ns/emix/2011/06/power">
                <power:itemDescription>RealEnergy</power:itemDescription>
                <power:itemUnits>Wh</power:itemUnits>
                <scale:siScaleCode>n</scale:siScaleCode>
              </power:energyReal>
              <ei:readingType>Direct Read</ei:readingType>
              <emix:marketContext>http://MarketContext1</emix:marketContext>
              <oadr:oadrSamplingRate>
                <oadr:oadrMinPeriod>PT1M</oadr:oadrMinPeriod>
                <oadr:oadrMaxPeriod>PT1M</oadr:oadrMaxPeriod>
                <oadr:oadrOnChange>false</oadr:oadrOnChange>
              </oadr:oadrSamplingRate>
            </oadr:oadrReportDescription>
            <oadr:oadrReportDescription xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
              <ei:rID>resource1_power</ei:rID>
              <ei:reportDataSource>
                <ei:resourceID>resource1</ei:resourceID>
              </ei:reportDataSource>
              <ei:reportType>usage</ei:reportType>
              <power:powerReal xmlns:scale="http://docs.oasis-open.org/ns/emix/2011/06/siscale" xmlns:power="http://docs.oasis-open.org/ns/emix/2011/06/power">
                <power:itemDescription>RealPower</power:itemDescription>
                <power:itemUnits>W</power:itemUnits>
                <scale:siScaleCode>n</scale:siScaleCode>
                <power:powerAttributes>
                  <power:hertz>50</power:hertz>
                  <power:voltage>230</power:voltage>
                  <power:ac>true</power:ac>
                </power:powerAttributes>
              </power:powerReal>
              <ei:readingType>Direct Read</ei:readingType>
              <emix:marketContext>http://MarketContext1</emix:marketContext>
              <oadr:oadrSamplingRate>
                <oadr:oadrMinPeriod>PT1M</oadr:oadrMinPeriod>
                <oadr:oadrMaxPeriod>PT1M</oadr:oadrMaxPeriod>
                <oadr:oadrOnChange>false</oadr:oadrOnChange>
              </oadr:oadrSamplingRate>
            </oadr:oadrReportDescription>
            <ei:reportRequestID>2244c5fd-44e2-4354-8aa0-97618cb1aa3a</ei:reportRequestID>
            <ei:reportSpecifierID>789ed6cd4e_history_usage</ei:reportSpecifierID>
            <ei:reportName>METADATA_HISTORY_USAGE</ei:reportName>
            <ei:createdDateTime>2019-11-20T15:04:52.638621Z</ei:createdDateTime>
          </oadr:oadrReport>
          <ei:venID>s3cc244ee6</ei:venID>
        </oadr:oadrRegisterReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'reports': [{'created_date_time': datetime.datetime(2019, 11, 20, 15, 4, 52, 638621, tzinfo=datetime.timezone.utc),
                  'duration': datetime.timedelta(seconds=7200),
                  'report_descriptions': [{'market_context': 'http://MarketContext1',
                                           'r_id': '1aed6a1f-f8c9-4fc1-9de1-1a0c5e1cd67a',
                                           'reading_type': 'x-notApplicable',
                                           'report_data_source': {'resource_id': 'resource1'},
                                           'report_type': 'x-resourceStatus',
                                           'sampling_rate': {'max_period': datetime.timedelta(seconds=60),
                                                             'min_period': datetime.timedelta(seconds=60),
                                                             'on_change': False}}],
                  'report_id': '622e2178-afa1-46e5-89ec-f00387fea5b0',
                  'report_name': 'METADATA_TELEMETRY_STATUS',
                  'report_request_id': 'fd27d669-9917-4096-ba1e-c3f5ae8a6886',
                  'report_specifier_id': '789ed6cd4e_telemetry_status'},
                 {'created_date_time': datetime.datetime(2019, 11, 20, 15, 4, 52, 638621, tzinfo=datetime.timezone.utc),
                  'duration': datetime.timedelta(seconds=7200),
                  'report_descriptions': [{'market_context': 'http://MarketContext1',
                                           'measurement': {'description': 'RealEnergy',
                                                           'name': 'energyReal',
                                                           'scale': 'n',
                                                           'unit': 'Wh'},
                                           'r_id': 'resource1_energy',
                                           'reading_type': 'Direct Read',
                                           'report_data_source': {'resource_id': 'resource1'},
                                           'report_type': 'usage',
                                           'sampling_rate': {'max_period': datetime.timedelta(seconds=60),
                                                             'min_period': datetime.timedelta(seconds=60),
                                                             'on_change': False}},
                                          {'market_context': 'http://MarketContext1',
                                           'measurement': {'description': 'RealPower',
                                                           'name': 'powerReal',
                                                           'power_attributes': {'ac': True,
                                                                                'hertz': 50,
                                                                                'voltage': 230},
                                                           'scale': 'n',
                                                           'unit': 'W'},
                                           'r_id': 'resource1_power',
                                           'reading_type': 'Direct Read',
                                           'report_data_source': {'resource_id': 'resource1'},
                                           'report_type': 'usage',
                                           'sampling_rate': {'max_period': datetime.timedelta(seconds=60),
                                                             'min_period': datetime.timedelta(seconds=60),
                                                             'on_change': False}}],
                  'report_id': '584d3b60-a8c6-4967-9f32-599a615a57c6',
                  'report_name': 'METADATA_TELEMETRY_USAGE',
                  'report_request_id': '538cf64f-901f-4bdf-ac7c-f5f72d4b4682',
                  'report_specifier_id': '789ed6cd4e_telemetry_usage'},
                 {'created_date_time': datetime.datetime(2019, 11, 20, 15, 4, 52, 638621, tzinfo=datetime.timezone.utc),
                  'duration': datetime.timedelta(seconds=7200),
                  'report_descriptions': [{'market_context': 'http://MarketContext1',
                                           'measurement': {'description': 'RealEnergy',
                                                           'name': 'energyReal',
                                                           'scale': 'n',
                                                           'unit': 'Wh'},
                                           'r_id': 'resource1_energy',
                                           'reading_type': 'Direct Read',
                                           'report_data_source': {'resource_id': 'resource1'},
                                           'report_type': 'usage',
                                           'sampling_rate': {'max_period': datetime.timedelta(seconds=60),
                                                             'min_period': datetime.timedelta(seconds=60),
                                                             'on_change': False}},
                                          {'market_context': 'http://MarketContext1',
                                           'measurement': {'description': 'RealPower',
                                                           'name': 'powerReal',
                                                           'power_attributes': {'ac': True,
                                                                                'hertz': 50,
                                                                                'voltage': 230},
                                                           'scale': 'n',
                                                           'unit': 'W'},
                                           'r_id': 'resource1_power',
                                           'reading_type': 'Direct Read',
                                           'report_data_source': {'resource_id': 'resource1'},
                                           'report_type': 'usage',
                                           'sampling_rate': {'max_period': datetime.timedelta(seconds=60),
                                                             'min_period': datetime.timedelta(seconds=60),
                                                             'on_change': False}}],
                  'report_id': '41907ef1-2f5b-45aa-b5fb-171098145438',
                  'report_name': 'METADATA_HISTORY_USAGE',
                  'report_request_id': '2244c5fd-44e2-4354-8aa0-97618cb1aa3a',
                  'report_specifier_id': '789ed6cd4e_history_usage'}],
     'request_id': '8a4f859883',
     'ven_id': 's3cc244ee6'}


.. _oadrResponse:

oadrResponse
============

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrResponse xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">c798c95c-08ee-4aab-bbb6-f37709ac0dbe</requestID>
          </ei:eiResponse>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrResponse>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'response': {'request_id': 'c798c95c-08ee-4aab-bbb6-f37709ac0dbe',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrResponse:

oadrResponse
============

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrResponse xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads"/>
          </ei:eiResponse>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrResponse>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'response': {'request_id': None,
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrUpdatedReport:

oadrUpdatedReport
=================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" oadr:Id="oadrSignedObject">
        <oadr:oadrUpdatedReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" xmlns:pyld="http://docs.oasis-open.org/ns/energyinterop/201110/payloads" ei:schemaVersion="2.0b">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <pyld:requestID>16f0ba0e-6962-48dc-8d7d-66a126d46760</pyld:requestID>
          </ei:eiResponse>
          <oadr:oadrCancelReport>
            <pyld:requestID>5328e42f-ae89-43fe-968a-3918997ed21c</pyld:requestID>
            <ei:reportRequestID>b41c5e66-907e-4f21-a023-480d1ce0f08a</ei:reportRequestID>
            <ei:reportRequestID>5862716f-87a4-4cd8-9bdd-3a036171c73c</ei:reportRequestID>
            <ei:reportRequestID>a631252e-5c6e-4c79-9485-c45f2dc86b5a</ei:reportRequestID>
            <pyld:reportToFollow>false</pyld:reportToFollow>
            <ei:venID>123ABC</ei:venID>
          </oadr:oadrCancelReport>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrUpdatedReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'cancel_report': {'report_request_id': ['b41c5e66-907e-4f21-a023-480d1ce0f08a',
                                             '5862716f-87a4-4cd8-9bdd-3a036171c73c',
                                             'a631252e-5c6e-4c79-9485-c45f2dc86b5a'],
                       'report_to_follow': False,
                       'request_id': '5328e42f-ae89-43fe-968a-3918997ed21c',
                       'ven_id': '123ABC'},
     'response': {'request_id': '16f0ba0e-6962-48dc-8d7d-66a126d46760',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


.. _oadrUpdateReport:

oadrUpdateReport
================

OpenADR payload:

.. code-block:: xml

    <oadr:oadrPayload xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07">
      <oadr:oadrSignedObject xmlns:oadr="http://openadr.org/oadr-2.0b/2012/07" xmlns:pyld="http://docs.oasis-open.org/ns/energyinterop/201110/payloads" xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06" oadr:Id="oadrSignedObject">
        <oadr:oadrUpdateReport xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" ei:schemaVersion="2.0b">
          <pyld:requestID>4875efec-522c-4990-9455-0d829a9032d8</pyld:requestID>
          <oadr:oadrReport xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0">
            <ei:eiReportID>f2b55629-fa99-4e48-903b-c2f4e1f9b589</ei:eiReportID>
            <oadr:oadrReportDescription xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
              <ei:rID>297b0a89-a674-4e6a-8543-2f50c91ffea9</ei:rID>
              <ei:reportSubject>
                <ei:resourceID>123ABC</ei:resourceID>
              </ei:reportSubject>
              <ei:reportDataSource>
                <ei:resourceID>123ABC</ei:resourceID>
              </ei:reportDataSource>
              <ei:reportType>availableEnergyStorage</ei:reportType>
              <ei:readingType>Allocated</ei:readingType>
              <emix:marketContext>http://localhost</emix:marketContext>
              <oadr:oadrSamplingRate>
                <oadr:oadrMinPeriod>PT1M</oadr:oadrMinPeriod>
                <oadr:oadrMaxPeriod>PT2M</oadr:oadrMaxPeriod>
                <oadr:oadrOnChange>false</oadr:oadrOnChange>
              </oadr:oadrSamplingRate>
            </oadr:oadrReportDescription>
            <ei:reportRequestID>253918be-08cf-4888-9c0b-d49a96136e54</ei:reportRequestID>
            <ei:reportSpecifierID>74ab5dae-95b9-4ba5-a68f-6e789ca41769</ei:reportSpecifierID>
            <ei:reportName>HISTORY_GREENBUTTON</ei:reportName>
            <ei:createdDateTime>2020-12-03T14:22:07.607232Z</ei:createdDateTime>
          </oadr:oadrReport>
          <ei:venID>123ABC</ei:venID>
        </oadr:oadrUpdateReport>
      </oadr:oadrSignedObject>
    </oadr:oadrPayload>

OpenLEADR representation:

.. code-block:: python3

    {'reports': [{'created_date_time': datetime.datetime(2020, 12, 3, 14, 22, 7, 607232, tzinfo=datetime.timezone.utc),
                  'report_descriptions': [{'market_context': 'http://localhost',
                                           'r_id': '297b0a89-a674-4e6a-8543-2f50c91ffea9',
                                           'reading_type': 'Allocated',
                                           'report_data_source': {'resource_id': '123ABC'},
                                           'report_subject': {'resource_id': '123ABC'},
                                           'report_type': 'availableEnergyStorage',
                                           'sampling_rate': {'max_period': datetime.timedelta(seconds=120),
                                                             'min_period': datetime.timedelta(seconds=60),
                                                             'on_change': False}}],
                  'report_id': 'f2b55629-fa99-4e48-903b-c2f4e1f9b589',
                  'report_name': 'HISTORY_GREENBUTTON',
                  'report_request_id': '253918be-08cf-4888-9c0b-d49a96136e54',
                  'report_specifier_id': '74ab5dae-95b9-4ba5-a68f-6e789ca41769'}],
     'request_id': '4875efec-522c-4990-9455-0d829a9032d8',
     'ven_id': '123ABC'}
