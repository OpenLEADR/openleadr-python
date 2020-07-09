.. _representations:

=======================
Payload Representations
=======================

In PyOpenADR, the complex hierarchies of the OpenADR XML-payloads are represented as Python dictionaries. These have been simplified as much as possible, allowing for a more natural and more readable experience.

The following general principles have been applied to representing OpenADR objects in PyOpenADR:

- All property names are represented in snake_case instead of CamelCase or mixedCase names. For example: ``requestID`` becomes ``request_id``.
- For all properties, the ``oadr*`` and ``Ei*`` prefixes have been stripped away. For example: ``eiResponse`` becomes ``response`` and ``oadrResponse`` becomes ``response``.
- OpenADR timestamps are converted to Python ``datetime.datetime`` objects.
- OpenADR time intervals are converted to Python ``datetime.timedelta`` objects.


oadrCanceledOpt
===============

OpenADR payload:


.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCanceledOpt ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">f48e3b7e78</requestID>
          </ei:eiResponse>
          <ei:optID>pc1e8ace47</ei:optID>
        </oadrCanceledOpt>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'opt_id': 'pc1e8ace47',
     'response': {'request_id': 'f48e3b7e78',
                  'response_code': 200,
                  'response_description': 'OK'}}


oadrCanceledPartyRegistration
=============================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCanceledPartyRegistration ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">aba0a805de</requestID>
          </ei:eiResponse>
          <ei:registrationID>zf68abb5c2</ei:registrationID>
          <ei:venID>123ABC</ei:venID>
        </oadrCanceledPartyRegistration>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'registration_id': 'zf68abb5c2',
     'response': {'request_id': 'aba0a805de',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


oadrCanceledReport
==================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCanceledReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">e4dfe735ea</requestID>
          </ei:eiResponse>
          <oadrPendingReports>
            <ei:reportRequestID>v5d42c35e6</ei:reportRequestID>
            <ei:reportRequestID>e8bf753e31</ei:reportRequestID>
          </oadrPendingReports>
        </oadrCanceledReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': 'v5d42c35e6'},
                         {'request_id': 'e8bf753e31'}],
     'response': {'request_id': 'e4dfe735ea',
                  'response_code': 200,
                  'response_description': 'OK'}}

oadrCanceledReport
==================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCanceledReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">c36bce5dcb</requestID>
          </ei:eiResponse>
          <oadrPendingReports>
            <ei:reportRequestID>b04cbfb723</ei:reportRequestID>
            <ei:reportRequestID>ra6231a650</ei:reportRequestID>
          </oadrPendingReports>
          <ei:venID>123ABC</ei:venID>
        </oadrCanceledReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': 'b04cbfb723'},
                         {'request_id': 'ra6231a650'}],
     'response': {'request_id': 'c36bce5dcb',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


oadrCancelOpt
=============

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCancelOpt ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">u07a26b1cc</requestID>
          <ei:optID>b1ef7afecc</ei:optID>
          <ei:venID>123ABC</ei:venID>
        </oadrCancelOpt>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'opt_id': 'b1ef7afecc', 'request_id': 'u07a26b1cc', 'ven_id': '123ABC'}


oadrCancelPartyRegistration
===========================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCancelPartyRegistration ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">z05e4ff0aa</requestID>
          <ei:registrationID>pfe04d8439</ei:registrationID>
          <ei:venID>123ABC</ei:venID>
        </oadrCancelPartyRegistration>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'registration_id': 'pfe04d8439',
     'request_id': 'z05e4ff0aa',
     'ven_id': '123ABC'}


oadrCancelReport
================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCancelReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">kcb7b5cf7a</requestID>
          <ei:reportRequestID>u1ebe92deb</ei:reportRequestID>
          <reportToFollow xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">true</reportToFollow>
          <ei:venID>123ABC</ei:venID>
        </oadrCancelReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'report_request_id': 'u1ebe92deb',
     'report_to_follow': True,
     'request_id': 'kcb7b5cf7a',
     'ven_id': '123ABC'}


