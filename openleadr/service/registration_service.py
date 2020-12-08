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
import logging
logger = logging.getLogger('openleadr')

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                           REGISTRATION SERVICE                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can explore some information about the VTN:                      │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │─────────────────────oadrQueryRegistration()────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ oadrCreatedPartyRegistration(VTN Info)─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can then go on and register with the VTN                         │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────oadrCreatePartyRegistration(VEN Info)────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ oadrCreatedPartyRegistration(VTN Info, registrationID)─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can also choose to cancel the registration                       │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │──────────oadrCancelPartyRegistration(registrationID)───────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─oadrCanceledPartyRegistration()─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘


@service('EiRegisterParty')
class RegistrationService(VTNService):

    def __init__(self, vtn_id, poll_freq):
        super().__init__(vtn_id)
        self.poll_freq = poll_freq

    @handler('oadrQueryRegistration')
    async def query_registration(self, payload):
        """
        Return the profiles we support.
        """
        if hasattr(self, 'on_query_registration'):
            result = self.on_query_registration(payload)
            if iscoroutine(result):
                result = await result
            return result

        # If you don't provide a default handler, just give out the info
        response_payload = {'request_id': payload['request_id'],
                            'profiles': [{'profile_name': '2.0b',
                                          'transports': [{'transport_name': 'simpleHttp'}]}],
                            'requested_oadr_poll_freq': self.poll_freq}
        return 'oadrCreatedPartyRegistration', response_payload

    @handler('oadrCreatePartyRegistration')
    async def create_party_registration(self, payload):
        """
        Handle the registration of a VEN party.
        """
        result = self.on_create_party_registration(payload)
        if iscoroutine(result):
            result = await result

        if result is not False and result is not None:
            if len(result) != 2:
                logger.error("Your on_create_party_registration handler should return either "
                             "'False' (if the client is rejected) or a (ven_id, registration_id) "
                             "tuple. Will REJECT the client for now.")
                response_payload = {}
            else:
                ven_id, registration_id = result
                transports = [{'transport_name': payload['transport_name']}]
                response_payload = {'ven_id': result[0],
                                    'registration_id': result[1],
                                    'profiles': [{'profile_name': payload['profile_name'],
                                                  'transports': transports}],
                                    'requested_oadr_poll_freq': self.poll_freq}
        else:
            transports = [{'transport_name': payload['transport_name']}]
            response_payload = {'profiles': [{'profile_name': payload['profile_name'],
                                              'transports': transports}],
                                'requested_oadr_poll_freq': self.poll_freq}
        return 'oadrCreatedPartyRegistration', response_payload

    def on_create_party_registration(self, payload):
        """
        Placeholder for the on_create_party_registration handler
        """
        logger.warning("You should implement and register your own on_create_party_registration "
                       "handler if you want VENs to be able to connect to you. This handler will "
                       "receive a registration request and should return either 'False' (if the "
                       "registration is denied) or a (ven_id, registration_id) tuple if the "
                       "registration is accepted.")
        return False

    @handler('oadrCancelPartyRegistration')
    async def cancel_party_registration(self, payload):
        """
        Cancel the registration of a party.
        """
        result = self.on_cancel_party_registration(payload)
        if iscoroutine(result):
            result = await result
        return result

    def on_cancel_party_registration(self, ven_id):
        """
        Placeholder for the on_cancel_party_registration handler.
        """
        logger.warning("You should implement and register your own on_cancel_party_registration "
                       "handler that allown VENs to deregister from your VTN. This will receive a "
                       "ven_id as its argument. You don't need to return anything.")
        return None
