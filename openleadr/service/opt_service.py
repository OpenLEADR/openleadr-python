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
import logging
logger = logging.getLogger('openleadr')

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                           OPT SERVICE                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can send an Opt-in / Opt-out schedule to the VTN:                │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrCreateOpt()──────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ oadrCreatedOpt()─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can cancel a sent Opt-in / Opt-out schedule:                │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrCancelOpt()──────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ oadrCanceledOpt()─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘


@service('EiOpt')
class OptService(VTNService):

    def __init__(self, vtn_id):
        super().__init__(vtn_id)
        self.created_opt_schedules = {}

    @handler('oadrCreateOpt')
    async def create_opt(self, payload):
        """
        Handle an opt schedule created by the VEN
        """
        ven_id = payload['ven_id']

        # payload parameters:
        # ven_id
        # opt_id
        # opt_type
        # opt_reason
        # market_context (optional)
        # array of availability components (optional):
        #   component.dstart
        #   component.duration
        # created_date_time
        # event_id (optional)
        # modification_number (optional)
        # array of eitarget (in parts folder)

        # TODO: create a handler for the ven called on_create_opt, handle and return the result (oadrCreatedOpt)

    @handler('oadrCancelOpt')
    async def cancel_opt(self, payload):
        """
        Cancel an opt schedule previously created by the VEN
        """
        ven_id = payload['ven_id']

        # payload parameters:
        # ven_id
        # opt_id

        # TODO: create a handler for the ven called on_cancel_opt, handle and return the result (oadrCanceledOpt)