oadrCreatedEvent
================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCreatedEvent ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <eiCreatedEvent xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">
            <ei:eiResponse>
              <ei:responseCode>200</ei:responseCode>
              <ei:responseDescription>OK</ei:responseDescription>
              <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">yaa3ee03b1</requestID>
            </ei:eiResponse>
            <ei:eventResponses>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">ycab9acb9f</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>od864b4ea6</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">bf2aad9af8</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>hc6cf67dab</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">jefb88dcbd</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>qdff0da955</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
            </ei:eventResponses>
            <ei:venID>123ABC</ei:venID>
          </eiCreatedEvent>
        </oadrCreatedEvent>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'event_responses': [{'event_id': 'od864b4ea6',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'ycab9acb9f',
                          'response_code': 200,
                          'response_description': 'OK'},
                         {'event_id': 'hc6cf67dab',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'bf2aad9af8',
                          'response_code': 200,
                          'response_description': 'OK'},
                         {'event_id': 'qdff0da955',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'jefb88dcbd',
                          'response_code': 200,
                          'response_description': 'OK'}],
     'response': {'request_id': 'yaa3ee03b1',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


oadrCreatedReport
=================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCreatedReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">ie8ff94fbc</requestID>
          </ei:eiResponse>
          <oadrPendingReports>
            <ei:reportRequestID>p8c56f9ed9</ei:reportRequestID>
            <ei:reportRequestID>hab1cced95</ei:reportRequestID>
          </oadrPendingReports>
          <ei:venID>123ABC</ei:venID>
        </oadrCreatedReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': 'p8c56f9ed9'},
                         {'request_id': 'hab1cced95'}],
     'response': {'request_id': 'ie8ff94fbc',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


oadrCreatedEvent
================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCreatedEvent ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <eiCreatedEvent xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">
            <ei:eiResponse>
              <ei:responseCode>200</ei:responseCode>
              <ei:responseDescription>OK</ei:responseDescription>
              <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">yde9c0369d</requestID>
            </ei:eiResponse>
            <ei:eventResponses>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">zc9523b16d</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>fefaa2b0f2</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optIn</ei:optType>
              </ei:eventResponse>
              <ei:eventResponse>
                <ei:responseCode>200</ei:responseCode>
                <ei:responseDescription>OK</ei:responseDescription>
                <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">tbeecb7c97</requestID>
                <ei:qualifiedEventID>
                  <ei:eventID>t63a63fea4</ei:eventID>
                  <ei:modificationNumber>1</ei:modificationNumber>
                </ei:qualifiedEventID>
                <ei:optType>optOut</ei:optType>
              </ei:eventResponse>
            </ei:eventResponses>
            <ei:venID>123ABC</ei:venID>
          </eiCreatedEvent>
        </oadrCreatedEvent>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'event_responses': [{'event_id': 'fefaa2b0f2',
                          'modification_number': 1,
                          'opt_type': 'optIn',
                          'request_id': 'zc9523b16d',
                          'response_code': 200,
                          'response_description': 'OK'},
                         {'event_id': 't63a63fea4',
                          'modification_number': 1,
                          'opt_type': 'optOut',
                          'request_id': 'tbeecb7c97',
                          'response_code': 200,
                          'response_description': 'OK'}],
     'response': {'request_id': 'yde9c0369d',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


oadrCreatedPartyRegistration
============================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCreatedPartyRegistration ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">k6565d9280</requestID>
          </ei:eiResponse>
          <ei:registrationID>o852fdbac9</ei:registrationID>
          <ei:venID>123ABC</ei:venID>
          <ei:vtnID>VTN123</ei:vtnID>
          <oadrProfiles>
            <oadrProfile>
              <oadrProfileName>2.0b</oadrProfileName>
              <oadrTransports>
                <oadrTransport>
                  <oadrTransportName>simpleHttp</oadrTransportName>
                </oadrTransport>
              </oadrTransports>
            </oadrProfile>
          </oadrProfiles>
        </oadrCreatedPartyRegistration>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'profiles': [{'profile_name': '2.0b',
                   'transports': [{'transport_name': 'simpleHttp'}]}],
     'registration_id': 'o852fdbac9',
     'response': {'request_id': 'k6565d9280',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC',
     'vtn_id': 'VTN123'}


oadrCreatedReport
=================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCreatedReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">gde557fcae</requestID>
          </ei:eiResponse>
          <oadrPendingReports>
            <ei:reportRequestID>e1e16137f3</ei:reportRequestID>
            <ei:reportRequestID>d0f2bcbe89</ei:reportRequestID>
          </oadrPendingReports>
        </oadrCreatedReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'pending_reports': [{'request_id': 'e1e16137f3'},
                         {'request_id': 'd0f2bcbe89'}],
     'response': {'request_id': 'gde557fcae',
                  'response_code': 200,
                  'response_description': 'OK'}}


oadrCreateOpt
=============

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrCreateOpt ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110" xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0" xmlns:emix="http://docs.oasis-open.org/ns/emix/2011/06">
          <ei:optID>l170fb7ea4</ei:optID>
          <ei:optType>optIn</ei:optType>
          <ei:optReason>participating</ei:optReason>
          <ei:venID>VEN123</ei:venID>
          <ei:createdDateTime>2020-07-09T15:54:03.151236Z </ei:createdDateTime>
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">k6dc07ece8</requestID>
          <ei:qualifiedEventID>
            <ei:eventID>sdfe18dd5c</ei:eventID>
            <ei:modificationNumber>1</ei:modificationNumber>
          </ei:qualifiedEventID>
          <ei:eiTarget>
            <ei:venID>123ABC</ei:venID>
          </ei:eiTarget>
        </oadrCreateOpt>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'created_date_time': datetime.datetime(2020, 7, 9, 15, 54, 3, 151236, tzinfo=datetime.timezone.utc),
     'event_id': 'sdfe18dd5c',
     'modification_number': 1,
     'opt_id': 'l170fb7ea4',
     'opt_reason': 'participating',
     'opt_type': 'optIn',
     'request_id': 'k6dc07ece8',
     'targets': [{'ven_id': '123ABC'}],
     'ven_id': 'VEN123'}


