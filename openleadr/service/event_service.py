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
from datetime import datetime, timedelta, timezone
from asyncio import iscoroutine

@service('EiEvent')
class EventService(VTNService):

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
        if isinstance(result, list):
            return 'oadrDistributeEvent', {'events': result}
        else:
            raise TypeError("Event handler should return None, a dict or a list")

    @handler('oadrCreatedEvent')
    async def created_event(self, payload):
        """
        The VEN informs us that they created an EiEvent.
        """
        result = self.on_created_event(payload)
        if iscoroutine(result):
            result = await(result)
        return result
