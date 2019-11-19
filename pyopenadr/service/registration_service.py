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
        if hasattr(self, 'on_query_registration'):
            result = self.on_query_registration(payload)
            if iscoroutine(result):
                result = await result
            return result

        # If you don't provide a default handler, just give out the info
        response_payload = {'response': {'response_code': 200, 'response_description': 'OK', 'request_id': payload['request_id']},
                            'request_id': payload['request_id'],
                            'vtn_id': 'ElaadVTN',
                            'profiles': [{'profile_name': '2.0b',
                                          'transports': {'transport_name': 'simpleHttp'}}],
                            'requested_oadr_poll_freq': timedelta(seconds=5)}
        return 'oadrCreatedPartyRegistration', response_payload

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