oadrCreatePartyRegistration
===========================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07">
      <oadrSignedObject>
        <oadrCreatePartyRegistration ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">g31f3a2aae</requestID>
          <ei:venID>123ABC</ei:venID>
          <oadrProfileName>2.0b</oadrProfileName>
          <oadrTransportName>simpleHttp</oadrTransportName>
          <oadrTransportAddress>http://localhost</oadrTransportAddress>
          <oadrReportOnly>false</oadrReportOnly>
          <oadrXmlSignature>false</oadrXmlSignature>
          <oadrVenName>test</oadrVenName>
          <oadrHttpPullModel>true</oadrHttpPullModel>
        </oadrCreatePartyRegistration>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'http_pull_model': True,
     'profile_name': '2.0b',
     'report_only': False,
     'request_id': 'g31f3a2aae',
     'transport_address': 'http://localhost',
     'transport_name': 'simpleHttp',
     'ven_id': '123ABC',
     'ven_name': 'test',
     'xml_signature': False}


oadrCreateReport
================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07">
      <oadrSignedObject>
        <oadrCreateReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">sdbbdefaad</requestID>
          <oadrReportRequest>
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
                  <xcal:tolerance>
                    <xcal:tolerate>
                      <xcal:startafter>PT5M</xcal:startafter>
                    </xcal:tolerate>
                  </xcal:tolerance>
                </xcal:properties>
              </ei:reportInterval>
              <ei:specifierPayload>
                <ei:rID>d6e2e07485</ei:rID>
                <ei:readingType>Direct Read</ei:readingType>
              </ei:specifierPayload>
            </ei:reportSpecifier>
          </oadrReportRequest>
          <ei:venID>123ABC</ei:venID>
        </oadrCreateReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'report_requests': [{'report_request_id': 'd2b7bade5f',
                          'report_specifier': {'granularity': datetime.timedelta(seconds=900),
                                               'report_back_duration': datetime.timedelta(seconds=900),
                                               'report_interval': {'dtstart': datetime.datetime(2019, 11, 19, 11, 0, 18, 672768, tzinfo=datetime.timezone.utc),
                                                                   'duration': datetime.timedelta(seconds=7200),
                                                                   'tolerance': {'tolerate': {'startafter': datetime.timedelta(seconds=300)}}},
                                               'report_specifier_id': '9c8bdc00e7',
                                               'specifier_payload': {'r_id': 'd6e2e07485',
                                                                     'reading_type': 'Direct '
                                                                                     'Read'}}}],
     'request_id': 'sdbbdefaad',
     'ven_id': '123ABC'}


