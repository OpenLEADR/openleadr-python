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
from asyncio import iscoroutine, gather
from openleadr.utils import generate_id
from openleadr import objects
import logging
logger = logging.getLogger('openleadr')

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                              REPORT SERVICE                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can register its reporting capabilities.                         │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────oadrRegisterReport(METADATA Report)──────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─oadrRegisteredReport(optional oadrReportRequest) ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │                                                                 │    │
# │   │─────────────oadrCreatedReport(if report requested)─────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ oadrResponse()─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ A report can also be canceled                                            │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────oadrRegisterReport(METADATA Report)──────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─oadrRegisteredReport(optional oadrReportRequest) ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │                                                                 │    │
# │   │─────────────oadrCreatedReport(if report requested)─────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ oadrResponse()─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘


@service('EiReport')
class ReportService(VTNService):

    @handler('oadrRegisterReport')
    async def register_report(self, payload):
        """
        Handle the VENs reporting capabilities.
        """
        result = [self.on_register_report(report) for report in payload['reports']]
        if iscoroutine(result[0]):
            result = await gather(*result)

        for report_request in result:
            if report_request is not None and len(report_request) != 3:
                logger.error("Your on_register_report handler should return a "
                             "(callable, sampling_rate, [list_of_r_ids]) "
                             "tuple for the report segments you wish te receive.")


        # Form the report request
        report_requests = []
        for i, report_request in enumerate(result):
            if report_request is None:
                continue

            callable_, sampling_rate, r_ids = report_request
            orig_report = payload['reports'][i]
            report_specifier_id = payload['reports'][i]['report_specifier_id']
            report_request_id = generate_id()

            specifier_payloads = []
            for r_id in r_ids:
                report_description = [report_description for report_description
                                      in orig_report['report_descriptions']
                                      if report_description['r_id'] == r_id][0]
                reading_type = report_description['reading_type']
                specifier_payloads.append(objects.SpecifierPayload(r_id=r_id,
                                                                   reading_type=reading_type))

            report_specifier = objects.ReportSpecifier(report_specifier_id=report_specifier_id,
                                                       granularity=sampling_rate,
                                                       specifier_payloads=specifier_payloads)

            report_requests.append(objects.ReportRequest(report_request_id=report_request_id,
                                                         report_specifier=report_specifier))

        # Put the report requests back together
        response_type = 'oadrRegisteredReport'
        response_payload = {'report_requests': report_requests}
        return response_type, response_payload

    async def on_register_report(self, payload):
        """
        Pre-handler for a oadrOnRegisterReport message. This will call your own handler (if defined)
        to allow for requesting the offered reports.
        """
        logger.warning("You should implement and register your own on_register_report handler "
                       "if you want to receive reports from a VEN. This handler will receive an "
                       "oadrReport descriptor, and should return a "
                       "(callable, sampling_rate, [list_of_r_ids]) tuples for the report segments you "
                       "wish to receive. Not requesting any reports at this moment.")
        return None

    @handler('oadrUpdateReport')
    async def update_report(self, payload):
        """
        Handle a report that we received from the VEN.
        """
        result = [self.on_update_report(report) for report in payload['reports']]
        if iscoroutine(result[0]):
            result = await gather(*result)

        response_type = 'oadrUpdatedReport'
        response_payload = {}
        return response_type, response_payload

    async def on_update_report(self, payload):
        """
        Placeholder for the on_update_report handler.
        """
        logger.warning("You should implement and register your own on_update_report handler "
                       "to deal with reports that your receive from the VEN. This handler will "
                       "receive an oadrReport that you can then process how you see fit. You don't "
                       "need to return anything from that handler.")
        return None
