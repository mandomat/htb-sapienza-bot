FROM alpine:latest

RUN apk update && apk upgrade && \
    apk add --no-cache python3 build-base gcc python3-dev libffi-dev libressl-dev libxml2-dev libxslt-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

COPY requirements.txt /

RUN   pip3 install -r /requirements.txt

COPY	. /bot
WORKDIR	/bot

CMD python3 bot.py
