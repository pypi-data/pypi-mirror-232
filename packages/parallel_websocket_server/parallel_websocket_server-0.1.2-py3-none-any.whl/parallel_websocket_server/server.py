import asyncio
import multiprocessing as mp
from functools import partial

import websockets


async def async_get(queue: mp.Queue):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, queue.get)


class ParallelWebSocketServer:
    def __init__(
        self, receive_queue: mp.Queue, send_queue: mp.Queue, host="0.0.0.0", port=8765
    ):
        self.__host = host
        self.__port = port

        p = mp.Process(target=self.run_in_process, args=(send_queue, receive_queue))
        p.start()

    async def __sender(self, websocket, send_queue: mp.Queue):
        while True:
            message = await async_get(send_queue)
            await websocket.send(message)

    async def __handler(self, websocket, send_queue: mp.Queue, receive_queue: mp.Queue):
        # launch sender coroutine as a separate task
        asyncio.create_task(self.__sender(websocket, send_queue))

        # Asynchronously iterate over incoming messages from the WebSocket.
        # This allows the server to wait for messages without blocking the entire program.
        async for message in websocket:
            receive_queue.put(message)

    async def __start_server(self, send_queue: mp.Queue, receive_queue: mp.Queue):
        bound_handler = partial(
            self.__handler, send_queue=send_queue, receive_queue=receive_queue
        )
        async with websockets.serve(bound_handler, self.__host, self.__port):
            await asyncio.Future()

    def run_in_process(self, send_queue: mp.Queue, receive_queue: mp.Queue):
        asyncio.run(self.__start_server(send_queue, receive_queue))
