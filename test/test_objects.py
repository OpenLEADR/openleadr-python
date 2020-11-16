from openleadr import objects, enums
from datetime import datetime, timedelta
from openleadr.messaging import create_message, parse_message
from pprint import pprint

def test_oadr_event():
    event = objects.Event(
        event_descriptor=objects.EventDescriptor(
            event_id=1,
            modification_number=0,
            market_context='MarketContext1',
            event_status=enums.EVENT_STATUS.NEAR),
        active_period=objects.ActivePeriod(
            dtstart=datetime.now(),
            duration=timedelta(minutes=10)),
        event_signals=[objects.EventSignal(
            intervals=[
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=0,
                    signal_payload=1),
                objects.Interval(
                    dtstart=datetime.now(),
                    duration=timedelta(minutes=5),
                    uid=1,
                    signal_payload=2)],
            targets=[objects.Target(
                ven_id='1234'
            )],
            signal_name=enums.SIGNAL_NAME.LOAD_CONTROL,
            signal_type=enums.SIGNAL_TYPE.LEVEL,
            signal_id=1,
            current_value=0
        )],
        targets=[objects.Target(
            ven_id='1234'
        )]
    )

    response = objects.Response(response_code=200,
                                response_description='OK',
                                request_id='1234')
    msg = create_message('oadrDistributeEvent', response=response, events=[event])
    message_type, message_payload = parse_message(msg)



def test_oadr_report():
    report = objects.Report(
        created_date_time=datetime.now(),
        duration=timedelta(hours=1),
        report_specifier_id='id001',
        report_descriptions=[
            objects.ReportDescription(
                r_id='report001',
                market_context='market001',
                reading_type=enums.READING_TYPE.DIRECT_READ,
                report_subject=objects.Target(

                ),
                report_data_source=objects.Target(
                    resource_id='resource001'
                ),
                report_type=enums.REPORT_TYPE.READING,
                sampling_rate=timedelta(seconds=10),
                measurement=enums.MEASUREMENTS.VOLTAGE
            )
        ],
        report_name=enums.REPORT_NAME.HISTORY_USAGE)

