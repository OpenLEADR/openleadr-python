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

from . import service, handler, VTNService
import asyncio
from openleadr import objects, utils, enums
import logging
import sys
from datetime import datetime, timezone
from functools import partial
from dataclasses import asdict
logger = logging.getLogger('openleadr')


@service('EiEvent')
class EventService(VTNService):

    def __init__(self, vtn_id, polling_method='internal', message_queues=None):
        super().__init__(vtn_id)
        self.polling_method = polling_method
        self.message_queues = message_queues
        self.pending_events = {}        # Holds the event callbacks
        self.running_events = {}        # Holds the event callbacks for accepted events

    @handler('oadrRequestEvent')
    async def request_event(self, payload):
        """
        The VEN requests us to send any events we have.
        """
        if self.polling_method == 'external':
            result = self.on_request_event(ven_id=payload['ven_id'])
            if asyncio.iscoroutine(result):
                result = await result
        elif payload['ven_id'] in self.message_queues:
            queue = self.message_queues[payload['ven_id']]
            result = utils.get_next_event_from_deque(queue)
        else:
            return 'oadrResponse', {}

        if result is None:
            return 'oadrResponse', {}
        if isinstance(result, dict) and 'event_descriptor' in result:
            return 'oadrDistributeEvent', {'events': [result]}
        elif isinstance(result, objects.Event):
            return 'oadrDistributeEvent', {'events': [asdict(result)]}

        logger.warning("Could not determine type of message "
                       f"in response to oadrRequestEvent: {result}")
        return 'oadrResponse', result

    def on_request_event(self, ven_id):
        """
        Placeholder for the on_request_event handler.
        """
        logger.warning("You should implement and register your own on_request_event handler "
                       "that returns the next event for a VEN. This handler will receive a "
                       "ven_id as its only argument, and should return None (if no events are "
                       "available), a single Event, or a list of Events.")
        return None

    @handler('oadrCreatedEvent')
    async def created_event(self, payload):
        """
        The VEN informs us that they created an EiEvent.
        """
        ven_id = payload['ven_id']
        if self.polling_method == 'internal':
            for event_response in payload['event_responses']:
                event_id = event_response['event_id']
                opt_type = event_response['opt_type']
                if event_response['event_id'] in self.pending_events:
                    event, callback = self.pending_events.pop(event_id)
                    if isinstance(callback, asyncio.Future):
                        callback.set_result(opt_type)
                    else:
                        result = callback(ven_id=ven_id, event_id=event_id, opt_type=opt_type)
                        if asyncio.iscoroutine(result):
                            result = await result
                    if opt_type == 'optIn':
                        self.running_events[event_id] = (event, callback)
                        self.schedule_event_updates(ven_id, event)
                elif event_response['event_id'] in self.running_events:
                    event, callback = self.running_events.pop(event_id)
                    if isinstance(callback, asyncio.Future):
                        logger.warning(f"Got a second response '{opt_type}' from ven '{ven_id}' "
                                       f"to event '{event_id}', which we cannot use because the "
                                       "callback future you provided was already completed during "
                                       "the first response.")
                    else:
                        result = callback(ven_id=ven_id, event_id=event_id, opt_type=opt_type)
                        if asyncio.iscoroutine(result):
                            result = await result
        else:
            result = self.on_created_event(ven_id=ven_id, event_id=event_id, opt_type=opt_type)
            if asyncio.iscoroutine(result):
                result = await(result)
        return 'oadrResponse', {}

    def on_created_event(self, ven_id, event_id, opt_type):
        """
        Placeholder for the on_created_event handler.
        """
        logger.warning("You should implement and register you own on_created_event handler "
                       "to receive the opt status for an Event that you sent to the VEN. This "
                       "handler will receive a ven_id, event_id and opt_status. "
                       "You don't need to return anything from this handler.")
        return None

    def _update_event_status(self, ven_id, event, event_status):
        """
        Update the event to the given Status.
        """
        event.event_descriptor.event_status = event_status
        if event_status == enums.EVENT_STATUS.CANCELLED:
            event.event_descriptor.modification_number += 1
        self.message_queues[ven_id].append(event)

    def schedule_event_updates(self, ven_id, event):
        """
        Schedules the event updates.
        """
        loop = asyncio.get_event_loop()
        now = datetime.now(timezone.utc)
        active_period = event.active_period

        # Named tasks is only supported in Python 3.8+
        if sys.version_info.minor >= 8:
            named_tasks = True
        else:
            named_tasks = False
            name = {}

        # Schedule status update to 'near' if applicable
        if active_period.ramp_up_period is not None and event.event_descriptor.event_status == 'far':
            ramp_up_start_delay = (active_period.dtstart - active_period.ramp_up_period) - now
            update_coro = partial(self._update_event_status, ven_id, event, 'near')
            if named_tasks:
                name = {'name': f'DelayedCall-EventStatusToNear-{event.event_descriptor.event_id}'}
            loop.create_task(utils.delayed_call(func=update_coro, delay=ramp_up_start_delay), **name)

        # Schedule status update to 'active'
        if event.event_descriptor.event_status in ('near', 'far'):
            active_start_delay = active_period.dtstart - now
            update_coro = partial(self._update_event_status, ven_id, event, 'active')
            if named_tasks:
                name = {'name': f'DelayedCall-EventStatusToActive-{event.event_descriptor.event_id}'}
            loop.create_task(utils.delayed_call(func=update_coro, delay=active_start_delay), **name)

        # Schedule status update to 'completed'
        if event.event_descriptor.event_status in ('near', 'far', 'active'):
            active_end_delay = active_period.dtstart + active_period.duration - now
            update_coro = partial(self._update_event_status, ven_id, event, 'completed')
            if named_tasks:
                name = {'name': f'DelayedCall-EventStatusToActive-{event.event_descriptor.event_id}'}
            loop.create_task(utils.delayed_call(func=update_coro, delay=active_end_delay), **name)
