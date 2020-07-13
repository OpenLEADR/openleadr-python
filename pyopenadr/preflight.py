"""
Tests message contents before sending them. It will correct benign errors and
warn you about them. Uncorrectable errors will raise an Exception.
"""
from datetime import timedelta
import warnings

def preflight_message(message_type, message_payload):
    if f'preflight_{message_type}' in globals():
        message_payload = globals()[f'preflight_{message_type}'](message_payload)
    return message_type, message_payload

def preflight_oadrDistributeEvent(message_payload):
    # Check that the total event_duration matches the sum of the interval durations (rule 8)
    for event in message_payload['events']:
        active_period_duration = event['active_period']['duration']
        signal_durations = []
        for signal in event['event_signals']:
            signal_durations.append(sum([i['duration'] for i in signal['intervals']], timedelta(seconds=0)))


        if not all([d==active_period_duration for d in signal_durations]):
            if not all([d==signal_durations[0] for d in signal_durations]):
                raise ValueError("The different EventSignals have different total durations. Please correct this.")
            else:
                warnings.warn(f"The active_period duration for event {event['event_descriptor']['event_id']} ({active_period_duration})"
                              f" was different from the sum of the interval's durations ({signal_durations[0]})."
                              f" The active_period duration has been adjusted to ({signal_durations[0]}).")
                event['active_period']['duration'] = signal_durations[0]

