# Using Multiple fly.io Instances with socket.io and FastAPI

## Run Locally

```bash
python3 -m pip install -r requirements.txt
./main.py
```

or 

```bash
docker build -t fly-fastapi-socketio .
docker run --rm -it -p 8000:8000 fly-fastapi-socketio
```

## Run on fly.io

```bash
fly scale count 2 # let two machines run in the same region to reproduce the error
fly deploy
fly logs
```

## The Issue

If the wrong server is requested to do the upgrade to websocket the client sticks with http long polling.
This can be reproduced by deploying the app and then reconnecting with the browser multiple times.

On the server we see

```
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]ERROR:    Exception in ASGI application
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]Traceback (most recent call last):
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/websockets/websockets_impl.py", line 247, in run_asgi
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    result = await self.app(self.scope, self.asgi_receive, self.asgi_send)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 84, in __call__
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    return await self.app(scope, receive, send)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/fastapi/applications.py", line 289, in __call__
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await super().__call__(scope, receive, send)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/starlette/applications.py", line 122, in __call__
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await self.middleware_stack(scope, receive, send)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 149, in __call__
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await self.app(scope, receive, send)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/app/main.py", line 36, in __call__
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await response(scope, receive, send)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/starlette/responses.py", line 164, in __call__
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await send(
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/websockets/websockets_impl.py", line 310, in asgi_send
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    raise RuntimeError(msg % message_type)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]RuntimeError: Expected ASGI message 'websocket.accept' or 'websocket.close', but got 'http.response.start'.
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]INFO:     connection open
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]ERROR:    closing handshake failed
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]Traceback (most recent call last):
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 959, in transfer_data
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    message = await self.read_message()
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]              ^^^^^^^^^^^^^^^^^^^^^^^^^
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1029, in read_message
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    frame = await self.read_data_frame(max_size=self.max_size)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1104, in read_data_frame
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    frame = await self.read_frame(max_size)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1161, in read_frame
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    frame = await Frame.read(
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]            ^^^^^^^^^^^^^^^^^
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/framing.py", line 68, in read
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    data = await reader(2)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]           ^^^^^^^^^^^^^^^
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/asyncio/streams.py", line 727, in readexactly
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    raise exceptions.IncompleteReadError(incomplete, n)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]asyncio.exceptions.IncompleteReadError: 0 bytes read on a total of 2 expected bytes
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]The above exception was the direct cause of the following exception:
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]Traceback (most recent call last):
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/server.py", line 248, in handler
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await self.close()
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 766, in close
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await self.write_close_frame(Close(code, reason))
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1232, in write_close_frame
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await self.write_frame(True, OP_CLOSE, data, _state=State.CLOSING)
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1205, in write_frame
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await self.drain()
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1194, in drain
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    await self.ensure_open()
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 935, in ensure_open
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]    raise self.connection_closed_exc()
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]websockets.exceptions.ConnectionClosedError: sent 1000 (OK); no close frame received
2023-07-30T07:13:11Z app[6e82932a759e18] fra [info]INFO:     connection closed
```