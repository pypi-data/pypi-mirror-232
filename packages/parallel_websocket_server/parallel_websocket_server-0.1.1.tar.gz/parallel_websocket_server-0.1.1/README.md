# parallel_websocket_server

run websocket server in parallel (using multiprocessing)

## Installation

```bash
pip install parallel_websocket_server
```

## How to use

```python

import json
import random
import multiprocessing as mp
from parallel_websocket_server import ParallelWebSocketServer


if __name__ == "__main__":
    receive_queue = mp.Queue()
    send_queue = mp.Queue()

    server = ParallelWebSocketServer(receive_queue, send_queue)

    while True:
        if not receive_queue.empty():
            received_message = receive_queue.get_nowait()
            print(received_message)

        ran = random.random()
        if ran < 0.00001:
            send_queue.put(json.dumps({"hoge": 1}))

```
