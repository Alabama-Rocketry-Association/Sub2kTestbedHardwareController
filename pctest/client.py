from net import NetworkClient


CLIENT = NetworkClient("ws://[fe80::e5f3:6c22:dc77:e4bc]:4444")

import asyncio 

async def loop(client_obj: NetworkClient):
    while 1:
        #client_obj.send("MOCK CMD")
        if (r := client_obj.recv()) != None:
            print(r)
        else:
            await asyncio.sleep(0.01)

eloop = asyncio.get_event_loop()
eloop.run_until_complete(
    asyncio.gather(
        *[
            CLIENT.clienthandler(),
            loop(CLIENT)
        ]
    )
)
eloop.run_forever()

