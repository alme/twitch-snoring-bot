FROM python:3.10

RUN apt update && \
    apt install -y ansible vim && \
    apt clean && rm -rf /var/lib/apt/lists/*
RUN pip install requests lxml irc