oadrDistributeEvent
===================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrDistributeEvent ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">123</requestID>
          </ei:eiResponse>
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">i5fea744ae</requestID>
          <ei:vtnID>VTN123</ei:vtnID>
          <oadrEvent>
            <ei:eiEvent>
              <ei:eventDescriptor>
                <ei:eventID>ifdda7aff6</ei:eventID>
                <ei:modificationNumber>1</ei:modificationNumber>
                <ei:modificationDateTime>2020-07-09T15:54:03.166717Z</ei:modificationDateTime>
                <ei:priority>1</ei:priority>
                <ei:eiMarketContext>
                  <marketContext xmlns="http://docs.oasis-open.org/ns/emix/2011/06">http://MarketContext1</marketContext>
                </ei:eiMarketContext>
                <ei:createdDateTime>2020-07-09T15:54:03.166717Z</ei:createdDateTime>
                <ei:eventStatus>near</ei:eventStatus>
                <ei:testEvent>false</ei:testEvent>
                <ei:vtnComment>This is an event</ei:vtnComment>
              </ei:eventDescriptor>
              <ei:eiActivePeriod>
                <properties xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                  <dtstart>
                    <date-time>2020-07-09T15:55:03.166717Z</date-time>
                  </dtstart>
                  <duration>
                    <duration>PT10M</duration>
                  </duration>
                </properties>
                <components xsi:nil="true" xmlns="urn:ietf:params:xml:ns:icalendar-2.0" />
              </ei:eiActivePeriod>
              <ei:eiEventSignals>
                <ei:eiEventSignal>
                  <intervals xmlns="urn:ietf:params:xml:ns:icalendar-2.0:stream">
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>1</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>8</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>2</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>10</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>3</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>12</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>4</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>14</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>5</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>16</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>6</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>18</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>7</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>20</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>8</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>10</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                    <ei:interval>
                      <duration xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <duration>PT1M</duration>
                      </duration>
                      <uid xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
                        <text>9</text>
                      </uid>
                      <ei:signalPayload>
                        <ei:payloadFloat>
                          <ei:value>20</ei:value>
                        </ei:payloadFloat>
                      </ei:signalPayload>
                    </ei:interval>
                  </intervals>
                  <ei:signalName>LOAD_CONTROL</ei:signalName>
                  <ei:signalType>x-loadControlCapacity</ei:signalType>
                  <ei:signalID>zccf1b86ee</ei:signalID>
                  <ei:currentValue>
                    <ei:payloadFloat>
                      <ei:value>9.99</ei:value>
                    </ei:payloadFloat>
                  </ei:currentValue>
                </ei:eiEventSignal>
              </ei:eiEventSignals>
              <ei:eiTarget>
                <ei:venID>VEN001</ei:venID>
                <ei:venID>VEN002</ei:venID>
              </ei:eiTarget>
            </ei:eiEvent>
            <oadrResponseRequired>always</oadrResponseRequired>
          </oadrEvent>
        </oadrDistributeEvent>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'events': [{'active_period': {'dtstart': datetime.datetime(2020, 7, 9, 15, 55, 3, 166717, tzinfo=datetime.timezone.utc),
                                   'duration': datetime.timedelta(seconds=600)},
                 'event_descriptor': {'created_date_time': datetime.datetime(2020, 7, 9, 15, 54, 3, 166717, tzinfo=datetime.timezone.utc),
                                      'event_id': 'ifdda7aff6',
                                      'event_status': 'near',
                                      'market_context': 'http://MarketContext1',
                                      'modification_date_time': datetime.datetime(2020, 7, 9, 15, 54, 3, 166717, tzinfo=datetime.timezone.utc),
                                      'modification_number': 1,
                                      'priority': 1,
                                      'test_event': 'false',
                                      'vtn_comment': 'This is an event'},
                 'event_signals': [{'current_value': 9.99,
                                    'intervals': [{'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 8,
                                                   'uid': 1},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 10,
                                                   'uid': 2},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 12,
                                                   'uid': 3},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 14,
                                                   'uid': 4},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 16,
                                                   'uid': 5},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 18,
                                                   'uid': 6},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 20,
                                                   'uid': 7},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 10,
                                                   'uid': 8},
                                                  {'duration': datetime.timedelta(seconds=60),
                                                   'signal_payload': 20,
                                                   'uid': 9}],
                                    'signal_id': 'zccf1b86ee',
                                    'signal_name': 'LOAD_CONTROL',
                                    'signal_type': 'x-loadControlCapacity'}],
                 'response_required': 'always',
                 'targets': [{'ven_id': 'VEN001'}, {'ven_id': 'VEN002'}]}],
     'request_id': 'i5fea744ae',
     'response': {'request_id': 123,
                  'response_code': 200,
                  'response_description': 'OK'},
     'vtn_id': 'VTN123'}


oadrPoll
========

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07">
      <oadrSignedObject>
        <oadrPoll ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:venID>123ABC</ei:venID>
        </oadrPoll>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'ven_id': '123ABC'}

