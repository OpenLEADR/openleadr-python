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
from asyncio import iscoroutine
from .. import objects
import logging
logger = logging.getLogger('openleadr')


@service('EiEvent')
class EventService(VTNService):

    def __init__(self, vtn_id, polling_method='internal', message_queues=None):
        super().__init__(vtn_id)
        self.polling_method = polling_method
        self.message_queues = message_queues
        self.pending_events = {}        # Holds the event callbacks

    @handler('oadrRequestEvent')
    async def request_event(self, payload):
        """
        The VEN requests us to send any events we have.
        """
        result = self.on_request_event(payload['ven_id'])
        if iscoroutine(result):
            result = await result
        if result is None:
            return 'oadrDistributeEvent', {'events': []}
        if isinstance(result, dict):
            return 'oadrDistributeEvent', {'events': [result]}
        if isinstance(result, objects.Event):
            return 'oadrDistributeEvent', {'events': [result]}
        if isinstance(result, list):
            return 'oadrDistributeEvent', {'events': result}
        else:
            raise TypeError("Event handler should return None, a dict or a list")

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
        if self.polling_method == 'internal':
            for event_response in payload['event_responses']:
                if event_response['event_id'] in self.pending_events:
                    callback = self.pending_events.pop(event_response['event_id'])
                    result = callback(event_response['opt_type'])
                    if iscoroutine(result):
                        result = await result
        else:
            result = self.on_created_event(payload)
            if iscoroutine(result):
                result = await(result)
        return 'oadrResponse', {}

    def on_created_event(self, payload):
        """
        Placeholder for the on_created_event handler.
        """
        logger.warning("You should implement and register you own on_created_event handler "
                       "to receive the opt status for an Event that you sent to the VEN. This "
                       "handler will receive a ven_id, event_id and opt_status. "
                       "You don't need to return anything from this handler.")
        return None
