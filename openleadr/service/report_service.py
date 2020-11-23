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
from openleadr.utils import generate_id, find_by, group_by
from openleadr import objects
import logging
import inspect
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

    def __init__(self, vtn_id, message_queues=None):
        super().__init__(vtn_id)
        self.report_callbacks = {}
        self.message_queues = message_queues

    @handler('oadrRegisterReport')
    async def register_report(self, payload):
        """
        Handle the VENs reporting capabilities.
        """
        report_requests = []
        args = inspect.signature(self.on_register_report).parameters
        if all(['measurement' in args, 'resource_id' in args,
                'min_sampling_interval' in args, 'max_sampling_interval' in args,
                'unit' in args, 'scale' in args]):
            for report in payload['reports']:
                if report['report_name'] == 'METADATA_TELEMETRY_STATUS':
                    result = [self.on_register_report(resource_id=rd['report_subject']['resource_id'],
                                                      measurement='Status',
                                                      unit=None,
                                                      scale=None,
                                                      min_sampling_interval=rd['sampling_rate']['min_period'],
                                                      max_sampling_interval=rd['sampling_rate']['max_period'])
                              for rd in report['report_descriptions']]
                elif report['report_name'] == 'METADATA_TELEMETRY_USAGE':
                    result = [self.on_register_report(resource_id=rd['report_subject']['resource_id'],
                                                      measurement=rd['measurement']['item_description'],
                                                      unit=rd['measurement']['item_units'],
                                                      scale=rd['measurement']['si_scale_code'],
                                                      min_sampling_interval=rd['sampling_rate']['min_period'],
                                                      max_sampling_interval=rd['sampling_rate']['max_period'])
                              for rd in report['report_descriptions']]
                else:
                    logger.warning("Reports other than TELEMETRY_USAGE and TELEMETRY_STATUS are "
                                   f"not yet supported. Skipping report {report['report_name']}.")
                    report_requests.append(None)
                    break

                if iscoroutine(result[0]):
                    result = await gather(*result)
                result = [(report['report_descriptions'][i]['r_id'], *result[i])
                          for i in range(len(report['report_descriptions'])) if result[i] is not None]
                report_requests.append(result)
        else:
            # Use the 'full' mode for openADR reporting
            result = [self.on_register_report(report) for report in payload['reports']]
            if iscoroutine(result[0]):
                result = await gather(*result)      # Now we have r_id, callback, sampling_rate
            report_requests = result

        for i, report_request in enumerate(report_requests):
            if report_request is not None:
                if not all(len(rrq) in (3, 4) for rrq in report_request):
                    logger.error("Your on_register_report handler did not return a valid response")

        # Validate the report requests
        for i, report_request in enumerate(report_requests):
            if report_request is None or len(report_request) == 0:
                continue
            # Check if all sampling rates per report_request are the same
            sampling_interval = min(rrq[2] for rrq in report_request if rrq is not None)
            if not all(rrq is not None and report_request[0][2] == sampling_interval for rrq in report_request):
                logger.error("OpenADR does not support multiple different sampling rates per "
                             "report. OpenLEADR will set all sampling rates to "
                             f"{sampling_interval}")

        # Form the report request
        oadr_report_requests = []
        for i, report_request in enumerate(report_requests):
            if report_request is None:
                continue

            orig_report = payload['reports'][i]
            report_specifier_id = orig_report['report_specifier_id']
            report_request_id = generate_id()
            specifier_payloads = []
            for rrq in report_request:
                if len(rrq) == 3:
                    r_id, callback, sampling_interval = rrq
                    report_interval = sampling_interval
                elif len(rrq) == 4:
                    r_id, callback, sampling_interval, report_interval = rrq

                report_description = find_by(orig_report['report_descriptions'], 'r_id', r_id)
                reading_type = report_description['reading_type']
                specifier_payloads.append(objects.SpecifierPayload(r_id=r_id,
                                                                   reading_type=reading_type))
                # Append the callback to our list of known callbacks
                self.report_callbacks[(report_request_id, r_id)] = callback

            # Add the ReportSpecifier to the ReportRequest
            report_specifier = objects.ReportSpecifier(report_specifier_id=report_specifier_id,
                                                       granularity=sampling_interval,
                                                       report_back_duration=report_interval,
                                                       specifier_payloads=specifier_payloads)

            # Add the ReportRequest to our outgoing message
            oadr_report_requests.append(objects.ReportRequest(report_request_id=report_request_id,
                                                              report_specifier=report_specifier))

        # Put the report requests back together
        response_type = 'oadrRegisteredReport'
        response_payload = {'report_requests': oadr_report_requests}
        return response_type, response_payload

    async def on_register_report(self, payload):
        """
        Pre-handler for a oadrOnRegisterReport message. This will call your own handler (if defined)
        to allow for requesting the offered reports.
        """
        logger.warning("You should implement and register your own on_register_report handler "
                       "if you want to receive reports from a VEN. This handler will receive an "
                       "oadrReport descriptor, and should return a list of"
                       "(r_id, callback, sampling_interval) "
                       "tuples for the report segments you wish to receive. "
                       "Not requesting any reports at this moment.")
        return None

    @handler('oadrUpdateReport')
    async def update_report(self, payload):
        """
        Handle a report that we received from the VEN.
        """
        for report in payload['reports']:
            report_request_id = report['report_request_id']
            if not self.report_callbacks:
                result = self.on_update_report(report)
                if iscoroutine(result):
                    result = await result
                continue
            for r_id, values in group_by(report['intervals'], 'report_payload.r_id').items():
                # Find the callback that was registered.
                if (report_request_id, r_id) in self.report_callbacks:
                    # Collect the values
                    values = [(ri['dtstart'], ri['report_payload']['value']) for ri in values]
                    # Call the callback function to deliver the values
                    result = self.report_callbacks[(report_request_id, r_id)](values)
                    if iscoroutine(result):
                        result = await result

        response_type = 'oadrUpdatedReport'
        response_payload = {}
        return response_type, response_payload

    async def on_update_report(self, payload):
        """
        Placeholder for the on_update_report handler.
        """
        logger.warning("You should implement and register your own on_update_report handler "
                       "to deal with reports that your receive from the VEN. This handler will "
                       "receive either a complete oadrReport dict, or a list of (datetime, value) "
                       "tuples that you can then process how you see fit. You don't "
                       "need to return anything from that handler.")
        return None
