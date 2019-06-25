from . import api, handler, VTNService
from datetime import datetime, timedelta, timezone
from asyncio import iscoroutine

@api.route('/OpenADR2/Simple/2.0b/EiEvent')
class EventService(VTNService):

    @handler('oadrRequestEvent')
    async def request_event(self, payload):
        """
        The VEN requests us to send any events we have.
        """
        # TODO: hook into some backend here to retrieve the appropriate events for this VEN.
        try:
            result = self.on_request_event(payload['ven_id'])
            if iscoroutine(result):
                result = await result
        except OpenADRError as err:
            response_type = 'oadrResponse'
            response_payload = {'request_id': payload['request_id'],
                                'response_code': err.status,
                                'response_description': err.description,
                                'ven_id': payload['ven_id']}
            return response_type, response_payload
        else:
            return result

    @handler('oadrCreatedEvent')
    async def created_event(self, payload):
        """
        The VEN informs us that they created an EiEvent.
        """
        result = self.on_created_event(payload)
        if iscoroutine(result):
            result = await(result)
        return result
