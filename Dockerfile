FROM python:3.9.7-slim-buster AS development

ENV LANG C.UTF-8

RUN apt-get update && apt-get install make && apt-get install -y --no-install-recommends ca-certificates sqlite3

WORKDIR /app
COPY . .

RUN make install-docker-local

CMD [ "/app/local.virtualenv/bin/gunicorn", "--config", "/app/local.persistent/gunicorn.py", "--reload"]

FROM python:3.9.7-slim-buster AS production

ENV LANG C.UTF-8

RUN apt-get update && apt-get install make && apt-get install -y --no-install-recommends ca-certificates sqlite3

WORKDIR /app
COPY . .

RUN make install-docker

CMD [ "/app/local.virtualenv/bin/gunicorn", "--config", "/app/local.persistent/gunicorn.py" ]

