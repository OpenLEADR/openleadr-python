# SPDX-License-Identifier: Apache-2.0

# Copyright 2020 Contributors to OpenLEADR

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime, timedelta, timezone
from dataclasses import asdict, is_dataclass
from openleadr import enums, utils
import logging
logger = logging.getLogger('openleadr')


def preflight_message(message_type, message_payload):
    """
    Tests message contents before sending them. It will correct benign errors
    and warn you about them. Uncorrectable errors will raise an Exception. It
    changes the message_payload dict in-place.

    :param message_type string: The type of message you are sending
    :param message_payload dict: The contents of the message
    """
    if f'_preflight_{message_type}' in globals():
        message_payload = message_payload.copy()
        for key, value in message_payload.items():
            if isinstance(value, list):
                message_payload[key] = [asdict(item) if is_dataclass(item) else item
                                        for item in value]
            else:
                message_payload[key] = asdict(value) if is_dataclass(value) else value
        globals()[f'_preflight_{message_type}'](message_payload)
    return message_payload


def _preflight_oadrRegisterReport(message_payload):
    for report in message_payload['reports']:
        # Check that the report name is preceded by METADATA_ when registering reports
        if report['report_name'] in enums.REPORT_NAME.values \
                and not report['report_name'].startswith("METADATA"):
            report['report_name'] = 'METADATA_' + report['report_name']

        # Check that the measurement name and description match according to the schema
        for report_description in report['report_descriptions']:
            if 'measurement' in report_description and report_description['measurement'] is not None:
                utils.validate_report_measurement_dict(report_description['measurement'])

        # Add the correct namespace to the measurement
        for report_description in report['report_descriptions']:
            if 'measurement' in report_description and report_description['measurement'] is not None:
                if report_description['measurement']['name'] in enums._MEASUREMENT_NAMESPACES:
                    measurement_name = report_description['measurement']['name']
                    measurement_ns = enums._MEASUREMENT_NAMESPACES[measurement_name]
                    report_description['measurement']['ns'] = measurement_ns
                else:
                    raise ValueError("The Measurement Name is unknown")


def _preflight_oadrDistributeEvent(message_payload):
    if 'parse_duration' not in globals():
        from .utils import parse_duration
    # Check that the total event_duration matches the sum of the interval durations (rule 8)
    for event in message_payload['events']:
        active_period_duration = event['active_period']['duration']
        signal_durations = []
        for signal in event['event_signals']:
            signal_durations.append(sum([parse_duration(i['duration'])
                                         for i in signal['intervals']], timedelta(seconds=0)))

        if not all([d == active_period_duration for d in signal_durations]):
            if not all([d == signal_durations[0] for d in signal_durations]):
                raise ValueError("The different EventSignals have different total durations. "
                                 "Please correct this.")
            else:
                logger.warning(f"The active_period duration for event "
                               f"{event['event_descriptor']['event_id']} ({active_period_duration})"
                               f" differs from the sum of the interval's durations "
                               f"({signal_durations[0]}). The active_period duration has been "
                               f"adjusted to ({signal_durations[0]}).")
                event['active_period']['duration'] = signal_durations[0]

    # Check that payload values with signal name SIMPLE are constricted (rule 9)
    for event in message_payload['events']:
        for event_signal in event['event_signals']:
            if event_signal['signal_name'] == "SIMPLE":
                for interval in event_signal['intervals']:
                    if interval['signal_payload'] not in (0, 1, 2, 3):
                        raise ValueError("Payload Values used with Signal Name SIMPLE "
                                         "must be one of 0, 1, 2 or 3")

    # Check that the current_value is 0 for SIMPLE events that are not yet active (rule 14)
    for event in message_payload['events']:
        for event_signal in event['event_signals']:
            if 'current_value' in event_signal and event_signal['current_value'] != 0:
                if event_signal['signal_name'] == "SIMPLE" \
                        and event['event_descriptor']['event_status'] != "ACTIVE":
                    logger.warning("The current_value for a SIMPLE event "
                                   "that is not yet active must be 0. "
                                   "This will be corrected.")
                    event_signal['current_value'] = 0

    # Add the correct namespace to the measurement
    for event in message_payload['events']:
        for event_signal in event['event_signals']:
            if 'measurement' in event_signal and event_signal['measurement'] is not None:
                if event_signal['measurement']['name'] in enums._MEASUREMENT_NAMESPACES:
                    measurement_name = event_signal['measurement']['name']
                    measurement_ns = enums._MEASUREMENT_NAMESPACES[measurement_name]
                    event_signal['measurement']['ns'] = measurement_ns
                else:
                    raise ValueError("The Measurement Name is unknown")

    # Check that there is a valid oadrResponseRequired value for each Event
    for event in message_payload['events']:
        if 'response_required' not in event:
            event['response_required'] = 'always'
        elif event['response_required'] not in ('never', 'always'):
            logger.warning(f"The response_required property in an Event "
                           f"should be 'never' or 'always', not "
                           f"{event['response_required']}. Changing to 'always'.")
            event['response_required'] = 'always'

    # Check that there is a valid oadrResponseRequired value for each Event
    for event in message_payload['events']:
        if 'created_date_time' not in event['event_descriptor'] \
                or not event['event_descriptor']['created_date_time']:
            logger.warning("Your event descriptor did not contain a created_date_time. "
                           "This will be automatically added.")
            event['event_descriptor']['created_date_time'] = datetime.now(timezone.utc)

    # Check that the target designations are correct and consistent
    for event in message_payload['events']:
        if 'targets' in event and 'targets_by_type' in event:
            if utils.group_targets_by_type(event['targets']) != event['targets_by_type']:
                raise ValueError("You assigned both 'targets' and 'targets_by_type' in your event, "
                                 "but the two were not consistent with each other. "
                                 f"You supplied 'targets' = {event['targets']} and "
                                 f"'targets_by_type' = {event['targets_by_type']}")
        elif 'targets_by_type' in event and 'targets' not in event:
            event['targets'] = utils.ungroup_targets_by_type(event['targets_by_type'])