oadrQueryRegistration
=====================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrQueryRegistration ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">i8cf15d21f</requestID>
        </oadrQueryRegistration>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'request_id': 'i8cf15d21f'}

oadrRegisteredReport
====================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07">
      <oadrSignedObject>
        <oadrRegisteredReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">uadb7d5fe5</requestID>
          </ei:eiResponse>
          <oadrReportRequest>
            <ei:reportRequestID>f5308f6138</ei:reportRequestID>
            <ei:reportSpecifier xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0">
              <ei:reportSpecifierID>se40c348d9</ei:reportSpecifierID>
              <xcal:granularity>
                <xcal:duration>PT15M</xcal:duration>
              </xcal:granularity>
              <ei:reportBackDuration>
                <xcal:duration>PT15M</xcal:duration>
              </ei:reportBackDuration>
              <ei:reportInterval>
                <xcal:properties>
                  <xcal:dtstart>
                    <xcal:date-time>2020-07-09T15:54:03.184498Z</xcal:date-time>
                  </xcal:dtstart>
                  <xcal:duration>
                    <xcal:duration>PT2H</xcal:duration>
                  </xcal:duration>
                  <xcal:tolerance>
                    <xcal:tolerate>
                      <xcal:startafter>PT5M</xcal:startafter>
                    </xcal:tolerate>
                  </xcal:tolerance>
                  <ei:x-eiNotification>
                    <xcal:duration>PT30M</xcal:duration>
                  </ei:x-eiNotification>
                  <ei:x-eiRampUp>
                    <xcal:duration>PT15M</xcal:duration>
                  </ei:x-eiRampUp>
                  <ei:x-eiRecovery>
                    <xcal:duration>PT5M</xcal:duration>
                  </ei:x-eiRecovery>
                </xcal:properties>
              </ei:reportInterval>
              <ei:specifierPayload>
                <ei:rID>u461c6e37e</ei:rID>
                <ei:readingType>Direct Read</ei:readingType>
              </ei:specifierPayload>
            </ei:reportSpecifier>
          </oadrReportRequest>
          <oadrReportRequest>
            <ei:reportRequestID>tc88cf616d</ei:reportRequestID>
            <ei:reportSpecifier xmlns:xcal="urn:ietf:params:xml:ns:icalendar-2.0">
              <ei:reportSpecifierID>le65d1bd2e</ei:reportSpecifierID>
              <xcal:granularity>
                <xcal:duration>PT15M</xcal:duration>
              </xcal:granularity>
              <ei:reportBackDuration>
                <xcal:duration>PT15M</xcal:duration>
              </ei:reportBackDuration>
              <ei:reportInterval>
                <xcal:properties>
                  <xcal:dtstart>
                    <xcal:date-time>2020-07-09T15:54:03.184526Z</xcal:date-time>
                  </xcal:dtstart>
                  <xcal:duration>
                    <xcal:duration>PT2H</xcal:duration>
                  </xcal:duration>
                  <xcal:tolerance>
                    <xcal:tolerate>
                      <xcal:startafter>PT5M</xcal:startafter>
                    </xcal:tolerate>
                  </xcal:tolerance>
                  <ei:x-eiNotification>
                    <xcal:duration>PT30M</xcal:duration>
                  </ei:x-eiNotification>
                  <ei:x-eiRampUp>
                    <xcal:duration>PT15M</xcal:duration>
                  </ei:x-eiRampUp>
                  <ei:x-eiRecovery>
                    <xcal:duration>PT5M</xcal:duration>
                  </ei:x-eiRecovery>
                </xcal:properties>
              </ei:reportInterval>
              <ei:specifierPayload>
                <ei:rID>caaff64e5a</ei:rID>
                <ei:readingType>Direct Read</ei:readingType>
              </ei:specifierPayload>
            </ei:reportSpecifier>
          </oadrReportRequest>
          <ei:venID>VEN123</ei:venID>
        </oadrRegisteredReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'report_requests': [{'report_request_id': 'f5308f6138',
                          'report_specifier': {'granularity': datetime.timedelta(seconds=900),
                                               'report_back_duration': datetime.timedelta(seconds=900),
                                               'report_interval': {'dtstart': datetime.datetime(2020, 7, 9, 15, 54, 3, 184498, tzinfo=datetime.timezone.utc),
                                                                   'duration': datetime.timedelta(seconds=7200),
                                                                   'notification': datetime.timedelta(seconds=1800),
                                                                   'ramp_up': datetime.timedelta(seconds=900),
                                                                   'recovery': datetime.timedelta(seconds=300),
                                                                   'tolerance': {'tolerate': {'startafter': datetime.timedelta(seconds=300)}}},
                                               'report_specifier_id': 'se40c348d9',
                                               'specifier_payload': {'r_id': 'u461c6e37e',
                                                                     'reading_type': 'Direct '
                                                                                     'Read'}}},
                         {'report_request_id': 'tc88cf616d',
                          'report_specifier': {'granularity': datetime.timedelta(seconds=900),
                                               'report_back_duration': datetime.timedelta(seconds=900),
                                               'report_interval': {'dtstart': datetime.datetime(2020, 7, 9, 15, 54, 3, 184526, tzinfo=datetime.timezone.utc),
                                                                   'duration': datetime.timedelta(seconds=7200),
                                                                   'notification': datetime.timedelta(seconds=1800),
                                                                   'ramp_up': datetime.timedelta(seconds=900),
                                                                   'recovery': datetime.timedelta(seconds=300),
                                                                   'tolerance': {'tolerate': {'startafter': datetime.timedelta(seconds=300)}}},
                                               'report_specifier_id': 'le65d1bd2e',
                                               'specifier_payload': {'r_id': 'caaff64e5a',
                                                                     'reading_type': 'Direct '
                                                                                     'Read'}}}],
     'response': {'request_id': 'uadb7d5fe5',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': 'VEN123'}


oadrRequestEvent
================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07">
      <oadrSignedObject>
        <oadrRequestEvent ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <eiRequestEvent xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">
            <requestID>oa1c52db3f</requestID>
            <ei:venID>123ABC</ei:venID>
          </eiRequestEvent>
        </oadrRequestEvent>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'request_id': 'oa1c52db3f', 'ven_id': '123ABC'}


