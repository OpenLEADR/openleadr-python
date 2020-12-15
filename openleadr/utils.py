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
from dataclasses import is_dataclass, asdict
from collections import OrderedDict
from openleadr import enums, objects
import asyncio
import re
import ssl
import hashlib
import uuid
import logging

logger = logging.getLogger('openleadr')

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FORMAT_NO_MICROSECONDS = "%Y-%m-%dT%H:%M:%SZ"


def generate_id(*args, **kwargs):
    """
    Generate a string that can be used as an identifier in OpenADR messages.
    """
    return str(uuid.uuid4())


def flatten_xml(message):
    """
    Flatten the entire XML structure.
    """
    lines = [line.strip() for line in message.split("\n") if line.strip() != ""]
    for line in lines:
        line = re.sub(r'\n', '', line)
        line = re.sub(r'\s\s+', ' ', line)
    return "".join(lines)


def normalize_dict(ordered_dict):
    """
    Main conversion function for the output of xmltodict to the OpenLEADR
    representation of OpenADR contents.

    :param ordered_dict dict: The OrderedDict, dict or dataclass that you wish to convert.
    """
    if is_dataclass(ordered_dict):
        ordered_dict = asdict(ordered_dict)

    def normalize_key(key):
        if key.startswith('oadr'):
            key = key[4:]
        elif key.startswith('ei'):
            key = key[2:]
        # Don't normalize the measurement descriptions
        if key in enums._MEASUREMENT_NAMESPACES:
            return key
        key = re.sub(r'([a-z])([A-Z])', r'\1_\2', key)
        if '-' in key:
            key = key.replace('-', '_')
        return key.lower()

    d = {}
    for key, value in ordered_dict.items():
        # Interpret values from the dict
        if key.startswith("@"):
            continue
        key = normalize_key(key)

        if isinstance(value, (OrderedDict, dict)):
            d[key] = normalize_dict(value)

        elif isinstance(value, list):
            d[key] = []
            for item in value:
                if isinstance(item, (OrderedDict, dict)):
                    dict_item = normalize_dict(item)
                    d[key].append(normalize_dict(dict_item))
                else:
                    d[key].append(item)
        elif key in ("duration", "startafter", "max_period", "min_period"):
            d[key] = parse_duration(value)
        elif ("date_time" in key or key == "dtstart") and isinstance(value, str):
            d[key] = parse_datetime(value)
        elif value in ('true', 'false'):
            d[key] = parse_boolean(value)
        elif isinstance(value, str):
            if re.match(r'^-?\d+$', value):
                d[key] = int(value)
            elif re.match(r'^-?[\d.]+$', value):
                d[key] = float(value)
            else:
                d[key] = value
        else:
            d[key] = value

        # Do our best to make the dictionary structure as pythonic as possible
        if key.startswith("x_ei_"):
            d[key[5:]] = d.pop(key)
            key = key[5:]

        # Group all targets as a list of dicts under the key "target"
        if key == 'target':
            targets = d.pop(key)
            new_targets = []
            if targets:
                for ikey in targets:
                    if isinstance(targets[ikey], list):
                        new_targets.extend([{ikey: value} for value in targets[ikey]])
                    else:
                        new_targets.append({ikey: targets[ikey]})
            d[key + "s"] = new_targets
            key = key + "s"

            # Also add a targets_by_type element to this dict
            # to access the targets in a more convenient way.
            d['targets_by_type'] = group_targets_by_type(new_targets)

        # Group all reports as a list of dicts under the key "pending_reports"
        if key == "pending_reports":
            if isinstance(d[key], dict) and 'report_request_id' in d[key] \
               and isinstance(d[key]['report_request_id'], list):
                d['pending_reports'] = [{'request_id': rrid}
                                        for rrid in d['pending_reports']['report_request_id']]

        # Group all events al a list of dicts under the key "events"
        elif key == "event" and isinstance(d[key], list):
            events = d.pop("event")
            new_events = []
            for event in events:
                new_event = event['event']
                new_event['response_required'] = event['response_required']
                new_events.append(new_event)
            d["events"] = new_events

        # If there's only one event, also put it into a list
        elif key == "event" and isinstance(d[key], dict) and "event" in d[key]:
            oadr_event = d.pop('event')
            ei_event = oadr_event['event']
            ei_event['response_required'] = oadr_event['response_required']
            d['events'] = [ei_event]

        elif key in ("request_event", "created_event") and isinstance(d[key], dict):
            d = d[key]

        # Plurarize some lists
        elif key in ('report_request', 'report', 'specifier_payload'):
            if isinstance(d[key], list):
                d[key + 's'] = d.pop(key)
            else:
                d[key + 's'] = [d.pop(key)]

        elif key in ('report_description', 'event_signal'):
            descriptions = d.pop(key)
            if not isinstance(descriptions, list):
                descriptions = [descriptions]
            for description in descriptions:
                # We want to make the identification of the measurement universal
                for measurement in enums._MEASUREMENT_NAMESPACES:
                    if measurement in description:
                        name, item = measurement, description.pop(measurement)
                        break
                else:
                    break
                item['description'] = item.pop('item_description', None)
                item['unit'] = item.pop('item_units', None)
                if 'si_scale_code' in item:
                    item['scale'] = item.pop('si_scale_code')
                if 'pulse_factor' in item:
                    item['pulse_factor'] = item.pop('pulse_factor')
                description['measurement'] = {'name': name,
                                              **item}
            d[key + 's'] = descriptions

        # Promote the contents of the Qualified Event ID
        elif key == "qualified_event_id" and isinstance(d['qualified_event_id'], dict):
            qeid = d.pop('qualified_event_id')
            d['event_id'] = qeid['event_id']
            d['modification_number'] = qeid['modification_number']

        # Durations are encapsulated in their own object, remove this nesting
        elif isinstance(d[key], dict) and "duration" in d[key] and len(d[key]) == 1:
            d[key] = d[key]["duration"]

        # In general, remove all double nesting
        elif isinstance(d[key], dict) and key in d[key] and len(d[key]) == 1:
            d[key] = d[key][key]

        # In general, remove the double nesting of lists of items
        elif isinstance(d[key], dict) and key[:-1] in d[key] and len(d[key]) == 1:
            if isinstance(d[key][key[:-1]], list):
                d[key] = d[key][key[:-1]]
            else:
                d[key] = [d[key][key[:-1]]]

        # Payload values are wrapped in an object according to their type. We don't need that.
        elif key in ("signal_payload", "current_value"):
            value = d[key]
            if isinstance(d[key], dict):
                if 'payload_float' in d[key] and 'value' in d[key]['payload_float'] \
                        and d[key]['payload_float']['value'] is not None:
                    d[key] = float(d[key]['payload_float']['value'])
                elif 'payload_int' in d[key] and 'value' in d[key]['payload_int'] \
                        and d[key]['payload_int'] is not None:
                    d[key] = int(d[key]['payload_int']['value'])

        # Report payloads contain an r_id and a type-wrapped payload_float
        elif key == 'report_payload':
            if 'payload_float' in d[key] and 'value' in d[key]['payload_float']:
                v = d[key].pop('payload_float')
                d[key]['value'] = float(v['value'])
            elif 'payload_int' in d[key] and 'value' in d[key]['payload_int']:
                v = d[key].pop('payload_float')
                d[key]['value'] = int(v['value'])

        # All values other than 'false' must be interpreted as True for testEvent (rule 006)
        elif key == 'test_event' and not isinstance(d[key], bool):
            d[key] = True

        # Promote the 'text' item
        elif isinstance(d[key], dict) and "text" in d[key] and len(d[key]) == 1:
            if key == 'uid':
                d[key] = int(d[key]["text"])
            else:
                d[key] = d[key]["text"]

        # Promote a 'date-time' item
        elif isinstance(d[key], dict) and "date_time" in d[key] and len(d[key]) == 1:
            d[key] = d[key]["date_time"]

        # Promote 'properties' item, discard the unused? 'components' item
        elif isinstance(d[key], dict) and "properties" in d[key] and len(d[key]) <= 2:
            d[key] = d[key]["properties"]

        # Remove all empty dicts
        elif isinstance(d[key], dict) and len(d[key]) == 0:
            d.pop(key)
    return d


