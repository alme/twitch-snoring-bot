FROM python:3.11-alpine

RUN pip install --no-cache-dir websockets

COPY src/websocket /python

ENTRYPOINT ["python", "/python/main.py"]