#!/usr/bin/env python3
import os
from urllib.parse import parse_qs
from uuid import uuid4
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi_socketio import SocketManager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import Response

from icecream import ic

app = FastAPI()
socket_manager = SocketManager(app=app)

fly_instance_id = os.environ.get('FLY_ALLOC_ID', 'local').split('-')[0]
counter_dict = {}

class FlyReplayMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        target_instance = query_params.get('fly_instance_id', [fly_instance_id])[0]
        async def send_wrapper(message):
            if target_instance != fly_instance_id:
                if message['type'] == 'websocket.close' and 'Invalid session' in message['reason']:
                    message = {'type': 'websocket.accept'} # fly.io only seems to look at the fly-replay header if websocket is accepted
                if 'headers' not in message:
                    message['headers'] = []              
                message['headers'].append([b'fly-replay', f'instance={target_instance}'.encode()])
            await send(message)
        await self.app(scope, receive, send_wrapper)

app.add_middleware(FlyReplayMiddleware)

@app.get('/')
async def get():
    id = str(uuid4())
    counter_dict[id] = 0
    return HTMLResponse(content=f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 10px;">
                <label id="label">Fly-Instance: {fly_instance_id}, Client-ID: {id}</label>
                <br/>
                <button id="button" style="padding: 10px 20px; margin: 40px 0px; border: none;">Increment</button>
                <br/>
                <label id="counter">Counter: 0</label>
                <br/>
                <label id="transport_type">Transport: N/A</label>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.2/socket.io.min.js"></script>
                <script>
                    const url = window.location.protocol === 'https:' ? 'wss://' : 'ws://' + window.location.host;
                    const query = {{ fly_instance_id: "{ fly_instance_id }" }};
                    var socket = io(url, {{ path: "/ws/socket.io", query }} );

                    var button = document.getElementById('button');
                    button.onclick = function() {{ socket.emit('click', '{id}'); }};
                    var counter = document.getElementById('counter');
                    socket.on('count', function(msg) {{ counter.innerHTML = "Counter: " + msg.count; }});
                    socket.on('error', function(msg) {{ counter.innerHTML = "Error: " + msg.msg; }});

                    var transport = document.getElementById('transport_type');
                    setInterval(function() {{
                        transport.innerHTML = "Transport: " + (socket.io.engine ? socket.io.engine.transport.name : 'N/A');
                    }}, 1000);
                </script>
            </body>
        </html>
    """)

@app.sio.on('click')
async def click(sid, data):
    if data in counter_dict:
        counter_dict[data] += 1
        await app.sio.emit('count', {'count': counter_dict[data]})
    else:
        await app.sio.emit('error', {'msg': 'unknown id'})


if __name__ == '__main__':
    import logging
    import sys

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)