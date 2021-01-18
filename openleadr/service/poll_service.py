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

from openleadr.service import service, handler, VTNService
from openleadr import objects
import asyncio
from dataclasses import asdict
import logging
logger = logging.getLogger('openleadr')

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                             POLLING SERVICE                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# oadrPoll is a service independent polling mechanism used by VENs in a PULL
# model to request pending service operations from the VTN. The VEN queries
# the poll endpoint and the VTN re- sponds with the same message that it would
# have “pushed” had it been a PUSH VEN. If there are multiple messages pending
# a “push,” the VEN will continue to query the poll endpoint until there are
# no new messages and the VTN responds with an eiResponse payload.
#
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can poll for any messages that we have for them. If we have no   │
# │ (more) messages, we send a generic oadrResponse:                         │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrResponse() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ If we have an Event, we expect the following:                            │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ oadrCreateEvent() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │───────────────────────oadrCreatedEvent()───────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrResponse() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ For Reports:                                                             │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrCreateReport() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │───────────────────────oadrCreatedReport()──────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrResponse() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ If re-registration is neccessary:                                        │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrRequestReregistration()─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │─────────────────────────oadrResponse()─────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ HTTP 200─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# │   │──────────────────oadrCreatePartyRegistration()─────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrRequestReregistration()─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘


@service('OadrPoll')
class PollService(VTNService):

    def __init__(self, vtn_id, polling_method='internal', event_service=None, report_service=None):
        super().__init__(vtn_id)
        self.polling_method = polling_method
        self.events_updated = {}
        self.report_requests = {}
        self.event_service = event_service
        self.report_service = report_service

    @handler('oadrPoll')
    async def poll(self, payload):
        """
        Handle the request to the oadrPoll service. This either calls a previously registered
        `on_poll` handler, or it retrieves the next message from the internal queue.
        """
        if self.polling_method == 'external':
            result = self.on_poll(ven_id=payload['ven_id'])
        elif self.events_updated.get(payload['ven_id']):
            # Send a oadrDistributeEvent whenever the events were updated
            result = await self.event_service.request_event({'ven_id': payload['ven_id']})
            self.events_updated[payload['ven_id']] = False
        else:
            return 'oadrResponse', {}

        if asyncio.iscoroutine(result):
            result = await result
        if result is None:
            return 'oadrResponse', {}
        if isinstance(result, tuple):
            return result
        if isinstance(result, list):
            return 'oadrDistributeEvent', result
        if isinstance(result, dict) and 'event_descriptor' in result:
            return 'oadrDistributeEvent', {'events': [result]}
        if isinstance(result, objects.Event):
            return 'oadrDistributeEvent', {'events': [asdict(result)]}
        logger.warning(f"Could not determine type of message in response to oadrPoll: {result}")
        return 'oadrResponse', result

    def on_poll(self, ven_id):
        """
        Placeholder for the on_poll handler.
        """
        logger.warning("You should implement and register your own on_poll handler that "
                       "returns the next message for the VEN. This handler receives the "
                       "ven_id as its argument, and should return None (if no messages "
                       "are available), an Event or list of Events, a RequestReregistration "
                       " or RequestReport.")
        return None
