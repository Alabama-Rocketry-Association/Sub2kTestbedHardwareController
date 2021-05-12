import websockets as ws
import asyncio
from queue import LifoQueue as Stack
import logging
import pickle

global LOGGER
LOGGER = logging.getLogger()

def fcmd(mode):
    return {"cmd":mode}

class NetworkClient(object):

    """
    NETWORK CLIENT FOR PC CONTROLLER

    """

    def __init__(self, target):
        self.target = target
        self.RECV = Stack(maxsize=4096)
        self.SEND = Stack(maxsize=4096)

    def send(self, data):
        """
        send a cmd object to send buffer
        :param CMD:
        :return:
        """
        self.SEND.put_nowait(pickle.dumps(data))

    def recv(self):
        if not self.RECV.empty():
            return pickle.loads(self.RECV.get_nowait())
        else:
            return None

    async def _recv(self, websocket):
        data = await websocket.recv()
        self.RECV.put_nowait(data)

    async def _send(self, websocket):
        if not self.SEND.empty():
            s = self.SEND.get_nowait()
            if s != None:
                await websocket.send(s)
            else:
                #let recv finish first
                await asyncio.sleep(0.1)

    async def clienthandler(self):
        while 1:
            try:
                async with ws.connect(self.target) as websocket:
                    while 1:
                        recv = asyncio.ensure_future(self._recv(websocket))
                        send = asyncio.ensure_future(self._send(websocket))
                        done, pending = await asyncio.wait(
                            [send, recv],
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        for task in pending:
                            task.cancel()
            except BaseException as e:
                LOGGER.debug(e)
            #sleep for reconnection
            await asyncio.sleep(0.5)


class NetworkServer(object):
    """
        HARDWARE CONTROLLER WEBSOCKETS SERVER for DATA AND COMMAND COMMUNICATION
    """
    def __init__(self):
        LOGGER.debug(f"{self}")
        self.SEND = Stack(maxsize=256)
        self.RECV = Stack(maxsize=256)

    def send(self, data):
        self.SEND.put_nowait(pickle.dumps(data))

    def recv(self):
        if not self.RECV.empty():
            return pickle.loads(self.RECV.get_nowait())
        return None

    async def _recv(self, websocket, path):
        cmd = await websocket.recv()
        self.RECV.put_nowait(cmd)

    async def _send(self, websocket, path):
        if not self.SEND.empty():
            s = self.SEND.get_nowait()
            if s != None:
                await websocket.send(s)
            else:
                #let _recv finish first if empty
                await asyncio.sleep(0.5)

    async def serverhandler(self, websocket, path):
        while 1:
            recv = asyncio.ensure_future(self._send(websocket, path))
            send = asyncio.ensure_future(self._recv(websocket, path))
            done, pending = await asyncio.wait(
                [send, recv],
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()

class Test:

    def __init__(self, net, c):
        self.net = net
        if c == "n":
            self.send = net.cmd
            self.recv = net.data
        else:
            self.send = net.data
            self.recv = net.cmd

    async def loop(self):
        while 1:

            self.send("hi")
            print(self.recv())

            await asyncio.sleep(10)

if __name__ == "__main__":

    v = input("server?")
    if v == "y":
        n = NetworkServer()
        t = Test(n, v)
        l = asyncio.get_event_loop()
        l.run_until_complete(asyncio.gather(*[ws.serve(n.handler, "localhost", 4444), t.loop()]))
        l.run_forever()
    if v == "n":
        uri = "ws://raspberrypi.local:4444"
        n = NetworkClient(uri)
        t = Test(n, v)
        l = asyncio.get_event_loop()
        l.run_until_complete(asyncio.gather(*[n.clienthandler(), t.loop()]))
