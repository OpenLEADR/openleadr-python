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

from aiohttp import web
from openleadr.service import EventService, PollService, RegistrationService, ReportService, \
                              VTNService
from openleadr.messaging import create_message
from openleadr import objects, enums, utils
from functools import partial
from datetime import datetime, timedelta, timezone
import asyncio
import inspect
import logging
import ssl
import re
logger = logging.getLogger('openleadr')


class OpenADRServer:
    _MAP = {'on_created_event': 'event_service',
            'on_request_event': 'event_service',

            'on_register_report': 'report_service',
            'on_create_report': 'report_service',
            'on_created_report': 'report_service',
            'on_request_report': 'report_service',
            'on_update_report': 'report_service',

            'on_poll': 'poll_service',

            'on_query_registration': 'registration_service',
            'on_create_party_registration': 'registration_service',
            'on_cancel_party_registration': 'registration_service'}

    def __init__(self, vtn_id, cert=None, key=None, passphrase=None, fingerprint_lookup=None,
                 show_fingerprint=True, http_port=8080, http_host='127.0.0.1', http_cert=None,
                 http_key=None, http_key_passphrase=None, http_path_prefix='/OpenADR2/Simple/2.0b',
                 requested_poll_freq=timedelta(seconds=10), http_ca_file=None, ven_lookup=None):
        """
        Create a new OpenADR VTN (Server).

        :param str vtn_id: An identifier string for this VTN. This is how you identify yourself
                              to the VENs that talk to you.
        :param str cert: Path to the PEM-formatted certificate file that is used to sign outgoing
                            messages
        :param str key: Path to the PEM-formatted private key file that is used to sign outgoing
                           messages
        :param str passphrase: The passphrase used to decrypt the private key file
        :param callable fingerprint_lookup: A callable that receives a ven_id and should return the
                                            registered fingerprint for that VEN. You should receive
                                            these fingerprints outside of OpenADR and configure them
                                            manually.
        :param bool show_fingerprint: Whether to print the fingerprint to your stdout on startup.
                                         Defaults to True.
        :param int http_port: The port that the web server is exposed on (default: 8080)
        :param str http_host: The host or IP address to bind the server to (default: 127.0.0.1).
        :param str http_cert: The path to the PEM certificate for securing HTTP traffic.
        :param str http_key: The path to the PEM private key for securing HTTP traffic.
        :param str http_ca_file: The path to the CA-file that client certificates are checked against.
        :param str http_key_passphrase: The passphrase for the HTTP private key.
        :param ven_lookup: A callback that takes a ven_id and returns a dict containing the
                           ven_id, ven_name, fingerprint and registration_id.
        """
        # Set up the message queues

        self.app = web.Application()
        self.services = {}
        self.services['event_service'] = EventService(vtn_id)
        self.services['report_service'] = ReportService(vtn_id)
        self.services['poll_service'] = PollService(vtn_id)
        self.services['registration_service'] = RegistrationService(vtn_id, poll_freq=requested_poll_freq)

        # Register the other services with the poll service
        self.services['poll_service'].event_service = self.services['event_service']
        self.services['poll_service'].report_service = self.services['report_service']

        # Set up the HTTP handlers for the services
        if http_path_prefix[-1] == "/":
            http_path_prefix = http_path_prefix[:-1]
        self.app.add_routes([web.post(f"{http_path_prefix}/{s.__service_name__}", s.handler)
                             for s in self.services.values()])

        # Add a reference to the openadr VTN to the aiohttp 'app'
        self.app['server'] = self

        # Configure the web server
        self.http_port = http_port
        self.http_host = http_host
        self.http_path_prefix = http_path_prefix

        # Create SSL context for running the server
        if http_cert and http_key:
            self.ssl_context = ssl.create_default_context(cafile=http_ca_file,
                                                          purpose=ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.load_cert_chain(http_cert, http_key, http_key_passphrase)
        else:
            self.ssl_context = None

        # Configure message signing
        if cert and key:
            with open(cert, "rb") as file:
                cert = file.read()
            with open(key, "rb") as file:
                key = file.read()
            if show_fingerprint:
                print("")
                print("*" * 80)
                print("Your VTN Certificate Fingerprint is "
                      f"{utils.certificate_fingerprint(cert)}".center(80))
                print("Please deliver this fingerprint to the VENs that connect to you.".center(80))
                print("You do not need to keep this a secret.".center(80))
                print("*" * 80)
                print("")
        VTNService._create_message = partial(create_message, cert=cert, key=key,
                                             passphrase=passphrase)
        if fingerprint_lookup is not None:
            logger.warning("DeprecationWarning: the argument 'fingerprint_lookup' is deprecated and "
                           "is replaced by 'ven_lookup'. 'fingerprint_lookup' will be removed in a "
                           "future version of OpenLEADR. Please see "
                           "https://openleadr.org/docs/server.html#things-you-should-implement.")
            VTNService.fingerprint_lookup = staticmethod(fingerprint_lookup)
        if ven_lookup is None:
            logger.warning("If you provide a 'ven_lookup' to your OpenADRServer() init, OpenLEADR can "
                           "automatically issue ReregistrationRequests for VENs that don't exist in "
                           "your system. Please see https://openleadr.org/docs/server.html#things-you-should-implement.")
        else:
            VTNService.ven_lookup = staticmethod(ven_lookup)
        self.__setattr__ = self.add_handler

    async def run(self):
        """
        Starts the server in an already-running asyncio loop.
        """
        self.app_runner = web.AppRunner(self.app)
        await self.app_runner.setup()
        site = web.TCPSite(self.app_runner,
                           port=self.http_port,
                           host=self.http_host,
                           ssl_context=self.ssl_context)
        await site.start()
        protocol = 'https' if self.ssl_context else 'http'
        print("")
        print("*" * 80)
        print("Your VTN Server is now running at ".center(80))
        print(f"{protocol}://{self.http_host}:{self.http_port}{self.http_path_prefix}".center(80))
        print("*" * 80)
        print("")

    async def run_async(self):
        await self.run()

    async def stop(self):
        """
        Stop the server in a graceful manner.
        """
        await self.app_runner.cleanup()

    def add_event(self, ven_id, signal_name, signal_type, intervals, callback=None, event_id=None,
                  targets=None, targets_by_type=None, target=None, response_required='always',
                  market_context="oadr://unknown.context", notification_period=None,
                  ramp_up_period=None, recovery_period=None, signal_target_mrid=None):
        """
        Convenience method to add an event with a single signal.

        :param str ven_id: The ven_id to whom this event must be delivered.
        :param str signal_name: The OpenADR name of the signal; one of openleadr.objects.SIGNAL_NAME
        :param str signal_type: The OpenADR type of the signal; one of openleadr.objects.SIGNAL_TYPE
        :param str intervals: A list of intervals with a dtstart, duration and payload member.
        :param str callback: A callback function for when your event has been accepted (optIn) or refused (optOut).
        :param list targets: A list of Targets that this Event applies to.
        :param target: A single target for this event.
        :param dict targets_by_type: A dict of targets, grouped by type.
        :param str market_context: A URI for the DR program that this event belongs to.
        :param timedelta notification_period: The Notification period for the Event's Active Period.
        :param timedelta ramp_up_period: The Ramp Up period for the Event's Active Period.
        :param timedelta recovery_period: The Recovery period for the Event's Active Period.

        If you don't provide a target using any of the three arguments, the target will be set to the given ven_id.
        """
        if self.services['event_service'].polling_method == 'external':
            logger.error("You cannot use the add_event method after you assign your own on_poll "
                         "handler. If you use your own on_poll handler, you are responsible for "
                         "delivering events from that handler. If you want to use OpenLEADRs "
                         "message queuing system, you should not assign an on_poll handler. "
                         "Your Event will NOT be added.")
            return
        if not re.match(r"^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?", market_context):
            raise ValueError("The Market Context must be a valid URI.")
        event_id = event_id or utils.generate_id()

        if response_required not in ('always', 'never'):
            raise ValueError("'response_required' should be either 'always' or 'never'; "
                             f"you provided '{response_required}'.")

        # Figure out the target for this Event
        if target is None and targets is None and targets_by_type is None:
            targets = [{'ven_id': ven_id}]
        elif target is not None:
            targets = [target]
        elif targets_by_type is not None:
            targets = utils.ungroup_targets_by_type(targets_by_type)
        if not isinstance(targets, list):
            targets = [targets]
        if signal_type not in enums.SIGNAL_TYPE.values:
            raise ValueError(f"""The signal_type must be one of '{"', '".join(enums.SIGNAL_TYPE.values)}', """
                             f"""you specified: '{signal_type}'.""")
        if signal_name not in enums.SIGNAL_NAME.values and not signal_name.startswith('x-'):
            raise ValueError(f"""The signal_name must be one of '{"', '".join(enums.SIGNAL_TYPE.values)}', """
                             f"""or it must begin with 'x-'. You specified: '{signal_name}'""")
        if not intervals or not isinstance(intervals, (list, tuple)) or len(intervals) == 0:
            raise ValueError(f"The intervals must be a list of intervals, you specified: {intervals}")

        event_descriptor = objects.EventDescriptor(event_id=event_id,
                                                   modification_number=0,
                                                   market_context=market_context,
                                                   event_status="far",
                                                   created_date_time=datetime.now(timezone.utc))
        event_signal = objects.EventSignal(intervals=intervals,
                                           signal_name=signal_name,
                                           signal_type=signal_type,
                                           signal_id=utils.generate_id())

        # Make sure the intervals carry timezone-aware timestamps
        for interval in intervals:
            if utils.getmember(interval, 'dtstart').tzinfo is None:
                utils.setmember(interval, 'dtstart',
                                utils.getmember(interval, 'dtstart').astimezone(timezone.utc))
                logger.warning("You supplied a naive datetime object to your interval's dtstart. "
                               "This will be interpreted as a timestamp in your local timezone "
                               "and then converted to UTC before sending. Please supply timezone-"
                               "aware timestamps like datetime.datetime.new(timezone.utc) or "
                               "datetime.datetime(..., tzinfo=datetime.timezone.utc)")
        active_period = utils.get_active_period_from_intervals(intervals, False)
        active_period.ramp_up_period = ramp_up_period
        active_period.notification_period = notification_period
        active_period.recovery_period = recovery_period
        event = objects.Event(active_period=active_period,
                              event_descriptor=event_descriptor,
                              event_signals=[event_signal],
                              targets=targets,
                              response_required=response_required)
        self.add_raw_event(ven_id=ven_id, event=event, callback=callback)
        return event_id

    def add_raw_event(self, ven_id, event, callback=None):
        """
        Add a new event to the queue for a specific VEN.
        :param str ven_id: The ven_id to which this event should be distributed.
        :param dict event: The event (as a dict or as a objects.Event instance)
                           that contains the event details.
        :param callable callback: A callback that will receive the opt status for this event.
                                  This callback receives ven_id, event_id, opt_type as its arguments.
        """
        if utils.getmember(event, 'response_required') == 'always':
            if callback is None:
                logger.warning("You did not provide a 'callback', which means you won't know if the "
                               "VEN will opt in or opt out of your event. You should consider adding "
                               "a callback for this.")
            elif not asyncio.isfuture(callback):
                args = inspect.signature(callback).parameters
                if not all(['ven_id' in args, 'event_id' in args, 'opt_type' in args]):
                    raise ValueError("The 'callback' must have at least the following parameters: "
                                     "'ven_id' (str), 'event_id' (str), 'opt_type' (str). Please fix "
                                     "your 'callback' handler.")

        event_id = utils.getmember(event, 'event_descriptor.event_id')
        # Create the event queue if it does not exist yet
        if ven_id not in self.events:
            self.events[ven_id] = []

        # Add event to the queue
        self.events[ven_id].append(event)
        self.events_updated[ven_id] = True

        # Add the callback for the response to this event
        if callback is not None:
            self.event_callbacks[event_id] = (event, callback)
        return event_id

    def cancel_event(self, ven_id, event_id):
        """
        Mark the indicated event as cancelled.
        """
        event = utils.find_by(self.events[ven_id], 'event_descriptor.event_id', event_id)
        if not event:
            logger.error("""The event you tried to cancel was not found. """
                         """Was looking for event_id {event_id} for ven {ven_id}."""
                         """Only found these: [getmember(e, 'event_descriptor.event_id')
                                               for e in self.events[ven_id]]""")
            return

        # Set the Event Status to cancelled
        utils.setmember(event, 'event_descriptor.event_status', enums.EVENT_STATUS.CANCELLED)
        utils.increment_event_modification_number(event)
        self.events_updated[ven_id] = True

    def add_handler(self, name, func):
        """
        Add a handler to the OpenADRServer.

        :param str name: The name for this handler. Should be one of: on_created_event,
                            on_request_event, on_register_report, on_create_report,
                            on_created_report, on_request_report, on_update_report, on_poll,
                            on_query_registration, on_create_party_registration,
                            on_cancel_party_registration.
        :param callable func: A function or coroutine that handles this type of occurrence.
                              It receives the message, and should return the contents of a response.
        """
        logger.debug(f"Adding handler: {name} {func}")
        if name in self._MAP:
            setattr(self.services[self._MAP[name]], name, func)
            if name == 'on_poll':
                self.services['poll_service'].polling_method = 'external'
                self.services['event_service'].polling_method = 'external'
        else:
            raise NameError(f"""Unknown handler '{name}'. """
                            f"""Correct handler names are: '{"', '".join(self._MAP.keys())}'.""")

    @property
    def registered_reports(self):
        return self.services['report_service'].registered_reports

    @property
    def events(self):
        return self.services['event_service'].events

    @property
    def events_updated(self):
        return self.services['poll_service'].events_updated

    @property
    def event_callbacks(self):
        return self.services['event_service'].event_callbacks