def parse_datetime(value):
    """
    Parse an ISO8601 datetime into a datetime.datetime object.
    """
    matches = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.?(\d{1,6})?\d*Z', value)
    if matches:
        year, month, day, hour, minute, second, micro = (int(value) for value in matches.groups())
        return datetime(year, month, day, hour, minute, second, micro, tzinfo=timezone.utc)
    else:
        logger.warning(f"parse_datetime: {value} did not match format")
        return value


def parse_duration(value):
    """
    Parse a RFC5545 duration.
    """
    if isinstance(value, timedelta):
        return value
    regex = r'(\+|\-)?P(?:(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)|(?:(\d+)W)'
    matches = re.match(regex, value)
    if not matches:
        raise ValueError(f"The duration '{value}' did not match the requested format")
    years, months, days, hours, minutes, seconds, weeks = (int(g) if g else 0 for g in matches.groups()[1:])
    if years != 0:
        logger.warning("Received a duration that specifies years, which is not a determinate duration. "
                       "It will be interpreted as 1 year = 365 days.")
        days = days + 365 * years
    if months != 0:
        logger.warning("Received a duration that specifies months, which is not a determinate duration "
                       "It will be interpreted as 1 month = 30 days.")
        days = days + 30 * months
    duration = timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
    if matches.groups()[0] == "-":
        duration = -1 * duration
    return duration