oadrRequestReregistration
=========================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrRequestReregistration ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:venID>123ABC</ei:venID>
        </oadrRequestReregistration>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'ven_id': '123ABC'}


oadrResponse
============

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrResponse ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <requestID xmlns="http://docs.oasis-open.org/ns/energyinterop/201110/payloads">i4a4d03ae5</requestID>
          </ei:eiResponse>
          <ei:venID>123ABC</ei:venID>
        </oadrResponse>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'response': {'request_id': 'i4a4d03ae5',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


oadrResponse
============

OpenADR payload:

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
          <ei:venID>123ABC</ei:venID>
        </oadrResponse>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'response': {'request_id': None,
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}


oadrUpdatedReport
=================

OpenADR payload:

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <oadrPayload xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://openadr.org/oadr-2.0b/2012/07" xmlns:pyld="http://docs.oasis-open.org/ns/energyinterop/201110/payloads" xsi:schemaLocation="http://openadr.org/oadr-2.0b/2012/07 oadr_20b.xsd">
      <oadrSignedObject>
        <oadrUpdatedReport ei:schemaVersion="2.0b" xmlns:ei="http://docs.oasis-open.org/ns/energyinterop/201110">
          <ei:eiResponse>
            <ei:responseCode>200</ei:responseCode>
            <ei:responseDescription>OK</ei:responseDescription>
            <pyld:requestID>icaffaa44f</pyld:requestID>
          </ei:eiResponse>
          <oadrCancelReport>
            <pyld:requestID>ra11e4fee3</pyld:requestID>
            <ei:reportRequestID>kbf16facdd</ei:reportRequestID>
            <ei:reportRequestID>kfbae403c3</ei:reportRequestID>
            <ei:reportRequestID>k91557da99</ei:reportRequestID>
            <pyld:reportToFollow>false</pyld:reportToFollow>
            <ei:venID>123ABC</ei:venID>
          </oadrCancelReport>
          <ei:venID>123ABC</ei:venID>
        </oadrUpdatedReport>
      </oadrSignedObject>
    </oadrPayload>

pyOpenADR representation:

.. code-block:: python3

    {'cancel_report': {'report_request_id': ['kbf16facdd',
                                             'kfbae403c3',
                                             'k91557da99'],
                       'report_to_follow': False,
                       'request_id': 'ra11e4fee3',
                       'ven_id': '123ABC'},
     'response': {'request_id': 'icaffaa44f',
                  'response_code': 200,
                  'response_description': 'OK'},
     'ven_id': '123ABC'}
