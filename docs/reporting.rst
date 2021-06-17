.. _reporting:

=========
Reporting
=========

Your VEN can provide periodic reports to the VTN. These reports usually contain metering data or status information.

A brief overview of reports in OpenADR
--------------------------------------

Reports can describe many measurable things. A report description contains:

- A ReportName, of which the following are predefined in OpenADR:
   - ``TELEMETRY_USAGE``: for providing meter reading or other instantanious values
   - ``TELEMETRY_STATUS``: for providing real-time status updates of availability
   - ``HISTORY_USAGE``: for providing a historic metering series
   - ``HISTORY_GREENBUTTON``: for providing historic data according to the GreenButton format
- A ReportType, which indicates what the data represents. There are many options predefined, like ``READING``, ``USAGE``, ``DEMAND``, ``STORED_ENERGY``, et cetera. You can find all of them in the ``enums.REPORT_TYPE`` enumeration.
- A ReadingType, which indicates the way in which the data is collected or possibly downsampled. For instance, ``DIRECT_READ``, ``NET``, ``ALLOCATED``, ``SUMMED``, ``MEAN``, ``PEAK``, et cetera.
- A Sampling Rate, which defines the rate at which data can or should be collected. When configuring / offering reports from the VEN, you can set a minimum and maximum sampling rate if you wish, to let the VTN choose its preferred sampling rate.
- A so-called ItemBase, which indicates the quantity you are reporting, like Voltage, Current or Energy. In OpenLEADR, this is called ``measurement``.
- A unit of measure, usually linked to the ``measurement``, like ``A`` for ampere, or ``V`` for volt.
- A Resource ID, which indicates which of the resources this report applies to. It's probably one of your controllable devices.

You configure which reports you can deliver, and the VEN offers these to the VTN. The VTN makes a selection and requests reports from the VEN to be sent at regular intervals. The VEN then starts collecting data and sending reports.

Offering reports (VEN to VTN)
-----------------------------


Basic telemetry reports
~~~~~~~~~~~~~~~~~~~~~~~

Say you have two devices, 'Device001' and 'Device002', which can each offer measurments of Voltage and Current at a samplerate of 10 seconds. You would register these reports as follows:

.. code-block:: python3

    import openleadr
    from functools import partial

    async def main():
        client = openleadr.OpenADRClient()
        # Add reports
        client.add_report(callback=partial(read_current, device='Device001'),
                          report_specifier_id='AmpereReport',
                          resource_id='Device001',
                          measurement='Current',
                          sampling_rate=timedelta(seconds=10),
                          unit='A')
        client.add_report(callback=partial(read_current, device='Device002'),
                          report_specifier_id='AmpereReport',
                          resource_id='Device002',
                          measurement='Current',
                          sampling_rate=timedelta(seconds=10),
                          unit='A')
        client.add_report(callback=partial(read_voltage, device='Device001'),
                          report_specifier_id='VoltageReport',
                          resource_id='Device001',
                          measurement='Voltage',
                          sampling_rate=timedelta(seconds=10),
                          unit='V')
        client.add_report(callback=partial(read_voltage, device='Device002'),
                          report_specifier_id='VoltageReport',
                          resource_id='Device002',
                          measurement='Voltage',
                          sampling_rate=timedelta(seconds=10),
                          unit='V')
        await client.run()

    async def read_voltage(device):
        """
        Retrieve the voltage value from the given 'device'.
        """
        v = await interface.read(device, 'voltage') # Dummy code
        return v

    async def read_current(device):
        """
        Retrieve the current value from the given 'device'.
        """
        a = await interface.read(device, 'current') # Dummy code
        return a


The VTN can request TELEMETRY_USAGE reports to be delivered at the sampling rate, or it can request them at a lower rate. For instance, it can request 15-minute readings, delivered every 24 hours. By default, openLEADR handles this case by incrementally building up the report during the day, calling your callback every 15 minutes and sending the report once it has 24 hours worth of values.

If, instead, you already have a system where historic data can be extracted, and prefer to use that method instead, you can configure that as well.

The two requirements for this kind of data collection are:

1. Your callback must accept arguments named ``date_from``, ``date_to`` and ``sampling_interval``
2. You must specify ``data_collection_mode='full'`` when adding the report.

Here's an example:

