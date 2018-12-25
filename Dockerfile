FROM python:3-alpine

COPY requirements.txt /

RUN apk update && \
 apk add --virtual dependencies --no-cache --upgrade \
  gcc libffi-dev musl-dev libxml2-dev libxslt-dev openssl-dev python3-dev && \
 pip3 install -r /requirements.txt && \
 apk del dependencies

COPY . /bot
WORKDIR /bot

CMD python3 db/dbimport.py && python3 bot.py
