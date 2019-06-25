from . import api, handler, VTNService
from asyncio import iscoroutine

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                             POLLING SERVICE                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# oadrPoll is a service independent polling mechanism used by VENs in a PULL
# model to request pending service operations from the VTN. The VEN queries
# the poll endpoint and the VTN re- sponds with the same message that it would
# have “pushed” had it been a PUSH VEN. If there are multiple messages pending
# a “push,” the VEN will continue to query the poll endpoint until there are
# no new messages and the VTN responds with an eiResponse payload.
#
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ The VEN can poll for any messages that we have for them. If we have no   │
# │ (more) messages, we send a generic oadrResponse:                         │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrResponse() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ If we have an Event, we expect the following:                            │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ oadrCreateEvent() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │───────────────────────oadrCreatedEvent()───────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrResponse() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ For Reports:                                                             │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrCreateReport() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │───────────────────────oadrCreatedReport()──────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrResponse() ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘
# ┌──────────────────────────────────────────────────────────────────────────┐
# │ If re-registration is neccessary:                                        │
# │                                                                          │
# │ ┌────┐                                                            ┌────┐ │
# │ │VEN │                                                            │VTN │ │
# │ └─┬──┘                                                            └─┬──┘ │
# │   │───────────────────────────oadrPoll()───────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrRequestReregistration()─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │   │─────────────────────────oadrResponse()─────────────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ HTTP 200─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# │   │──────────────────oadrCreatePartyRegistration()─────────────────▶│    │
# │   │                                                                 │    │
# │   │◀ ─ ─ ─ ─ ─ ─ ─ ─ ─oadrRequestReregistration()─ ─ ─ ─ ─ ─ ─ ─ ─ ─│    │
# │   │                                                                 │    │
# │                                                                          │
# └──────────────────────────────────────────────────────────────────────────┘

@api.route('/OpenADR2/Simple/2.0b/OadrPoll')
class PollService(VTNService):

    @handler('oadrPoll')
    async def poll(self, payload):
        """
        Retrieve the messages that we have for this VEN in order.

        The backend get_next_message
        """
        result = self.on_poll(ven_id=payload['ven_id'])
        if iscoroutine(result):
            result = await result
        return result
