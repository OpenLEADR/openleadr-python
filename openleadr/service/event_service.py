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
from openleadr import utils, errors, enums
import logging
logger = logging.getLogger('openleadr')


@service('EiEvent')
class EventService(VTNService):

    def __init__(self, vtn_id, polling_method='internal'):
        super().__init__(vtn_id)
        self.polling_method = polling_method
        self.events = {}
        self.completed_event_ids = {}   # Holds the ids of completed events
        self.event_callbacks = {}
        self.event_opt_types = {}

    @handler('oadrRequestEvent')
    async def request_event(self, payload):
        """
        The VEN requests us to send any events we have.
        """
        ven_id = payload['ven_id']
        if self.polling_method == 'internal':
            if ven_id in self.events and self.events[ven_id]:
                events = utils.order_events(self.events[ven_id])
                for event in events:
                    event_status = utils.getmember(event, 'event_descriptor.event_status')
                    # Pop the event from the events so that this is the last time it is communicated
                    if event_status == enums.EVENT_STATUS.COMPLETED:
                        self.events[ven_id].pop(self.events[ven_id].index(event))
            else:
                events = None
        else:
            result = self.on_request_event(ven_id=payload['ven_id'])
            if asyncio.iscoroutine(result):
                result = await result
            if result is None:
                events = None
            else:
                events = utils.order_events(result)

        if events is None:
            return 'oadrResponse', {}
        else:
            return 'oadrDistributeEvent', {'events': events}
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
                modification_number = event_response['modification_number']
                opt_type = event_response['opt_type']
                event = utils.find_by(self.events[ven_id],
                                      'event_descriptor.event_id', event_id,
                                      'event_descriptor.modification_number', modification_number)
                if not event:
                    if event_id not in self.completed_event_ids.get(ven_id, []):
                        logger.warning(f"""Got an oadrCreatedEvent message from ven '{ven_id}' """
                                       f"""for event '{event_id}' with modification number """
                                       f"""{modification_number} that does not exist.""")
                        raise errors.InvalidIdError
                # Remove the event from the events list if the cancellation is confirmed.
                if utils.getmember(event, 'event_descriptor.event_status') == enums.EVENT_STATUS.CANCELLED:
                    utils.pop_by(self.events[ven_id], 'event_descriptor.event_id', event_id)
                if event_response['event_id'] in self.event_callbacks:
                    event, callback = self.event_callbacks.pop(event_id)
                    if isinstance(callback, asyncio.Future):
                        if callback.done():
                            logger.warning(f"Got a second response '{opt_type}' from ven '{ven_id}' "
                                           f"to event '{event_id}', which we cannot use because the "
                                           "callback future you provided was already completed during "
                                           "the first response.")
                        else:
                            callback.set_result(opt_type)
                    else:
                        result = callback(ven_id=ven_id, event_id=event_id, opt_type=opt_type)
                        if asyncio.iscoroutine(result):
                            result = await result
        else:
            for event_response in payload['event_responses']:
                event_id = event_response['event_id']
                opt_type = event_response['opt_type']
                result = await utils.await_if_required(self.on_created_event(ven_id=ven_id,
                                                                             event_id=event_id,
                                                                             opt_type=opt_type))
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
