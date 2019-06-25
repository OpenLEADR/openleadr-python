from . import api, handler, VTNService

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

@api.route('/OpenADR2/Simple/2.0b/EiReport')
class ReportService(VTNService):

    @handler('oadrRegisterReport')
    async def register_report(self, payload):
        """
        Register a reporting type.
        """
        print("Called Registered Report")
        response_type = 'oadrRegisteredReport'
        response_payload = {"response": {"response_code": 200,
                                         "response_description": "OK",
                                         "request_id": payload['request_id']},
                            "ven_id": '123'}
        return response_type, response_payload

    @handler('oadrRequestReport')
    async def request_report(self, payload):
        """
        Provide the VEN with the latest report.
        """
        print("Called Request Report")

    @handler('oadrUpdateReport')
    async def update_report(self, payload):
        """
        Updates an existing report from this VEN in our database.
        """
        print("Called Update Report")

    @handler('oadrCancelReport')
    async def cancel_report(self, payload):
        """
        Cancels a previously received report from this VEN.
        """
        print("Called Cancel Report")
