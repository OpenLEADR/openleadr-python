from logging import debug, exception
from flask import Flask, request
import asyncio
import threading
import ssl
import aiohttp
import nest_asyncio
import json
from openleadr.client import OpenADRClient
from openleadr.utils import report_callback
from openleadr.enums import MEASUREMENTS
nest_asyncio.apply()
client = OpenADRClient(ven_name='myven', vtn_url='http://127.0.0.1:8080/OpenADR2/Simple/2.0b')
client.add_report(report_callback, client.ven_id, report_name = 'TELEMETRY_STATUS')
client.add_report(report_callback, client.ven_id, report_name = 'TELEMETRY_USAGE', measurement= MEASUREMENTS.POWER_REAL)
app = Flask(__name__)


@app.route('/home')
def home():
    return "Hello from the flask!"


@app.route('/create_party_registration', methods=['POST', 'GET'])
async def create_party_registration():
    await client.create_party_registration(ven_id = client.ven_id, registration_id=client.registration_id)
    return {'status': 200, 'body': 'return from the create party registration'}

@app.route('/create_party_registration_while_registered', methods=['POST', 'GET'])
async def create_party_registration_while_registered():
    await client.create_party_registration_while_registered()
    return {'status': 200, 'body': 'return from the create party registration'}

@app.route('/query_registration', methods=['POST'])
async def query_registration():
    await client.query_registration()
    return {'status': 200, 'body': 'return from the query registration'}

@app.route('/cancel_party_registration', methods=['POST'])
async def cancel_party_registration():
    await client.cancel_party_registration()
    return {'status': 200, 'body': 'return from the cancel registration'}

@app.route('/register_reports')
async def register_reports():
    if client.reports:
        await client.register_reports(client.reports)
    return {'status': 200, 'body': 'The VEN has sent register report with metadata.'}

@app.route('/request_event', methods=['POST'])
async def request_event():
    response_type, response_payload = await client.request_event()
    if response_type == 'oadrDistributeEvent':
        if 'events' in response_payload and len(response_payload['events']) > 0:
                await client._on_event(response_payload)
    return {'status': 200, 'body': 'return from the request event'}


@app.route('/create_opt', methods =['POST'])
async def create_opt():
   return await client.create_opt(request.data)

@app.route('/cancel_opt', methods = ['POST'])
async def cancel_opt():
   return await client.cancel_opt(request.data)



def client_run():
    loop = asyncio.new_event_loop()
    loop.create_task(client.run())
    loop.run_forever()


if __name__ == "__main__":
    t1 = threading.Thread(target=app.run)
    t2 = threading.Thread(target=client_run)
    t1.start()
    t2.start()
    t2.join()