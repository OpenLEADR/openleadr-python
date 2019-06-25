# PyOpenADR

PyOpenADR is a Python 3 module that provides a convenient interface to OpenADR
systems. It contains an OpenADR Client that you can use to talk to other OpenADR
systems, and it contains an OpenADR Server (VTN) with convenient integration
possibilities.

It's easy to hook up your own pieces of functionality while having as little to do with the OpenADR protocol and intricacies as possible. If you want, everything can be coroutine and event-based, and your coroutines will be called whenever something of interest happens.

If you want to get up to speed on how the basic OpenADR communication flows happen, please read the [OpenADR Basics](#openadr-basics) section.

## Client (VEN)

You can use the OpenADR Client (Virtual End Node) to talk to OpenADR Virtual Top Nodes.

### Manual Mode

If you want to use the client in manual mode, you can instantiate the OpenADRClient with just a `ven_name` and a `vtn_url`, and then call the `create_party_registration()` once, and the `poll()` method repeatedly. The OpenADR client will keep track of the VTN-assigned `ven_id` and `registration_id`. The former is used for many messages, the latter is used if you wish to 'unregister' from the VTN.

The `poll()` method will return a tuple of (message type, message payload) for you to interpret. The message payload is a dict that contains native Python types as much as possible.

### Auto Mode

The client can handle the automatic polling and call your own functions or coroutines whenever there is an event or report that your application needs to see or needs to respond to. If you want to use automatic polling, set `auto_polling` = `True`, and also implement the `on_event` and `on_report` handlers. All handlers can be implemented as regular methods or coroutines; the coroutines having the advantage of not blocking the rest of the client (polling for example).

### Handling events

To link your own event handler, populate the `on_event` method in the OpenADRClient. This method or coroutine will be once for each event that comes in, event if these events are supplied in a single message from the VTN. You can decide what your response to each event is, by supplying the contents of the `oadrCreatedEvent` message. Mostly, you will want to either Opt In or Opt Out of the event by returning the strings `"optIn"` or `"optOut"`. The client will perform the neccessary requests to the VTN.

### Handling reports

To link your own report handler, implement the `on_report` method in the OpenADRClient. Your method or coroutine is called once for each report, supplying the contents of the report to your function.

### Supplying reports

If you want to supply reports to the VTN on an automated basis, implement the `next_report` method in the OpenADRClient. Your method or coroutine should supply the contents of the `oadrCreateReport` message.



## Server (VTN)

The Virtual Top Node is the "server" that the VENs connect to. The pyopenadr server implements most of the behavior, but you have to connect it to the backend that provides the data.

## Connecting to your data sources


### Responding to queries

*Methods dealing with events*

* `on_created_event(payload)` method is called whenever the VEN sends an `oadrCreatedEvent` message, probably informing you of what they intend to do with the event you gave them.
* `on_request_event(ven_id)`: this should return the next event (if any) that you have for the VEN. If you return `None`, a blank `oadrResponse` will be returned to the VEN.
* `on_request_report(ven_id)`: this should return then next report (if any) that you have for the VEN. If you return None, a blank oadrResponse will be returned to the VEN.
* `on_poll(ven_id)`: this should return the next message in line, which is usually either a new `oadrReport` or a `oadrDistributeEvent` message.

*Methods dealing with reports*

Please read the [OpenADR Basics: reporting](#reporting) section if you are unsure of the correct message flow involved in OpenADR Reporting.

* `on_create_report(payload)` method is called whenever the VEN sends an `oadrCreateReport` message, requesting you to periodically generate reports for the VEN.
* `on_register_report(payload)` method is called whenever the VEN sends an `oadrRegisterReport` message, probably to register their reporting capabilities with you.
* `on_update_report(payload)` method is called whenever the VEN sends an `oadrUpdateReport`, probably including an actual report from the VEN.

* `on_registered_report(payload)` method is called whenever the VEN confirms your communication of reporting capabilities.
* `on_created_report(payload)` method is called whenever the VEN sends an `oadrCreatedReport` message, probably informing you that they will be preparing periodic reports for you.

You have to supply your own classes for these. Each of the backends will be explained below.

### Getting meta-information on connected VENs

The Server can also call methods or coroutines if a VEN comes online, or when they go offline (having missed three polling intervals, which is configurable):

* `on_ven_online(ven_id)`
* `on_ven_offline(ven_id)`

## OpenADR Basics

OpenADR revolves around the VEN polling for messages from the VTN.

### Registration



### Reporting

Reporting is probably the most complicated of interactions within OpenADR. It involves the following steps:

1. Party A makes its reporting capabilities known to party B using a `oadrRegisterReport` message.
2. Party B responds with an `oadrRegisteredReport` message, optionally including an `oadrReportRequest` section that tells party A which party B is interested in.
3. Party A reponds with an `oadrCreatedReport` message telling party B that it will periodically generate the reports.

This ceremony is performed once with the VTN as party A and once with the VEN as party A.

The VEN party can collect the reports it requested from the VTN using either the `oadrPoll` or `oadrRequestReport` mechanisms. The VTN will respond with an `oadrUpdateReport` message containing the actual report. The VEN should then respond with a `oadrUpdatedReport` message.

The VEN should actively supply the reports to the VTN using `oadrUpdateReport` messages, to which the VTN will respond with `oadrUpdatedReport` messages.

### Events

OpenADR has a pretty flexible event modeling, which can nessecarily make things quite complex. The mechanism is pretty simple, and follows the following logic:

1. The VEN asks the VTN if there are any Events for the VEN. This can be done using the `oadrRequestEvent` or `oadrPoll` methods.
2. The VTN will supply an Event to the VEN using an `oadrDistributeEvent` message.
3. The VEN can decide whether to 'opt in' or 'opt out' of the event, which is included in the `oadrCreatedEvent` message.

An OpenADR Event is built up of the following properties (more or less):

* A specification of when this EVent is active, and what tolerances around the activation of the event are permissible (ActivePeriod)
* A list of Targets to which the event applies. THis can be VENs, groups, assets, geographic areas, and more.
* A list of Signals that have a name, a type and multiple Intervals that contain start dates and some payload value.




### Polling