def parse_boolean(value):
    if value == 'true':
        return True
    else:
        return False


def datetimeformat(value, format=DATETIME_FORMAT):
    """
    Format a given datetime as a UTC ISO3339 string.
    """
    if not isinstance(value, datetime):
        return value
    return value.astimezone(timezone.utc).strftime(format)


def timedeltaformat(value):
    """
    Format a timedelta to a RFC5545 Duration.
    """
    if not isinstance(value, timedelta):
        return value
    days = value.days
    hours, seconds = divmod(value.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    formatted = "P"
    if days:
        formatted += f"{days}D"
    if hours or minutes or seconds:
        formatted += "T"
    if hours:
        formatted += f"{hours}H"
    if minutes:
        formatted += f"{minutes}M"
    if seconds:
        formatted += f"{seconds}S"
    return formatted


def booleanformat(value):
    """
    Format a boolean value
    """
    if isinstance(value, bool):
        if value is True:
            return "true"
        elif value is False:
            return "false"
    elif value in ("true", "false"):
        return value
    else:
        raise ValueError(f"A boolean value must be provided, not {value}.")


def ensure_bytes(obj):
    """
    Converts a utf-8 str object to bytes.
    """
    if obj is None:
        return obj
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, str):
        return bytes(obj, 'utf-8')
    else:
        raise TypeError("Must be bytes or str")


def ensure_str(obj):
    """
    Converts bytes to a utf-8 string.
    """
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        raise TypeError("Must be bytes or str")


def certificate_fingerprint_from_der(der_bytes):
    hash = hashlib.sha256(der_bytes).digest().hex()
    return ":".join([hash[i-2:i].upper() for i in range(-20, 0, 2)])


def certificate_fingerprint(certificate_str):
    """
    Calculate the fingerprint for the given certificate, as defined by OpenADR.
    """
    der_bytes = ssl.PEM_cert_to_DER_cert(ensure_str(certificate_str))
    return certificate_fingerprint_from_der(der_bytes)


