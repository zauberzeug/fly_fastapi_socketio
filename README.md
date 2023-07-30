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
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/websockets/websockets_impl.py", line 247, in run_asgi
    result = await self.app(self.scope, self.asgi_receive, self.asgi_send)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 84, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/applications.py", line 289, in __call__
    await super().__call__(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/applications.py", line 122, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 149, in __call__
    await self.app(scope, receive, send)
  File "/app/main.py", line 36, in __call__
    await response(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/responses.py", line 164, in __call__
    await send(
  File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/websockets/websockets_impl.py", line 310, in asgi_send
    raise RuntimeError(msg % message_type)
RuntimeError: Expected ASGI message 'websocket.accept' or 'websocket.close', but got 'http.response.start'.
INFO:     connection open
ERROR:    closing handshake failed
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 959, in transfer_data
    message = await self.read_message()
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1029, in read_message
    frame = await self.read_data_frame(max_size=self.max_size)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1104, in read_data_frame
    frame = await self.read_frame(max_size)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1161, in read_frame
    frame = await Frame.read(
            ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/framing.py", line 68, in read
    data = await reader(2)
           ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 727, in readexactly
    raise exceptions.IncompleteReadError(incomplete, n)
asyncio.exceptions.IncompleteReadError: 0 bytes read on a total of 2 expected bytes
The above exception was the direct cause of the following exception:
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/server.py", line 248, in handler
    await self.close()
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 766, in close
    await self.write_close_frame(Close(code, reason))
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1232, in write_close_frame
    await self.write_frame(True, OP_CLOSE, data, _state=State.CLOSING)
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1205, in write_frame
    await self.drain()
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 1194, in drain
    await self.ensure_open()
  File "/usr/local/lib/python3.11/site-packages/websockets/legacy/protocol.py", line 935, in ensure_open
    raise self.connection_closed_exc()
websockets.exceptions.ConnectionClosedError: sent 1000 (OK); no close frame received
INFO:     connection closed
```