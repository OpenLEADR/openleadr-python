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

from asyncio import iscoroutine
from datetime import datetime, timedelta, timezone
import random
import string
from collections import OrderedDict
import itertools
import re

from pyopenadr import config

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATETIME_FORMAT_NO_MICROSECONDS = "%Y-%m-%dT%H:%M:%SZ"

def new_request_id(*args, **kwargs):
    return random.choice(string.ascii_lowercase) + ''.join(random.choice(string.hexdigits) for _ in range(9)).lower()

def generate_id(*args, **kwargs):
    return new_request_id()

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
    lines = [line.strip() for line in message.split("\n") if line.strip() != ""]
    for line in lines:
        line = re.sub(r'\n', '', line)
        line = re.sub(r'\s\s+', ' ', line)
    return "".join(lines)

def normalize_dict(ordered_dict):
    """
    Convert the OrderedDict to a regular dict, snake_case the key names, and promote uniform lists.
    """
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

        if isinstance(value, OrderedDict):
            d[key] = normalize_dict(value)
        elif isinstance(value, list):
            d[key] = []
            for item in value:
                if isinstance(item, OrderedDict):
                    dict_item = normalize_dict(item)
                    d[key].append(normalize_dict(dict_item))
                else:
                    d[key].append(item)
        elif key in ("duration", "startafter", "max_period", "min_period"):
            d[key] = parse_duration(value)
        elif "date_time" in key and isinstance(value, str):
            d[key] = parse_datetime(value)
        elif value in ('true', 'false'):
            d[key] = parse_boolean(value)
        elif isinstance(value, str):
            d[key] = parse_int(value) or parse_float(value) or value
        else:
            d[key] = value

        # Do our best to make the dictionary structure as pythonic as possible
        if key.startswith("x_ei_"):
            d[key[5:]] = d.pop(key)
            key = key[5:]

        # Group all targets as a list of dicts under the key "target"
        if key in ("target", "report_subject", "report_data_source"):
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

        # Dig up the properties inside some specific target identifiers
        # if key in ("aggregated_pnode", "pnode", "service_delivery_point"):
        #     d[key] = d[key]["node"]

        # if key in ("end_device_asset", "meter_asset"):
        #     d[key] = d[key]["mrid"]

        # Group all reports as a list of dicts under the key "pending_reports"
        if key == "pending_reports":
            if isinstance(d[key], dict) and 'report_request_id' in d[key] and isinstance(d[key]['report_request_id'], list):
                d['pending_reports'] = [{'request_id': rrid} for rrid in d['pending_reports']['report_request_id']]

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
        elif key in ('report_request', 'report'):
            if isinstance(d[key], list):
                d[key + 's'] = d.pop(key)
            else:
                d[key + 's'] = [d.pop(key)]

        elif key == 'report_description':
            if isinstance(d[key], list):
                original_descriptions = d.pop(key)
                report_descriptions = {}
                for item in original_descriptions:
                    r_id = item.pop('r_id')
                    report_descriptions[r_id] = item
                d[key + 's'] = report_descriptions
            else:
                original_description = d.pop(key)
                r_id = original_description.pop('r_id')
                d[key + 's'] = {r_id: original_description}

        # Promote the contents of the Qualified Event ID
        elif key == "qualified_event_id" and isinstance(d['qualified_event_id'], dict):
            qeid = d.pop('qualified_event_id')
            d['event_id'] = qeid['event_id']
            d['modification_number'] = qeid['modification_number']

        # Promote the contents of the tolerance items
        # if key == "tolerance" and "tolerate" in d["tolerance"] and len(d["tolerance"]["tolerate"]) == 1:
        #     d["tolerance"] = d["tolerance"]["tolerate"].values()[0]

        # Durations are encapsulated in their own object, remove this nesting
        elif isinstance(d[key], dict) and "duration" in d[key] and len(d[key]) == 1:
            try:
                d[key] = d[key]["duration"]
            except:
                breakpoint()

        # In general, remove all double nesting
        elif isinstance(d[key], dict) and key in d[key] and len(d[key]) == 1:
            d[key] = d[key][key]

        # In general, remove the double nesting of lists of items
        elif isinstance(d[key], dict) and key[:-1] in d[key] and len(d[key]) == 1:
            if isinstance(d[key][key[:-1]], list):
                d[key] = d[key][key[:-1]]
            else:
                d[key] = [d[key][key[:-1]]]

        # Payload values are wrapped in an object according to their type. We don't need that information.
        elif key in ("signal_payload", "current_value"):
            value = d[key]
            if isinstance(d[key], dict):
                if 'payload_float' in d[key] and 'value' in d[key]['payload_float'] and d[key]['payload_float']['value'] is not None:
                    d[key] = float(d[key]['payload_float']['value'])
                elif 'payload_int' in d[key] and 'value' in d[key]['payload_int'] and d[key]['payload_int'] is not None:
                    d[key] = int(d[key]['payload_int']['value'])

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
    Parse an ISO8601 datetime
    """
    matches = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.?(\d{1,6})?\d*Z', value)
    if matches:
        year, month, day, hour, minute, second, microsecond = (int(value) for value in matches.groups())
        return datetime(year, month, day, hour, minute, second, microsecond=microsecond, tzinfo=timezone.utc)
    else:
        print(f"{value} did not match format")
        return value

def parse_duration(value):
    """
    Parse a RFC5545 duration.
    """
    # TODO: implement the full regex: matches = re.match(r'(\+|\-)?P((\d+Y)?(\d+M)?(\d+D)?T?(\d+H)?(\d+M)?(\d+S)?)|(\d+W)', value)
    if isinstance(value, timedelta):
        return value
    matches = re.match(r'P(\d+(?:D|W))?T(\d+H)?(\d+M)?(\d+S)?', value)
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

def parse_int(value):
    matches = re.match(r'^[\d-]+$', value)
    if not matches:
        return False
    else:
        return int(value)

def parse_float(value):
    matches = re.match(r'^[\d.-]+$', value)
    if not matches:
        return False
    else:
        return float(value)

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
        formatted += f"T"
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
        if value == True:
            return "true"
        elif value == False:
            return "false"
    elif value in ("true", "false"):
        return value
    else:
        raise ValueError("A boolean value must be provided.")

def ensure_bytes(obj):
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, str):
        return bytes(obj, 'utf-8')
    else:
        raise TypeError("Must be bytes or str")