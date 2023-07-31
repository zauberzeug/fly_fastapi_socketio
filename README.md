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

## The Problem

If you have an interactive app running on fly.io with multiple instances
you may need to make sure that your websocket is connecting back to exactly the instance where the website was served from due some local state.
This can not be archived with the `fly-force-instance-id` header, because it is not possible to add custom headers to websockets in the browser.

# The Solution

Inspired by https://fly.io/blog/replicache-machines-demo/ we use the `fly-replay` header in the response 
to tell the load balancer to run the request once again to the right instance.
But how do we know the right instance? The blog from fly.io suggests a database in the backend.
To minimize infrastructure and potential bottlenecks the implementation here takes an alternative route: 
The instance simply injects its fly id into the served page so the socket connection can provide it as a query parameter.
A middleware can then decide if the requested instance id matches the one handling the request.
If not a replay must be performed.