.. code-block:: python3

    import openleadr

    async def main():
        client = openleadr.OpenADRClient(ven_name='myven', vtn_url='http://some-vtn.com')
        client.add_report(callback=load_data,
                          data_collection_mode='full',
                          report_specifier_id='AmpereReport',
                          resource_id='Device001',
                          measurement='current',
                          sampling_rate=timedelta(seconds=10),
                          unit='A')

    async def load_data(date_from, date_to, sampling_interval):
        """
        Function that loads data between date_from and date_to, sampled at sampling_interval.
        """
        # Load data from a backend system
        result = await database.get("""SELECT time_bucket('15 minutes', datetime) as dt, AVG(value)
                                         FROM metervalues
                                        WHERE datetime BETWEEN %s AND %s
                                        GROUP BY dt
                                        ORDER BY dt""")
        # Pack the data into a list of (datetime, value) tuples
        data = result.fetchall()

        # data should look like:
        # [(datetime.datetime(2020, 1, 1, 12, 0, 0), 10.0),
        #  (datetime.datetime(2020, 1, 1, 12, 15, 0), 9.0),
        #  (datetime.datetime(2020, 1, 1, 12, 30, 0), 11.0),
        #  (datetime.datetime(2020, 1, 1, 12, 45, 0), 12.0)]
        return data


Historic data reports
~~~~~~~~~~~~~~~~~~~~~

.. note::
    Historic reports are not yet implemented into OpenLEADR. Please follow updates in `this issue on GitHub <https://github.com/OpenLEADR/openleadr-python/issues/18>`_.

You can also configure historic reports, where the VTN can at any time request data from a specified time interval and granularity. For historic reports, you must have your own data collection system and the provided callback must have the signature:

.. code-block:: python3

    async def get_historic_data(date_from, date_to, sampling_interval)


An example for configuring historic reports:

.. code-block:: python3

    import openleadr
    from functools import partial

    async def main():
        client = openleadr.OpenADRClient(ven_name='myven', vtn_url='http://some-vtn.com')
        client.add_report(callback=partial(get_historic_data, device_id='Device001'),
                          report_name='HISTORY_USAGE',
                          report_specifier_id='AmpereHistory',
                          resource_id='Device001',
                          measurement='current'
                          sampling_rate=timedelta(seconds=10),
                          unit='A')

Note that you have to override the default ``report_name`` compared to the previous examples.


Requesting Reports (VTN to VEN)
-------------------------------

The VTN will receive an ``oadrRegisterReport`` message. Your handler ``on_register_report`` will be called for each report that is offered. You inspect the report description and decide which elements from the report you wish to receive.

Using the compact format
~~~~~~~~~~~~~~~~~~~~~~~~

The compact format provides an abstraction over the actual encapsulation of reports. If your ``on_register_report`` handler has the following signature, if will be called using the simple format:

.. code-block:: python3

    async def on_register_report(ven_id, resource_id, measurement, unit, scale,
                                 min_sampling_interval, max_sampling_interval):
        if want_report:
            return (callback, sampling_interval, report_interval)
        else:
            return None

The ``callback`` refers to a function or coroutine that will be called when data is received.
The ``sampling_interval`` is a ``timedelta`` object that contains the interval at which data is sampled by the client.
The ``report_interval`` is optional, and contains a ``timedelta`` object that indicates how often you want to receive a report. If you don't specify a ``report_interval``, you will receive each report immediately after it is sampled.

This mechanism allows you to specify, for instance, that you want to receive 15-minute sampled values every 24 hours.

For more information on the design of your callback function, see the :ref:`receiving_reports` section below.

Using the full format
~~~~~~~~~~~~~~~~~~~~~

If you want full control over the reporting specification, you implement an ``on_register_report`` handler with the following signature:

.. code-block:: python3

    async def on_register_report(report):
        # For each report description (identified by their r_id)
        # you want to received, return a callback and sampling rate

        return [(callback_1, r_id_1, sampling_rate_1),
                (callback_2, r_id_2, sampling_rate_2)]

The Report object that you have to inspect looks like this:

