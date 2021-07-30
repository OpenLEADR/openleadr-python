# from logging import debug, exception
# from flask import Flask, request
# import asyncio
# import threading
# import logging
# from flask.wrappers import Response
# import nest_asyncio
# import json
# from openleadr.client import OpenADRClient
# nest_asyncio.apply()
# client = OpenADRClient(
#     ven_name='myven', vtn_url='http://127.0.0.1:8080/OpenADR2/Simple/2.0b')
# app = Flask(__name__)

# logger = logging.getLogger('openleadr')


# @app.route('/create_party_registration', methods=['POST'])
# async def create_party_registration():
#     print(client.ven_id)
#     await client.create_party_registration()
#     print(client.ven_id)
#     if not client.ven_id:
#         logger.error("No VEN ID received from the VTN, aborting.")
#         await client.stop()
#         return
#     return {'status': 200, 'body': 'return from the create party registration'}


# @app.route('/query_registration', methods=['POST'])
# async def query_registration():
#     await client.query_registration()
#     await client.create_party_registration()
#     return {'status': 200, 'body': 'return from the query registration'}


# @app.route('/cancel_party_registration', methods=['POST'])
# async def cancel_party_registration():
#     await client.cancel_party_registration()
#     return {'status': 200, 'body': 'return from the cancel registration'}
# print(client.ven_id, client.registration_id)
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(asyncio.new_event_loop())
# asyncio.get_event_loop()
# a1 = loop.create_task(await client.cancel_party_registration())
# loop.run_until_complete(a1)
# print("after cancel")
# print(client.ven_id, client.registration_id)
# return {'status': 200, 'body': 'return from the cancel registration'}


# @app.route('/OadrPoll', methods=['POST'])
# async def client_run():
#     await client.run()
#     return {'status': 200, 'body': 'return from the oadr poll'}


# if __name__ == "__main__":
#     app.run()


from logging import debug, exception
from flask import Flask, request
import asyncio
import threading
import ssl
import aiohttp
import nest_asyncio
import json
from openleadr.client import OpenADRClient
nest_asyncio.apply()
client = OpenADRClient(
    ven_name='myven', vtn_url='http://127.0.0.1:8080/OpenADR2/Simple/2.0b')
app = Flask(__name__)


@app.route('/home')
def home():
    return "Hello from the flask!"


@app.route('/create_party_registration', methods=['GET'])
async def create_party_registration():
    # await client.create_party_registration()
    return {'status': 200, 'body': 'return from the create party registration'}


# @app.route('/create_opt', methods=['POST'])
# async def create_opt():
#     eventBody = json.loads(request.data)
#     print(eventBody)
#     return await client.create_opt(eventBody)


# @app.route('/cancel_opt', methods=['POST'])
# async def cancel_opt():
#     eventBody = json.loads(request.data)
#     print(eventBody)
#     return await client.cancel_opt(eventBody)


# def client_run():
#     loop = asyncio.new_event_loop()
#     loop.create_task(client.run())
#     loop.run_forever()


if __name__ == "__main__":
    t1 = threading.Thread(target=app.run)
    #t2 = threading.Thread(target=client_run)
    t1.start()
    # t2.start()
