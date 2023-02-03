FROM python:3.11-alpine

RUN pip install --no-cache-dir irc requests lxml

COPY src/irc /python
COPY docker/.irc-build/config.py /python/config.py

ENTRYPOINT ["python", "/python/main.py"]