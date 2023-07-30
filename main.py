#!/usr/bin/env python3
from uuid import uuid4
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi_socketio import SocketManager

app = FastAPI()
socket_manager = SocketManager(app=app)

counter_dict = {}

@app.get('/')
async def get():
    id = str(uuid4())
    counter_dict[id] = 0
    return HTMLResponse(content=f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 10px;">
                <label id="label">ID: {id}</label>
                <br/>
                <button id="button" style="padding: 10px 20px; margin: 40px 0px; border: none;">Increment</button>
                <br/>
                <label id="counter">Counter: 0</label>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.2/socket.io.min.js"></script>
                <script>
                    const url = window.location.protocol === 'https:' ? 'wss://' : 'ws://' + window.location.host;
                    var socket = io(url, {{ path: "/ws/socket.io" }} );
                    var button = document.getElementById('button');
                    var counter = document.getElementById('counter');
                    button.onclick = function() {{
                        socket.emit('click', '{id}');
                    }};
                    socket.on('count', function(msg) {{
                        counter.innerHTML = "Counter: " + msg.count;
                    }});
                    socket.on('error', function(msg) {{
                        counter.innerHTML = "Error: " + msg.msg;
                    }});
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
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)