def extract_pem_cert(tree):
    """
    Extract a given X509 certificate inside an XML tree and return the standard
    form of a PEM-encoded certificate.

    :param tree lxml.etree: The tree that contains the X509 element. This is
                            usually the KeyInfo element from the XMLDsig Signature
                            part of the message.
    """
    cert = tree.find('.//{http://www.w3.org/2000/09/xmldsig#}X509Certificate').text
    return "-----BEGIN CERTIFICATE-----\n" + cert + "-----END CERTIFICATE-----\n"


def find_by(dict_or_list, key, value, *args):
    """
    Find a dict inside a dict or list by key, value properties.
    """
    search_params = [(key, value)]
    if args:
        search_params += [(args[i], args[i+1]) for i in range(0, len(args), 2)]
    if isinstance(dict_or_list, dict):
        dict_or_list = dict_or_list.values()
    for item in dict_or_list:
        if not isinstance(item, dict):
            _item = item.__dict__
        else:
            _item = item
        for key, value in search_params:
            if isinstance(value, tuple):
                if key not in _item or _item[key] not in value:
                    break
            else:
                if key not in _item or _item[key] != value:
                    break
        else:
            return item
    else:
        return None


def group_by(list_, key, pop_key=False):
    """
    Return a dict that groups values
    """
    grouped = {}
    key_path = key.split(".")
    for item in list_:
        value = item
        for key in key_path:
            value = value.get(key)
        if value not in grouped:
            grouped[value] = []
        grouped[value].append(item)
    return grouped


def cron_config(interval, randomize_seconds=False):
    """
    Returns a dict with cron settings for the given interval
    """
    if interval < timedelta(minutes=1):
        second = f"*/{interval.seconds}"
        minute = "*"
        hour = "*"
    elif interval < timedelta(hours=1):
        second = "0"
        minute = f"*/{int(interval.total_seconds()/60)}"
        hour = "*"
    elif interval < timedelta(hours=24):
        second = "0"
        minute = "0"
        hour = f"*/{int(interval.total_seconds()/3600)}"
    else:
        second = "0"
        minute = "0"
        hour = "0"
    cron_config = {"second": second, "minute": minute, "hour": hour}
    if randomize_seconds:
        jitter = min(int(interval.total_seconds() / 10), 300)
        cron_config['jitter'] = jitter
    return cron_config


def get_cert_fingerprint_from_request(request):
    ssl_object = request.transport.get_extra_info('ssl_object')
    if ssl_object:
        der_bytes = ssl_object.getpeercert(binary_form=True)
        if der_bytes:
            return certificate_fingerprint_from_der(der_bytes)


def group_targets_by_type(list_of_targets):
    targets_by_type = {}
    for target in list_of_targets:
        for key, value in target.items():
            if value is None:
                continue
            if key not in targets_by_type:
                targets_by_type[key] = []
            targets_by_type[key].append(value)
    return targets_by_type


def ungroup_targets_by_type(targets_by_type):
    ungrouped_targets = []
    for target_type, targets in targets_by_type.items():
        if isinstance(targets, list):
            for target in targets:
                ungrouped_targets.append({target_type: target})
        elif isinstance(targets, str):
            ungrouped_targets.append({target_type: targets})
    return ungrouped_targets


