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
from openleadr import objects, utils
import logging
import inspect
logger = logging.getLogger('openleadr')

@service('EiOpt')
class OptService(VTNService):

    def __init__(self, vtn_id):
        super().__init__(vtn_id)
        self.opt_schedules = {}

    ###########################################################################
    #                                                                         #
    #                              CREATE METHODS                             #
    #                                                                         #
    ###########################################################################
    @handler('oadrCreateOpt')
    async def create_opt(self, payload):
        """
        Called when the server receives an oadrCreateOpt message.

        Payload will look like:
            {'opt_id': 'opt123', 
            'opt_type': 'optOut', 
            'opt_reason': 'emergency', 
            'market_context': 'oadr://unknown.context', 
            'ven_id': 'ven123', 
            'vavailability': {
                'components': {
                    'available': {
                        'dtstart': datetime.datetime(2024, 2, 9, 20, 22, 25, 628864, tzinfo=datetime.timezone.utc), 
                        'duration': datetime.timedelta(seconds=300)
                    }
                }
            }, 
            'created_date_time': datetime.datetime(2024, 2, 9, 20, 22, 25, 628912, tzinfo=datetime.timezone.utc), 
            'request_id': 'request123', 
            'targets': [{'ven_id': 'ven123'}], 
            'targets_by_type': {
                'ven_id': ['ven123']
            }
        }
        """
        logger.debug("Received an oadrCreateOpt message.")
        logger.debug(f"Payload: {payload}")
        result = self.on_create_opt(payload)
        if iscoroutine(result):
            result = await result

        logger.debug(f"...Result: {result}")
        return 'oadrCreatedOpt', result

    def on_create_opt(self, payload):
        """
        Manage the details of the creation of an Opt Schedule.
        """
        targets = payload.get('targets', [{'ven_id': payload.get('ven_id')}])
        for target in targets:
            key = f"{payload['opt_id']}_{target['ven_id']}"
            logger.debug(f"Adding opt schedule with key {key}")
            self.opt_schedules[key] = payload

        return {'opt_id': payload['opt_id'], 'request_id': payload['request_id']}
    
    ###########################################################################
    #                                                                         #
    #                              CANCEL METHODS                             #
    #                                                                         #
    ###########################################################################

    @handler('oadrCancelOpt')
    async def cancel_opt(self, payload):
        """
        Called when the server receives an oadrCancelOpt message.

        Opt schedules are removed from the dictionary
        Dictionary will be keyed by optId_venId
        """
        logger.debug("Received an oadrCancelOpt message.")
        logger.debug(f"Payload: {payload}")
        result = self.on_cancel_opt(payload)
        if iscoroutine(result):
            result = await result

        logger.debug(f"...Result: {result}")

        return 'oadrCanceledOpt', result
    
    def on_cancel_opt(self, payload):
        """
        Managed the details of the cancellation of an Opt Schedule.
        """
        keys_to_delete = []
        for key in self.opt_schedules.keys():
            if key.startswith(f"{payload['opt_id']}_"):
                keys_to_delete.append(key)
        for key in keys_to_delete:
            logger.debug(f"Removing opt schedule with key {key}")
            del self.opt_schedules[key]

        return {'opt_id': payload['opt_id'], 'request_id': payload['request_id']}
