# Using Multiple fly.io Instances with socket.io and FastAPI

## Run Locally

```bash
python3 -m pip install -r requirements.txt
./main.py
```

or 

```bash
docker build -t fly-socketio .
docker run --rm -it -p 8000:8000 fly-socketio
```