def validate_report_measurement_dict(measurement):
    from openleadr.enums import _ACCEPTABLE_UNITS, _MEASUREMENT_DESCRIPTIONS

    if 'name' not in measurement \
            or 'description' not in measurement \
            or 'unit' not in measurement:
        raise ValueError("The measurement dict must contain the following keys: "
                         "'name', 'description', 'unit'. Please correct this.")

    name = measurement['name']
    description = measurement['description']
    unit = measurement['unit']

    # Validate the item name and description match
    if name in _MEASUREMENT_DESCRIPTIONS:
        required_description = _MEASUREMENT_DESCRIPTIONS[name]
        if description != required_description:
            if description.lower() == required_description.lower():
                logger.warning(f"The description for the measurement with name '{name}' "
                               f"was not in the correct case; you provided '{description}' but "
                               f"it should be '{required_description}'. "
                               "This was automatically corrected.")
                measurement['description'] = required_description
            else:
                raise ValueError(f"The measurement's description '{description}' "
                                 f"did not match the expected description for this type "
                                 f" ('{required_description}'). Please correct this, or use "
                                 "'customUnit' as the name.")
        if unit not in _ACCEPTABLE_UNITS[name]:
            raise ValueError(f"The unit '{unit}' is not acceptable for measurement '{name}'. Allowed "
                             f"units are: '" + "', '".join(_ACCEPTABLE_UNITS[name]) + "'.")
    else:
        if name != 'customUnit':
            logger.warning(f"You provided a measurement with an unknown name {name}. "
                           "This was corrected to 'customUnit'. Please correct this in your "
                           "report definition.")
            measurement['name'] = 'customUnit'

    if 'power' in name:
        if 'power_attributes' in measurement:
            power_attributes = measurement['power_attributes']
            if 'voltage' not in power_attributes \
                    or 'ac' not in power_attributes \
                    or 'hertz' not in power_attributes:
                raise ValueError("The power_attributes of the measurement must contain the "
                                 "following keys: 'voltage' (int), 'ac' (bool), 'hertz' (int).")
        else:
            raise ValueError("A 'power' related measurement must contain a "
                             "'power_attributes' section that contains the following "
                             "keys: 'voltage' (int), 'ac' (boolean), 'hertz' (int)")


def get_active_period_from_intervals(intervals, as_dict=True):
    if is_dataclass(intervals[0]):
        intervals = [asdict(i) for i in intervals]
    period_start = min([i['dtstart'] for i in intervals])
    period_duration = max([i['dtstart'] + i['duration'] - period_start for i in intervals])
    if as_dict:
        return {'dtstart': period_start,
                'duration': period_duration}
    else:
        from openleadr.objects import ActivePeriod
        return ActivePeriod(dtstart=period_start, duration=period_duration)


def determine_event_status(active_period):
    if is_dataclass(active_period):
        active_period = asdict(active_period)
    now = datetime.now(timezone.utc)
    if active_period['dtstart'].tzinfo is None:
        active_period['dtstart'] = active_period['dtstart'].astimezone(timezone.utc)
    active_period_start = active_period['dtstart']
    active_period_end = active_period['dtstart'] + active_period['duration']
    if now >= active_period_end:
        return 'completed'
    if now >= active_period_start:
        return 'active'
    if active_period.get('ramp_up_duration') is not None:
        ramp_up_start = active_period_start - active_period['ramp_up_duration']
        if now >= ramp_up_start:
            return 'near'
    return 'far'


async def delayed_call(func, delay):
    try:
        if isinstance(delay, timedelta):
            delay = delay.total_seconds()
        await asyncio.sleep(delay)
        if asyncio.iscoroutinefunction(func):
            await func()
        elif asyncio.iscoroutine(func):
            await func
        else:
            func()
    except asyncio.CancelledError:
        pass


def hasmember(obj, member):
    """
    Check if a dict or dataclass has the given member
    """
    if is_dataclass(obj):
        if hasattr(obj, member):
            return True
    else:
        if member in obj:
            return True
    return False


def getmember(obj, member):
    """
    Get a member from a dict or dataclass
    """
    if is_dataclass(obj):
        return getattr(obj, member)
    else:
        return obj[member]


def setmember(obj, member, value):
    """
    Set a member of a dict of dataclass
    """
    if is_dataclass(obj):
        setattr(obj, member, value)
    else:
        obj[member] = value


def get_next_event_from_deque(deque):
    unused_elements = []
    event = None
    for i in range(len(deque)):
        msg = deque.popleft()
        if isinstance(msg, objects.Event) or (isinstance(msg, dict) and 'event_descriptor' in msg):
            event = msg
            break
        else:
            unused_elements.append(msg)
    deque.extend(unused_elements)
    return event
