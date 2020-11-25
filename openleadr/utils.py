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
import itertools
import re
import ssl
import hashlib
import uuid

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FORMAT_NO_MICROSECONDS = "%Y-%m-%dT%H:%M:%SZ"


def generate_id(*args, **kwargs):
    """
    Generate a string that can be used as an identifier in OpenADR messages.
    """
    return str(uuid.uuid4())


def indent_xml(message):
    """
    Indents the XML in a nice way.
    """
    INDENT_SIZE = 2
    lines = [line.strip() for line in message.split("\n") if line.strip() != ""]
    indent = 0
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if re.search(r'^</[^>]+>$', line):
            indent = indent - INDENT_SIZE
        lines[i] = " " * indent + line
        if not (re.search(r'</[^>]+>$', line) or line.endswith("/>")):
            indent = indent + INDENT_SIZE
    return "\n".join(lines)


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
        if key in ("target",):
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
                if 'voltage' in description:
                    item_name, item = 'voltage', description.pop('voltage')
                elif 'power_real' in description:
                    item_name, item = 'powerReal', description.pop('power_real')
                elif 'power_apparent' in description:
                    item_name, item = 'powerApparent', description.pop('power_apparent')
                elif 'power_reactive' in description:
                    item_name, item = 'powerReactive', description.pop('power_reactive')
                elif 'energy_real' in description:
                    item_name, item = 'energyReal', description.pop('energy_real')
                elif 'energy_apparent' in description:
                    item_name, item = 'energyApparent', description.pop('energy_apparent')
                elif 'energy_reactive' in description:
                    item_name, item = 'energyReactive', description.pop('energy_reactive')
                elif 'frequency' in description:
                    item_name, item = 'frequency', description.pop('frequency')
                elif 'pulse_count' in description:
                    item_name, item = 'pulseCount', description.pop('pulse_count')
                elif 'temperature' in description:
                    item_name, item = 'temperature', description.pop('temperature')
                elif 'therm' in description:
                    item_name, item = 'therm', description.pop('therm')
                elif 'currency' in description:
                    item_name, item = 'currency', description.pop('currency')
                elif 'currency_per_kw' in description:
                    item_name, item = 'currencyPerKW', description.pop('currency_per_kw')
                elif 'currency_per_kwh' in description:
                    item_name, item = 'currencyPerKWh', description.pop('currency_per_kwh')
                elif 'currency_per_therm' in description:
                    item_name, item = 'currencyPerTherm', description.pop('currency_per_therm')
                elif 'custom_unit' in description:
                    item_name, item = 'customUnit', description.pop('custom_unit')
                else:
                    break
                description['measurement'] = {'item_name': item_name,
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
        print(f"{value} did not match format")
        return value


def parse_duration(value):
    """
    Parse a RFC5545 duration.
    """
    # TODO: implement the full regex:
    # matches = re.match(r'(\+|\-)?P((\d+Y)?(\d+M)?(\d+D)?T?(\d+H)?(\d+M)?(\d+S)?)|(\d+W)', value)
    if isinstance(value, timedelta):
        return value
    matches = re.match(r'P(\d+(?:D|W))?T?(\d+H)?(\d+M)?(\d+S)?', value)
    if not matches:
        return False
    days = hours = minutes = seconds = 0
    _days, _hours, _minutes, _seconds = matches.groups()
    if _days:
        if _days.endswith("D"):
            days = int(_days[:-1])
        elif _days.endswith("W"):
            days = int(_days[:-1]) * 7
    if _hours:
        hours = int(_hours[:-1])
    if _minutes:
        minutes = int(_minutes[:-1])
    if _seconds:
        seconds = int(_seconds[:-1])
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def parse_boolean(value):
    if value == 'true':
        return True
    else:
        return False


def peek(iterable):
    """
    Peek into an iterable.
    """
    try:
        first = next(iterable)
    except StopIteration:
        return None
    else:
        return itertools.chain([first], iterable)


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
                if _item[key] not in value:
                    break
            else:
                if _item[key] != value:
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


def cron_config(interval):
    """
    Returns a dict with cron settings for the given interval
    """
    if interval < timedelta(minutes=1):
        second = f"*/{interval.seconds}"
        minute = "*"
        hour = "*"
    elif interval < timedelta(hours=1):
        second = "0"
        minute = f"*/{int(interval.total_seconds/60)}"
        hour = "*"
    elif interval < timedelta(days=1):
        second = "0"
        minute = "0"
        hour = f"*/{int(interval.total_seconds/3600)}"
    return {"second": second, "minute": minute, "hour": hour}


def get_cert_fingerprint_from_request(request):
    ssl_object = request.transport.get_extra_info('ssl_object')
    if ssl_object:
        der_bytes = ssl_object.getpeercert(binary_form=True)
        if der_bytes:
            return certificate_fingerprint_from_der(der_bytes)


def get_certificate_common_name(request):
    cert = request.transport.get_extra_info('peercert')
    if cert:
        subject = dict(x[0] for x in cert['subject'])
        return subject.get('commonName')
