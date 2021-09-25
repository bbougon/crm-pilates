FROM python:3.9.7-slim-buster

ENV LANG C.UTF-8

RUN apt-get update && apt-get install make && apt-get install -y --no-install-recommends ca-certificates sqlite3

#RUN useradd --shell /bin/bash -u 500 -o -c "" -m crm-pilates
#VOLUME /home/crm-pilates
#
#USER crm-pilates
WORKDIR /app
COPY . .

RUN make install-docker

CMD [ "/app/local.virtualenv/bin/gunicorn", "--config", "/app/local.persistent/gunicorn.py" ]
