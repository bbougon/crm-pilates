FROM python:3.9.7-slim-buster

ENV LANG C.UTF-8

RUN apt-get update && apt-get install make && apt-get install -y --no-install-recommends ca-certificates sqlite3

RUN useradd --shell /bin/bash -u 500 -o -c "" -m crm-pilates
VOLUME /home/crm-pilates

# Run sensei as user 'user' -> this means the server will run unprivileged
# using id 500, in the /home/user directory
USER crm-pilates
WORKDIR /home/crm-pilates/api
COPY . .

RUN make install-docker

CMD [ "/home/crm-pilates/api/local.virtualenv/bin/gunicorn", "--config", "/home/crm-pilates/api/local.persistent/gunicorn.py" ]
