from . import api, handler, VTNService
from datetime import timedelta
from asyncio import iscoroutine

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

@api.route('/OpenADR2/Simple/2.0b/EiRegisterParty')
class RegistrationService(VTNService):

    @handler('oadrQueryRegistration')
    async def query_registration(self, payload):
        """
        Return the profiles we support.
        """
        request_id = payload['request_id']
        response_type = "oadrCreatedPartyRegistration"
        response_payload = {"request_id": request_id,
                            "vtn_id": "elaadvtn",
                            "profiles": [{"profile_name": "2.0a",
                                          "transports": [{"transport_name": "simpleHttp"},
                                                          {"transport_name": "xmpp"}]},
                                         {"profile_name": "2.0b",
                                          "transports": [{"transport_name": "simpleHttp"},
                                                          {"transport_name": "xmpp"}]}],
                            "requested_oadr_poll_freq": timedelta(seconds=10)}
        return response_type, response_payload

    @handler('oadrCreatePartyRegistration')
    async def create_party_registration(self, payload):
        """
        Handle the registration of a VEN party.
        """
        result = self.on_create_party_registration(payload)
        if iscoroutine(result):
            result = await result
        return result

    @handler('oadrCancelPartyRegistration')
    async def cancel_party_registration(self, payload):
        """
        Cancel the registration of a party.
        """
        result = self.on_cancel_party_registration(payload)
        if iscoroutine(result):
            result = await result
        return result
