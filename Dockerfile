FROM python:3.9.9-slim-buster AS runtime-env

ENV LANG C.UTF-8


RUN pip install --user poetry
RUN apt-get update && apt-get install -y gnupg && apt-get install -y curl && apt-get install -y --no-install-recommends ca-certificates
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg >/dev/null
RUN echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install make && apt-get install -y libpq5 && apt-get install -y libpq-dev && apt-get install -y gcc && apt-get -y install postgresql && apt-get install -y --no-install-recommends sqlite3

ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /crm-pilates
COPY . .

FROM runtime-env AS development

WORKDIR /crm-pilates

ENV VIRTUAL_ENV=/crm-pilates/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN make install-docker-local INSTALL_ARGS="--no-dev"

CMD [ "gunicorn", "--config", "/crm-pilates/crm_pilates/gunicorn.py", "--reload"]

FROM runtime-env AS production

WORKDIR /crm-pilates

ENV VIRTUAL_ENV=/crm-pilates/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN make install-docker INSTALL_ARGS="--no-dev"

CMD [ "gunicorn", "--config", "/crm-pilates/crm_pilates/gunicorn.py"]
