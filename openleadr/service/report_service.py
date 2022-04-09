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

    def __init__(self, vtn_id):
        super().__init__(vtn_id)
        self.report_callbacks = {}
        self.registered_reports = {}
        self.requested_reports = {}
        self.created_reports = {}

    @handler('oadrRegisterReport')
    async def register_report(self, payload):
        """
        Handle the VENs reporting capabilities.
        """
        report_requests = []
        args = inspect.signature(self.on_register_report).parameters
        if all(['ven_id' in args, 'resource_id' in args, 'measurement' in args,
                'min_sampling_interval' in args, 'max_sampling_interval' in args,
                'unit' in args, 'scale' in args]):
            mode = 'compact'
        else:
            mode = 'full'

        if payload['reports'] is None:
            return

        for report in payload['reports']:
            if payload['ven_id'] not in self.registered_reports:
                self.registered_reports[payload['ven_id']] = []

            report_copy = report.copy()
            report_copy['report_name'] = report_copy['report_name'][9:]
            self.registered_reports[payload['ven_id']].append(report_copy)

            if report['report_name'] == 'METADATA_TELEMETRY_STATUS':
                if mode == 'compact':
                    results = [self.on_register_report(ven_id=payload['ven_id'],
                                                       resource_id=rd.get('report_data_source', {}).get('resource_id'),
                                                       measurement='Status',
                                                       unit=None,
                                                       scale=None,
                                                       min_sampling_interval=rd['sampling_rate']['min_period'],
                                                       max_sampling_interval=rd['sampling_rate']['max_period'])
                               for rd in report['report_descriptions']]
                    results = await utils.gather_if_required(results)
                elif mode == 'full':
                    results = await utils.await_if_required(self.on_register_report(report))
            elif report['report_name'] == 'METADATA_TELEMETRY_USAGE':
                if mode == 'compact':
                    results = [self.on_register_report(ven_id=payload['ven_id'],
                                                       resource_id=rd.get('report_data_source', {}).get('resource_id'),
                                                       measurement=rd['measurement']['description'],
                                                       unit=rd['measurement']['unit'],
                                                       scale=rd['measurement']['scale'],
                                                       min_sampling_interval=rd['sampling_rate']['min_period'],
                                                       max_sampling_interval=rd['sampling_rate']['max_period'])
                               for rd in report['report_descriptions']]
                    results = await utils.gather_if_required(results)
                elif mode == 'full':
                    results = await utils.await_if_required(self.on_register_report(report))
            elif report['report_name'] in ('METADATA_HISTORY_USAGE', 'METADATA_HISTORY_GREENBUTTON'):
                report_requests.append(None)
                continue
            else:
                logger.warning("Reports other than TELEMETRY_USAGE, TELEMETRY_STATUS, "
                               "HISTORY_USAGE and HISTORY_GREENBUTTON are not yet supported. "
                               f"Skipping report with name {report['report_name']}.")
                report_requests.append(None)
                continue

            # Perform some rudimentary checks on the returned type
            if results is not None:
                if not isinstance(results, list):
                    logger.error("Your on_register_report handler must return a list of tuples or None; "
                                 f"it returned '{results}' ({results.__class__.__name__}).")
                    results = None
                else:
                    for i, r in enumerate(results):
                        if r is None:
                            continue
                        if not isinstance(r, tuple):
                            if mode == 'compact':
                                logger.error("Your on_register_report handler must return a tuple or None; "
                                             f"it returned '{r}' ({r.__class__.__name__}).")
                            elif mode == 'full':
                                logger.error("Your on_register_report handler must return a list of tuples or None; "
                                             f"The first item from the list was '{r}' ({r.__class__.__name__}).")
                            results[i] = None
                    # If we used compact mode, prepend the r_id to each result
                    # (this is already there when using the full mode)
                    if mode == 'compact':
                        results = [(report['report_descriptions'][i]['r_id'], *results[i])
                                   for i in range(len(report['report_descriptions'])) if isinstance(results[i], tuple)]
            report_requests.append(results)
        utils.validate_report_request_tuples(report_requests, mode=mode)

        for i, report_request in enumerate(report_requests):
            if report_request is None or len(report_request) == 0 or all(rrq is None for rrq in report_request):
                continue
            # Check if all sampling rates per report_request are the same
            sampling_interval = min(rrq[2] for rrq in report_request if isinstance(rrq, tuple))
            if not all(rrq is not None and report_request[0][2] == sampling_interval for rrq in report_request):
                logger.error("OpenADR does not support multiple different sampling rates per "
                             "report. OpenLEADR will set all sampling rates to "
                             f"{sampling_interval}")

        # Form the report request
        oadr_report_requests = []
        for i, report_request in enumerate(report_requests):
            if report_request is None or len(report_request) == 0 or all(rrq is None for rrq in report_request):
                continue

            orig_report = payload['reports'][i]
            report_specifier_id = orig_report['report_specifier_id']
            report_request_id = utils.generate_id()
            specifier_payloads = []
            for rrq in report_request:
                if len(rrq) == 3:
                    r_id, callback, sampling_interval = rrq
                    report_interval = sampling_interval
                elif len(rrq) == 4:
                    r_id, callback, sampling_interval, report_interval = rrq

                report_description = utils.find_by(orig_report['report_descriptions'], 'r_id', r_id)
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

        # Store the requested reports
        self.requested_reports[payload['ven_id']] = oadr_report_requests
        return response_type, response_payload

    async def on_register_report(self, payload):
        """
        Pre-handler for a oadrOnRegisterReport message. This will call your own handler (if defined)
        to allow for requesting the offered reports.
        """
        logger.warning("You should implement and register your own on_register_report handler "
                       "if you want to receive reports from a VEN. This handler will receive the "
                       "following arguments: ven_id, resource_id, measurement, unit, scale, "
                       "min_sampling_interval, max_sampling_interval and should return either "
                       "None or (callback, sampling_interval) or "
                       "(callback, sampling_interval, reporting_interval).")
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
            for r_id, values in utils.group_by(report['intervals'], 'report_payload.r_id').items():
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

    @handler('oadrCreatedReport')
    async def created_report(self, payload):
        """
        Handle the confirmation that a report was created.
        """
        if not hasattr(self, 'on_created_report'):
            logger.info(f"""VEN {payload['ven_id']} created reports with reportRequestIDs """
                        f"""'{"', '".join([r['request_id'] for r in payload['pending_reports']])}'.""")
        else:
            await utils.await_if_required(self.on_created_report(payload))

    async def on_created_report(self, payload):
        """
        Implementation of the on_created_report handler, may be overwritten by the user.
        """
        ven_id = payload['ven_id']
        if payload['ven_id'] not in self.created_reports:
            self.created_reports[ven_id] = []

        if payload.get('pending_reports'):
            for pending_report in payload.get('pending_reports', []):
                self.created_reports[ven_id].append(pending_report['report_request_id'])

        # Check if all requested reports were created
        for requested_report in self.requested_reports[ven_id]:
            if requested_report.report_request_id not in self.created_reports[ven_id]:
                logger.warning(f"The requested report with id {requested_report.report_request_id} "
                               "was not created by the VEN. Yoy may want to contact the VEN to "
                               "determine the problem. The requested reports was: \n"
                               f"{requested_report}")