.. code-block:: python3

    {'report_specifier_id': 'AmpereHistory',
     'report_name': 'METADATA_TELEMETRY_USAGE',
     'report_descriptions': [

            {'r_id': 'abc346-de6255-2345',
             'report_type': 'READING',
             'reading_type': 'DIRECT_READ',
             'report_subject': {'resource_ids': ['Device001']},
             'report_data_source': {'resource_ids': ['Device001']},
             'sampling_rate': {'min_period': timedelta(seconds=10),
                               'max_period': timedelta(minutes=15),
                               'on_change': False},
             'measurement': {'item_name': 'current',
                             'item_description': 'Current',
                             'item_units': 'A',
                             'si_scale_code': None},

            {'r_id': 'd2e352-126ae2-1723',
             'report_type': 'READING',
             'reading_type': 'DIRECT_READ',
             'report_subject': {'resource_ids': ['Device002']},
             'report_data_source': {'resource_ids': ['Device002']},
             'sampling_rate': {'min_period': timedelta(seconds=10),
                               'max_period': timedelta(minutes=15),
                               'on_change': False},
             'measurement': {'item_name': 'current',
                             'item_description': 'Current',
                             'item_units': 'A',
                             'si_scale_code': None}

        ]
    }

.. note:: The ``report_name`` property of a report gets prefixed with ``METADATA_`` during the ``register_report`` step. This indicates that it is a report without any data. Once you get the actual reports, the ``METADATA_`` prefix will not be there.

Your handler should read this, and make the following choices:

- Which of these reports, specified by their ``r_id``, do I want?
- At which sampling rate? In other words: how often should the data be sampled from the device?
- At which reporting interval? In other words: how ofter should the collected data be packed up and sent to me?
- Which callback should be called when I receive a new report?

Your ``on_register_report`` handler thus looks something like this:

.. code-block:: python3

    import openleadr

    async def store_data(data):
        """
        Function that stores data from the report.
        """

    async def on_register_report(resource_id, measurement, unit, scale, min_sampling_period, max_sampling_period):
        """
        This is called for every measurement that the VEN is offering as a telemetry report.
        """
        if measurement == 'Voltage':
            return store_data, min_sampling_period

    async def main():
        server = openleadr.OpenADRServer(vtn_id='myvtn')
        server.add_handler('on_register_report', on_register_report)

Your ``store_data`` handler will be called with the contents of each report as it comes in.

You have two options for receiving the data:

1. Receive the entire oadrReport dict that contains the values as we receive it.
2. Receive only the r_id and an iterable of ``(datetime.datetime, value)`` tuples for you to deal with.


Delivering Reports (VEN to VTN)
-------------------------------

Report values will be automatically collected by running your provided callbacks. They are automatically packed up and sent to the VTN at the requested interval.

Your callbacks should return either a single value, representing the most up-to-date reading,
or a list of ``(datetime.datetime, value)`` tuples. This last type is useful when providing historic reports.

This was already described in the previous section on this page.


.. receiving_reports::

Receiving Reports (VTN)
-----------------------

When the VEN delivers a report that you asked for, your handlers will be called to deal with it.

Instead of giving you the full Report object, your handler will receive the iterable of ``(datetime.datetime, value)`` tuples.

If your callback needs to know other metadata properties at runtime, you should add those as default arguments during the request report phase. For instance:

.. code-block:: python3

    from functools import partial

    async def receive_data(data, resource_id, measurement):
        for timestamp, value in data:
            await database.execute("""INSERT INTO metervalues (resource_id, measurement, timestamp, value)
                                         VALUES (%s, %s, %s, %s)""", (resource_id, measurement, dt, value))


    async def on_register_report(resource_id, measurement, unit, scale, min_sampling_rate, max_sampling_rate):
        prepared_callback = partial(receive_data, resource_id=resource_id, measurement=measurement)
        return (callback, min_sampling_rate)

The ``partial`` function creates a version of your callback with default parameters filled in.


Identifying a data stream
-------------------------

Reports in OpenADR carry with them the following identifiers:

- ``reportSpecifierID``: the id that the VEN assigns to this report
- ``rID``: the id that the VEN assigns to a specific data stream in the report
- ``reportRequestID``: the id that the VTN assigns to its request of a report
- ``reportID``: the id that the VEN assigns to a single copy of a report

The ``rID`` is the most specific identifier of a data stream. The ``rID`` is part of the ``oadrReportDescription``, along with information like the measurement type, unit, and the ``resourceID``.

